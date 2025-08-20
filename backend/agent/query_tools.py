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
        Filters through user preferences which are the features selected by the user while configuring the fleet and user filters which are the filters selected by the user on the right of the UI.
        
        Returns a list of vehicle states based on the user preferences and agent filters.
        """
        collection = self.get_collection(self.mdb_timeseries_collection)
        
        logger.info(f"[MongoDB] Starting vehicle state search")
        

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

        logger.info(f"User preferences: {user_preferences}")
        match_stage = self.build_match_stage(user_filters, agent_filters, user_preferences)
        logger.info(f"Match stage for vehicle state search: {match_stage}")
        if match_stage["$or"] != []:
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


            if group:
                pipeline = [
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
       
        logger.info(f"Aggregation pipeline: {pipeline}")



        cursor = collection.aggregate(pipeline)
        result = list(cursor)

        #If user asked for timestamp based averages, we process them here
        for fleet_prefs in user_filters: 
            logger.info(f"Processing user filter: {fleet_prefs}")
            if fleet_prefs == "Last 30 min" or fleet_prefs == "Last hour" or fleet_prefs == "Last 2 hours":
                average = await self.calculate_field_averages_by_timeframe(timeframe=fleet_prefs, user_preferences=user_preferences, user_filters=user_filters, match_stage=match_stage)
                result.append(average)
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

                if fleet_idx is not None:
                    allowed_fields = set(mapped_user_preferences[fleet_idx])
                    allowed_fields.add("car_id")
                    allowed_fields.add("timestamp")
                    # Set to None any field not in allowed_fields
                    for field in list(car.keys()):
                        if field not in allowed_fields:
                            car[field] = None
        return result

    async def calculate_field_averages_by_timeframe(self, timeframe: str, user_preferences: str = None, user_filters: str = None, match_stage: dict = None):
        """
        Calculate the average of all numeric fields in the timeseries collection within a given timeframe.
        
        Args:
            timeframe (str): Time range - "last 30 min", "last hour", "last 2 hours"
            user_preferences (str, optional): User preferences for filtering data
            user_filters (str, optional): User filters for additional filtering
            
        Returns:
            dict: Dictionary containing averages for all numeric fields
        """
        collection = self.get_collection(self.mdb_timeseries_collection)
        logger.info(f"[MongoDB] Calculating field averages for timeframe: {timeframe}")
        
        # Calculate the start time based on timeframe
        now = datetime.datetime.utcnow()
        


        if timeframe == "Last 30 min":
            start_time = now - datetime.timedelta(minutes=30)
        elif timeframe == "Last hour":
            start_time = now - datetime.timedelta(hours=1)
        elif timeframe == "Last 2 hours":
            start_time = now - datetime.timedelta(hours=2)
        else:
            # Default to last hour if timeframe is not recognized
            start_time = now - datetime.timedelta(hours=1)
            logger.warning(f"Unrecognized timeframe '{timeframe}', defaulting to last hour")
        
        logger.info(f"Calculating averages from {start_time} to {now}")
        
        # Build base match stage with time filter
        match_stage2 = {
            "timestamp": {
                "$gte": start_time,
                "$lte": now
            }
        }
        
        # Define all numeric fields that we want to calculate averages for
        numeric_fields = [
            "performance_score",
            "run_time", 
            "availability_score",
            "quality_score",
            "oee",
            "fuel_efficiency",
            "engine_oil_level",
            "oil_temperature",
            "fuel_level",
            "max_fuel_level",
            "traveled_distance",
            "average_speed",
            "speed"
        ]
        
        # Build the group stage to calculate averages
        group_stage = {
            "_id": None,
            "total_records": {"$sum": 1}
        }
        
        # Add average calculation for each numeric field
        for field in numeric_fields:
            group_stage[f"avg_{field}"] = {"$avg": f"${field}"}
        
        logger.info(f"Match stage before user filters: {match_stage}")
        logger.info(f"Match stage2 after user filters: {match_stage2}")

        # Build the aggregation pipeline
        if match_stage["$or"]:
            pipeline = [
                {"$match": match_stage2},
                {"$match": match_stage},
                {"$group": group_stage},
                {
                    "$project": {
                        "_id": 0,
                        "timeframe": {"$literal": timeframe},
                        "total_records": 1,
                        "start_time": {"$literal": start_time.isoformat()},
                        "end_time": {"$literal": now.isoformat()},
                        # Project all average fields
                        **{f"avg_{field}": {"$round": [f"$avg_{field}", 2]} for field in numeric_fields}
                    }
                }
            ]
        else:
            pipeline = [
                {"$match": match_stage2},
                
                # {"$group": group_stage},
                # {
                #     "$project": {
                #         "_id": 0,
                #         "timeframe": {"$literal": timeframe},
                #         "total_records": 1,
                #         "start_time": {"$literal": start_time.isoformat()},
                #         "end_time": {"$literal": now.isoformat()},
                #         # Project all average fields
                #         **{f"avg_{field}": {"$round": [f"$avg_{field}", 2]} for field in numeric_fields}
                #     }
                # }
            ]
        
        # logger.info(f"Aggregation pipeline: {pipeline}")
        
        try:
            cursor = collection.aggregate(pipeline)
            result = list(cursor)

            logger.info(f"Avarage Aggregation result sample: {result[0:3]}")
            
            if result:
                averages = result[0]
                logger.info(f"Successfully calculated averages for a bunch of records")
                return averages
            else:
                logger.warning("No data found for the specified timeframe and filters")
                return {
                    "timeframe": timeframe,
                    "total_records": 0,
                    "start_time": start_time.isoformat(),
                    "end_time": now.isoformat(),
                    "message": "No data found for the specified criteria"
                }
                
        except Exception as e:
            logger.error(f"Error calculating field averages: {e}")
            raise e

    async def average_time_series_value(self, field: str, start_date: str, end_date: str):
        """
        Calculate the average value of a specific field in the time series data within a given date range.
        
        Args:
            field (str): The field to calculate the average for
            start_date (str): The start date of the range (ISO format)
            end_date (str): The end date of the range (ISO format)
            
        Returns:
            dict: Dictionary containing the average value and other metadata
        """
        collection = self.get_collection(self.mdb_timeseries_collection)
        
        # Build match stage
        match_stage = {
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        # Build group stage
        group_stage = {
            "_id": None,
            "count": {"$sum": 1},
            "sum": {"$sum": f"${field}"}
        }
        
        # Build project stage
        project_stage = {
            "_id": 0,
            "field": f"${field}",
            "average": {"$divide": ["$sum", "$count"]},
            "count": 1
        }
        
        pipeline = [
            {"$match": match_stage},
            {"$group": group_stage},
            {"$project": project_stage}
        ]
        
        logger.info(f"Executing pipeline: {pipeline}")
        
        cursor = collection.aggregate(pipeline)
        result = list(cursor)
        
        if result:
            average_result = result[0]
            logger.info(f"Calculated average for field '{field}': {average_result.get('average')}")
            return {
                "field": field,
                "average": round(average_result.get("average", 0), 2),
                "count": average_result.get("count"),
                "timeframe": f"{start_date} to {end_date}"
            }
        else:
            logger.warning(f"No data found for field '{field}' between {start_date} and {end_date}")
            return {
                "field": field,
                "average": 0,
                "count": 0,
                "timeframe": f"{start_date} to {end_date}"
            }

    def build_match_stage(self, user_filters: str = None, agent_filters: str = None, user_preferences: str = None):
        """
        Build the match stage for the MongoDB query based on user preferences and agent filters.
        This returns a dictionary representing the $match stage.
        """
        match_stage = {}
        fleet_capacity = self.understand_fleet_number(user_preferences)
        logger.info(f"Fleet capacity: {fleet_capacity}")
        logger.info(f"User filters: {user_filters}")

        match_stage["$or"] = []
        # Handle empty user_filters
        if user_filters and len(user_filters) > 0:
            for fleet_prefs in user_filters:
                
                car_ids1 = None
                car_ids2 = None
                car_ids3 = None

                logger.info(f"Processing user filter: {fleet_prefs}")
                
                if fleet_prefs == "Last 30 min" or fleet_prefs == "Last hour" or fleet_prefs == "Last 2 hours":
                    # logger.info(f"Skipping preference")
                    continue
                if fleet_prefs:
                    if fleet_prefs == "Fleet 1":
                        car_ids1 = list(range(0, fleet_capacity[0]))  # Car IDs 0-99
                        match_stage["$or"].append({"car_id": {"$in": car_ids1}})
                    if fleet_prefs == "Fleet 2":
                        car_ids2 = list(range(100, fleet_capacity[1]))  # Car IDs 100-199
                        match_stage["$or"].append({"car_id": {"$in": car_ids2}})
                    if fleet_prefs == "Fleet 3":
                        car_ids3 = list(range(200, fleet_capacity[2]))  # Car IDs 200-299
                        match_stage["$or"].append({"car_id": {"$in": car_ids3}})
                    elif fleet_prefs in ["downtown","utxa", "north_austin","capitol_area","south_austin","airport_zone","south_east_austin","south_west_austin","barton_creek","georgetown"]:
                        # For geofence filters, use current_geozone field instead
                        match_stage["$or"].append({"current_geozone": fleet_prefs})
                        # logger.info(f"Match stage: {match_stage}")
                        
                    else:
                        # For other string values, treat as direct car_id match
                        match_stage["$or"].append({"car_id": fleet_prefs})
                        continue
        
        else:
            logger.info("No user filters provided. Returning all data.")

        if match_stage["$or"] == []:
            match_stage["$or"].append({"car_id": {"$in": list(range(0, fleet_capacity[0]))}})
            match_stage["$or"].append({"car_id": {"$in": list(range(0, fleet_capacity[1]))}})
            match_stage["$or"].append({"car_id": {"$in": list(range(0, fleet_capacity[2]))}})
            
        # Handle agent_filters
        if agent_filters:
            if isinstance(agent_filters, str):
                agent_filters = json.loads(agent_filters)

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
        logger.info(f"[MongoDB] Starting vehicle maintenance data search")

        fleet_capacity = self.understand_fleet_number(user_preferences)
        logger.info(f"Fleet capacity from user preferences: {fleet_capacity}")

        match_stage = {}
        match_stage["$or"] = []

        # Fix the car ID ranges to match the logic in build_match_stage
        if user_preferences:
            if len(fleet_capacity) > 0 and fleet_capacity[0] > 0:
                car_ids1 = list(range(0, fleet_capacity[0]))  # 0 to fleet_capacity[0]-1
                match_stage["$or"].append({"car_id": {"$in": car_ids1}})
                logger.info(f"Fleet 1 car IDs: {car_ids1[:5]}...{car_ids1[-5:] if len(car_ids1) > 5 else car_ids1}")
                
            if len(fleet_capacity) > 1 and fleet_capacity[1] > 0:
                car_ids2 = list(range(100, 100 + fleet_capacity[1]))  # 100 to 100+fleet_capacity[1]-1
                match_stage["$or"].append({"car_id": {"$in": car_ids2}})
                logger.info(f"Fleet 2 car IDs: {car_ids2[:5]}...{car_ids2[-5:] if len(car_ids2) > 5 else car_ids2}")
                
            if len(fleet_capacity) > 2 and fleet_capacity[2] > 0:
                car_ids3 = list(range(200, 200 + fleet_capacity[2]))  # 200 to 200+fleet_capacity[2]-1
                match_stage["$or"].append({"car_id": {"$in": car_ids3}})
                logger.info(f"Fleet 3 car IDs: {car_ids3[:5]}...{car_ids3[-5:] if len(car_ids3) > 5 else car_ids3}")

        logger.info(f"Match stage for maintenance data: {match_stage}")

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
        
        cursor = collection.aggregate(pipeline)
        result = list(cursor)
        logger.info(f"Maintenance data results count: {len(result)}")
        
        # We need to obtain at least the latest vehicle state data to make a good recommendation
        logger.info("Calling vehicle_state_search for additional data...")
        result2 = await self.vehicle_state_search(
            user_preferences=user_preferences, 
            agent_filters=agent_filters, 
            user_filters=user_filters, 
            group=True
        )
        logger.info(f"Vehicle state search results count: {len(result2)}")

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
        logger.info(f"Combined results count: {len(combined)}")

        return combined
    

    def understand_fleet_number(self, user_preferences: str):
        """       
        Understand the fleet number from user preferences.

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
    checkpoint = query_tools.obtain_checkpoint()
    state["checkpoint"] = checkpoint
    state["recommendation_data"] = result
    state["next_step"] = "recommendation_node"
    logger.info(f"Next step: {state['next_step']}")
    return AgentState(**state)

