
from db.mdb import MongoDBConnector

import datetime
import logging

from config.config_loader import ConfigLoader
from config.prompts import get_chain_of_thoughts_prompt, get_llm_recommendation_prompt
from utils import convert_objectids

from loader import CSVLoader
import csv
from dateutil.parser import parse

from websocketServer import manager

from agent_state import AgentState
from embedder import Embedder
from agent_profiles import AgentProfiles
from mdb_timeseries_coll_creator import TimeSeriesCollectionCreator
from mdb_vector_search_idx_creator import VectorSearchIDXCreator

from dotenv import load_dotenv

import json




# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class QueryTools(MongoDBConnector):
    """
    QueryTools class to handle various query operations for the agent.
    It includes methods for loading CSV data, generating embeddings, and managing agent states.
    """

    def __init__(self, collection_name = None,  uri: str = None, database_name: str = None, appname: str = None):
        super().__init__(uri, database_name, appname)

        # Load configuration
        config = ConfigLoader()
        self.config = config

                # Get configuration values
        self.mdb_timeseries_collection = self.config.get("MDB_TIMESERIES_COLLECTION")
        self.mdb_static_information_collection = self.config.get("MDB_STATIC_INFORMATION_COLLECTION")
        self.mdb_timeseries_timefield = self.config.get("MDB_TIMESERIES_TIMEFIELD")
        self.mdb_timeseries_granularity = self.config.get("MDB_TIMESERIES_GRANULARITY")
        self.default_timeseries_data = self.config.get("DEFAULT_TIMESERIES_DATA")
        self.critical_conditions_config = self.config.get("CRITICAL_CONDITIONS")
        self.mdb_embeddings_collection = self.config.get("MDB_EMBEDDINGS_COLLECTION") # historical_recommendations
        self.mdb_embeddings_collection_vs_field = self.config.get("MDB_EMBEDDINGS_COLLECTION_VS_FIELD")
        self.mdb_vs_index = self.config.get("MDB_VS_INDEX")
        self.mdb_agent_profiles_collection = self.config.get("MDB_AGENT_PROFILES_COLLECTION")
        self.agent_profile_chosen_id = self.config.get("AGENT_PROFILE_CHOSEN_ID")
        self.embeddings_model_id = self.config.get("EMBEDDINGS_MODEL_ID")
        self.embeddings_model_name = self.config.get("EMBEDDINGS_MODEL_NAME")
        self.chatcompletions_model_id = self.config.get("CHATCOMPLETIONS_MODEL_ID")
        self.chatcompletions_model_name = self.config.get("CHATCOMPLETIONS_MODEL_NAME")
        self.mdb_historical_recommendations_collection = self.config.get("MDB_HISTORICAL_RECOMMENDATIONS_COLLECTION") # historical_recommendations
        self.mdb_checkpointer_collection = self.config.get("MDB_CHECKPOINTER_COLLECTION")

        if collection_name:
            # Set the collection name
            self.collection_name = collection_name
            self.collection = self.get_collection(self.collection_name)
    

    async def fleet_position_search(self, user_preferences: str = None, agent_filters: str = None):
        """
        Perform a fleet search based on the provided user preferences.

        User preferences could be the filters
        agent filters are things that the LLM identifies that should be used for the filter

        Mainly a timeseries collection search
        """
        collection = self.get_collection(self.mdb_timeseries_collection)
        
        pipeline = [
        {
            "$group": {
                "_id": "$car_id",
                "car_id": {"$first": "$car_id"},
                "current_geozone": {"$first": "$current_geozone"},
                "timestamp": {"$first": "$timestamp"}
            }
        },
        
        {
            "$project": {
                "_id": 0,
                "car_id": 1,
                "current_geozone": 1,
                "timestamp": 1
            }
        },
        
        {
            "$sort": {
                "car_id": 1
            }
        }
    ]

        cursor = collection.aggregate(pipeline)
        result = list(cursor)
        logger.info(f"Sample: {result[:3]}")
        
        return result

    async def vehicle_state_search(self, user_preferences: str = None, agent_filters: str = None, user_filters: str = None, limit: int = 500, group: bool = False):
        """
        Perform a vehicle state search based on the provided user preferences.
        """
        collection = self.get_collection(self.mdb_timeseries_collection)
        
        logger.info(f"User preferences: {user_preferences}")
        logger.info(f"Agent filters: {agent_filters}")

        # Field mapping - only include fields that exist in your collection
        FIELD_MAPPING = {  
        "Performance": "performance_score",  
        "Run Time": "run_time",  
        "Avaliability": "availability_score",  
        "Quality": "quality_score",  
        "OEE": "oee",  
        "Gas efficiency": "fuel_efficiency",  
        "Oil level": "engine_oil_level",  
        "Last maintance": "last_maintenance_date",  
        "Temperature": "oil_temperature",  
        "Ambient temperature": "ambient_temperature",  
        "Gas level": "fuel_level",  
        "Distance driven": "traveled_distance",  
        "Geozone": "current_geozone",  
        "Coordinates": "coordinates",  
    }  

        mapped_user_preferences = {
            "0": [],
            "1": [],
            "2": []
        }

        # Process user preferences
        for i, fleet_prefs in enumerate(user_preferences):
            if fleet_prefs:
                mapped_user_preferences[str(i)] = [
                    FIELD_MAPPING[field] for field in fleet_prefs if field in FIELD_MAPPING
                ]

        logger.info(f"Mapped user preferences: {mapped_user_preferences}")

        # Collect unique mapped fields
        mapped_fields = set()
        for fleet_prefs in user_preferences:
            if fleet_prefs:
                for field in fleet_prefs:
                    if field in FIELD_MAPPING:  # Only process fields that exist in mapping
                        db_field = FIELD_MAPPING[field]
                        if db_field is not None:  # Extra safety check
                            mapped_fields.add(db_field)

        logger.info(f"Mapped fields: {mapped_fields}")

        # Build project stage
        project_stage = {
            "_id": 0,
            "car_id": 1,
            "timestamp": 1,
        }   

        # Add the mapped fields
        for field in mapped_fields:
            if field is not None:  # Double check for None
                project_stage[field] = 1

        logger.info(f"Final project stage: {project_stage}")

        match_stage = self.build_match_stage(user_filters, agent_filters, user_preferences)

        logger.info(f"group: {group}")

        if group:
            pipeline = [
            {
                "$match": match_stage
            },
            {
                "$group": {
                    "_id": "$car_id",
                    "car_id": {"$first": "$car_id"},
                    "timestamp": {"$first": "$timestamp"},
                    "availability_score": {"$first": "$availability_score"},
                    "current_route": {"$first": "$current_route"},
                    "run_time": {"$first": "$run_time"},
                    "performance_score": {"$first": "$performance_score"},
                    "oil_temperature": {"$first": "$oil_temperature"},
                    "current_geozone": {"$first": "$current_geozone"},
                    "engine_oil_level": {"$first": "$engine_oil_level"},
                    "is_crashed": {"$first": "$is_crashed"},
                    "metadata": {"$first": "$metadata"},
                    "average_speed": {"$first": "$average_speed"},
                    "quality_score": {"$first": "$quality_score"},
                    "is_moving": {"$first": "$is_moving"},
                    "coordinates": {"$first": "$coordinates"},
                    "oee": {"$first": "$oee"},
                    "fuel_level": {"$first": "$fuel_level"},
                    "max_fuel_level": {"$first": "$max_fuel_level"},
                    "speed": {"$first": "$speed"},
                    "is_engine_running": {"$first": "$is_engine_running"},
                    "is_oil_leak": {"$first": "$is_oil_leak"},
                    "traveled_distance": {"$first": "$traveled_distance"}
                }
            },
            {
                "$sort": {"timestamp": -1}
            },
            {
                "$project": project_stage
            },
            # Final sort
            {
                "$sort": {
                    "car_id": 1
                }
            }
        ]

        else:
            pipeline = [
                {
                    "$match": match_stage
                },
                {
                    "$sort": {"timestamp": -1}
                },
                {
                    "$limit": limit  # Limit to 500 results
                },
                {
                    "$project": project_stage
                },
                # Final sort
                {
                    "$sort": {
                        "car_id": 1
                    }
                }
            ]

        logger.info(f"Pipeline for vehicle state search: {pipeline}")
        cursor = collection.aggregate(pipeline)
        result = list(cursor)
        logger.info(f"Sample: {result[:3]}")

         # We clean the outputs and only process whats in the user preferences
        for car in result:
            car_id = car.get("car_id")
            # Determine fleet index based on car_id
            if car_id is not None:
                if 0 <= car_id <= 99:
                    fleet_idx = "0"
                elif 100 <= car_id <= 199:
                    fleet_idx = "1"
                elif 200 <= car_id <= 299:
                    fleet_idx = "2"
                else:
                    fleet_idx = None

                # logger.info(mapped_user_preferences)
                if fleet_idx is not None:
                    allowed_fields = set(mapped_user_preferences[fleet_idx])
                    allowed_fields.add("car_id")
                    allowed_fields.add("timestamp")
                    # Set to None any field not in allowed_fields
                    for field in list(car.keys()):
                        # logger.info(f"Checking field: {field} in allowed fields: {allowed_fields}")
                        if field not in allowed_fields:
                            car[field] = None
        
        return result


    def build_match_stage(self, user_filters: str = None, agent_filters: str = None, user_preferences: str = None):
        """
        Build the match stage for the MongoDB query based on user preferences and agent filters.
        
        User Filters are to be used in the match stage
        User Preferences are to be used in the project stage
        
        
        """
        match_stage = {}
        fleet_capacity = self.understand_fleet_number(user_preferences)
        logger.info(f"Fleet capacity: {fleet_capacity}")
        if user_filters:
            match_stage["$or"] = []
            for fleet_prefs in user_filters:
                if fleet_prefs == "Last 30 min" or fleet_prefs == "Last hour" or fleet_prefs == "Last 2 hours" :
                    logger.info(f"Skipping preference")
                    continue
                if fleet_prefs:
                    if fleet_prefs == "Fleet 1":
                        car_ids1 = list(range(0, fleet_capacity[0]))  # Car IDs 0-99
                    elif fleet_prefs == "Fleet 2":
                        car_ids2 = list(range(100, fleet_capacity[1]))  # Car IDs 100-199
                    elif fleet_prefs == "Fleet 3":
                        car_ids3 = list(range(200, fleet_capacity[2]))  # Car IDs 200-299
                    elif fleet_prefs in ["Downtown", "Geofence 2"]:
                        # For geofence filters, use current_geozone field instead
                        match_stage["$or"].append({"current_geozone": fleet_prefs})
                        logger.info(f"Match stage: {match_stage}")
                        continue
                    else:
                        # For other string values, treat as direct car_id match
                        match_stage["$or"].append({"car_id": fleet_prefs})
                        continue
                    
                    # Add car ID range filter
                    match_stage["$or"].append({"car_id": {"$in": car_ids1}, "car_id": {"$in": car_ids2}, "car_id": {"$in": car_ids3}})
                    # logger.info(f"Match stage: {match_stage}")


        if agent_filters:
            # agent_filters is already a dict, no need to parse JSON
            if isinstance(agent_filters, str):
                agent_filters = json.loads(agent_filters)
            
            # Access the nested time_range
            time_range = agent_filters.get("time_range", {})
            if time_range:
                try:
                    start_date = time_range.get("start_date")
                    end_date = time_range.get("end_date")

                    # Parse and convert to ISO format
                    if start_date:
                        start_date = parse(start_date).isoformat()
                    if end_date:
                        end_date = parse(end_date).isoformat()

                    match_stage["timestamp"] = {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                except Exception as e:
                    logger.error(f"Error parsing time_range: {e}")
                    match_stage["current_geozone"] = {"$exists": True}
                    match_stage["coordinates"] = {"$exists": True}
                    logger.info(f"Match stage: {match_stage}")

        return match_stage
    
    async def obtain_maintenance_data(self, user_preferences: str = None, agent_filters: str = None, user_filters: str = None):
        """
        Obtain maintenance data for a specific car range based on user preferences and agent filters.
        """

        collection = self.get_collection(self.mdb_static_information_collection)
        logger.info(f"User preferences: {user_preferences}")
        logger.info(f"Agent filters: {agent_filters}")
        logger.info(f"User filters: {user_filters}")


        fleet_capacity = self.understand_fleet_number(user_preferences)
        logger.info(f"Fleet capacity: {fleet_capacity}")

        match_stage = {}
        match_stage["$or"] = []

        # Example: fleet_capacity like [50,150,250] meaning upper bounds (inclusive?) for fleets 1,2,3
        # Decide inclusive vs exclusive. Here assume inclusive, so add +1 to stop.
        if user_preferences:
           
            if fleet_capacity[0] > 0:
                car_ids1 = list(range(0, fleet_capacity[0])) 
            if fleet_capacity[1] > 0:
                car_ids2 = list(range(100, fleet_capacity[1]+100))
            if fleet_capacity[2] > 0:
                car_ids3 = list(range(200, fleet_capacity[2]+200))
            
            if car_ids1:
                match_stage["$or"].append({"car_id": {"$in": car_ids1}})
            if car_ids2:
                match_stage["$or"].append({"car_id": {"$in": car_ids2}})
            if car_ids3:
                match_stage["$or"].append({"car_id": {"$in": car_ids3}})

        pipeline = [
            {"$match": match_stage},
            {
                "$project": {
                    "_id": 0,
                    "car_id": 1,
                    "maintenance_log": 1
                }
            }
        ]
    


        logger.info(f"Pipeline for maintenance data: {pipeline}")

        cursor = collection.aggregate(pipeline)
        result = list(cursor)

        logger.info(f"Maintenance data result count: {len(result)}")

        logger.info(f"Sample maintenance data: {result[:3]}")

        result2 = await self.vehicle_state_search(user_preferences=user_preferences, agent_filters=agent_filters, user_filters=user_filters, group=True)


        # Combine maintenance and state info
        combined = []
        combined.append(result)
        combined.append(result2)

        # Create a dictionary to merge results by car_id
        combined_dict = {car["car_id"]: car for car in result}

        for car in result2:
            car_id = car.get("car_id")
            if car_id in combined_dict:
                # Merge fields from result2 into the existing car in combined_dict
                combined_dict[car_id].update(car)
            else:
                # Add the car from result2 if it doesn't exist in result
                combined_dict[car_id] = car

        # Convert the merged dictionary back to a list
        combined = list(combined_dict.values())

        logger.info(f"sample combined data: {combined[:3]}")

        return combined
    def understand_fleet_number(self, user_preferences: str):
        """        Understand the fleet number from user preferences.

        Args:
            user_preferences (str): User preferences string.

        Returns:
            [int]: an array of the last car IDs in the fleet
            for example [50,150,250] for fleets 1,2,3 so we know we should search for car IDs 0-50, 100-150, 200-250
        """
        fleet_numbers = []
        for preference in user_preferences:
            if isinstance(preference[-1], int):
                fleet_numbers.append(preference[-1])
        return fleet_numbers

    def obtain_checkpoint(self):

        checkpoint_collection = self.get_collection(self.mdb_checkpointer_collection)

        checkpoint = checkpoint_collection.find_one({}, {"_id": 0})
        checkpoint = json.loads(json.dumps(checkpoint, default=str))  # Convert ObjectId to string for JSON serialization
        if checkpoint:
            # Convert ObjectId to string for JSON serialization
            checkpoint = convert_objectids(checkpoint)
        else:
            logger.warning("No checkpoint found in the collection.")
            checkpoint = {}
        return checkpoint


async def fleet_position_search_tool(state: dict) -> AgentState:
    await manager.send_to_thread("Performing fleet location search", state.get("thread_id", None))

    query_tools = QueryTools()
    logger.info("QueryTools initialized for fleet location search.")
    result = await query_tools.fleet_position_search()
    logger.info(f"Fleet location search result count: {len(result)}")
    checkpoint = query_tools.obtain_checkpoint()
    state["checkpoint"] = checkpoint
    state["recommendation_data"] = result
    state["next_step"] = "recommendation_node"
    return AgentState(**state)

async def vehicle_state_search_tool(state: dict) -> AgentState:
    await manager.send_to_thread("Performing vehicle state search", state.get("thread_id", None))
    logger.info("QueryTools initialized for vehicle state search.")

    userPreferences = state.get("userPreferences")
    userFilters = state.get("userFilters")
    agentPreferences = state.get("botPreferences")

    query_tools = QueryTools()
    result = await query_tools.vehicle_state_search(user_preferences=userPreferences, agent_filters=agentPreferences, user_filters=userFilters)

    checkpoint = query_tools.obtain_checkpoint()
    state["checkpoint"] = checkpoint
    state["recommendation_data"] = result
    state["next_step"] = "recommendation_node"
    return AgentState(**state)

async def get_vehicle_maintenance_data_tool(state: dict) -> AgentState:
    await manager.send_to_thread("Obtaining vehicle maintenance data", state.get("thread_id", None))
    logger.info("QueryTools initialized for vehicle maintenance data.")
    query_tools = QueryTools()
    userPreferences = state.get("userPreferences")
    agentPreferences = state.get("botPreferences")
    userFilters = state.get("userFilters")
    logger.info(f"loaded preferences")
    result = await query_tools.obtain_maintenance_data(user_preferences=userPreferences, agent_filters=agentPreferences, user_filters=userFilters)
    logger.info(f"Vehicle maintenance data result: {result}")
    checkpoint = query_tools.obtain_checkpoint()
    state["checkpoint"] = checkpoint
    state["recommendation_data"] = result
    state["next_step"] = "recommendation_node"
    return AgentState(**state)