async def vehicle_state_search_tool(state: dict) -> AgentState:
    await manager.send_to_thread("Performing vehicle state search", state.get("thread_id", None))
    logger.info("QueryTools initialized for vehicle state search.")

    userPreferences = state.get("userPreferences")
    userFilters = state.get("userFilters")
    agentPreferences = state.get("botPreferences")

    logger.info(f"User Preferences: {userPreferences}")
    logger.info(f"User Filters: {userFilters}")
    logger.info(f"Agent Preferences: {agentPreferences}")

    query_tools = QueryTools()
    result = await query_tools.vehicle_state_search(user_preferences=userPreferences, agent_filters=agentPreferences, user_filters=userFilters)

    checkpoint = query_tools.obtain_checkpoint()
    state["checkpoint"] = checkpoint
    state["recommendation_data"] = result
    state["next_step"] = "recommendation_node"
    logger.info(f"Next step: {state['next_step']}")
    logger.info(f"Result count: {len(result)}")
    return AgentState(**state)

async def get_vehicle_maintenance_data_tool(state: dict) -> AgentState:
    await manager.send_to_thread("Obtaining vehicle maintenance data", state.get("thread_id", None))
    logger.info("QueryTools initialized for vehicle maintenance data.")
    query_tools = QueryTools()
    userPreferences = state.get("userPreferences")
    agentPreferences = state.get("botPreferences")
    userFilters = state.get("userFilters")
    result = await query_tools.obtain_maintenance_data(user_preferences=userPreferences, agent_filters=agentPreferences, user_filters=userFilters)
    checkpoint = query_tools.obtain_checkpoint()
    state["checkpoint"] = checkpoint
    state["recommendation_data"] = result
    state["next_step"] = "recommendation_node"
    logger.info(f"Next step: {state['next_step']}")
    return AgentState(**state)