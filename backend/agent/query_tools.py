
from db.mdb import MongoDBConnector

import datetime
import logging

from config.config_loader import ConfigLoader
from config.prompts import get_chain_of_thoughts_prompt, get_llm_recommendation_prompt
from utils import convert_objectids
from bedrock.anthropic_chat_completions import BedrockAnthropicChatCompletions

from loader import CSVLoader
import csv

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
        self.mdb_timeseries_timefield = self.config.get("MDB_TIMESERIES_TIMEFIELD")
        self.mdb_timeseries_granularity = self.config.get("MDB_TIMESERIES_GRANULARITY")
        self.default_timeseries_data = self.config.get("DEFAULT_TIMESERIES_DATA")
        self.critical_conditions_config = self.config.get("CRITICAL_CONDITIONS")
        self.mdb_embeddings_collection = self.config.get("MDB_EMBEDDINGS_COLLECTION") # historical_recommendations
        self.mdb_embeddings_collection_vs_field = self.config.get("MDB_EMBEDDINGS_COLLECTION_VS_FIELD")
        self.mdb_vs_index = self.config.get("MDB_VS_INDEX")
        self.default_similar_queries = self.config.get("DEFAULT_SIMILAR_QUERIES")
        self.mdb_agent_profiles_collection = self.config.get("MDB_AGENT_PROFILES_COLLECTION")
        self.agent_profile_chosen_id = self.config.get("AGENT_PROFILE_CHOSEN_ID")
        self.embeddings_model_id = self.config.get("EMBEDDINGS_MODEL_ID")
        self.embeddings_model_name = self.config.get("EMBEDDINGS_MODEL_NAME")
        self.chatcompletions_model_id = self.config.get("CHATCOMPLETIONS_MODEL_ID")
        self.chatcompletions_model_name = self.config.get("CHATCOMPLETIONS_MODEL_NAME")
        self.mdb_historical_recommendations_collection = self.config.get("MDB_HISTORICAL_RECOMMENDATIONS_COLLECTION") # historical_recommendations

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

    async def vehicle_state_search(self, user_preferences: str = None, agent_filters: str = None):
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
            "Distance driven": "traveled_distance"        
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
            "coordinates": 1
        }

        # Add the mapped fields
        for field in mapped_fields:
            if field is not None:  # Double check for None
                project_stage[field] = 1

        logger.info(f"Final project stage: {project_stage}")

        pipeline = [
            # Sort first to get latest documents
            {
                "$sort": {
                    "car_id": 1,
                    "timestamp": -1 
                }
            },
            # Group to get latest per car
            {
                "$group": {
                    "_id": "$car_id",
                    "car_id": {"$first": "$car_id"},
                    "fuel_level": {"$first": "$fuel_level"},
                    "oil_temperature": {"$first": "$oil_temperature"},
                    "quality_score": {"$first": "$quality_score"},
                    "performance_score": {"$first": "$performance_score"},
                    "availability_score": {"$first": "$availability_score"},
                    "engine_oil_level": {"$first": "$engine_oil_level"},
                    "coordinates": {"$first": "$coordinates"},
                    "current_route": {"$first": "$current_route"},
                    "speed": {"$first": "$speed"},
                    "average_speed": {"$first": "$average_speed"},
                    "traveled_distance": {"$first": "$traveled_distance"},
                    "is_engine_running": {"$first": "$is_engine_running"},
                    "is_moving": {"$first": "$is_moving"},
                    "is_crashed": {"$first": "$is_crashed"},
                    "is_oil_leak": {"$first": "$is_oil_leak"},
                    "max_fuel_level": {"$first": "$max_fuel_level"},
                    "run_time": {"$first": "$run_time"},
                    "current_geozone": {"$first": "$current_geozone"},
                    "vin": {"$first": "$vin"},
                    "timestamp": {"$first": "$timestamp"}
                }
            },
            # Project only requested fields
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
                    allowed_fields = set(mapped_user_preferences[fleet_idx]) | {"car_id", "timestamp"}
                    # Set to None any field not in allowed_fields
                    for field in list(car.keys()):
                        if field not in allowed_fields:
                            car[field] = None

        # logger.info(f"Sample: {result[:3]}")


        return result


async def fleet_position_search_tool(state: dict) -> AgentState:
    await manager.send_to_thread("Performing fleet location search", state.get("thread_id", None))

    query_tools = QueryTools()
    logger.info("QueryTools initialized for fleet location search.")
    result = await query_tools.fleet_position_search()
    logger.info(f"Fleet location search result count: {len(result)}")

    state["recommendation_data"] = result
    state["next_step"] = "recommendation_node"
    return AgentState(**state)

async def vehicle_state_search_tool(state: dict) -> AgentState:
    await manager.send_to_thread("Performing vehicle state search", state.get("thread_id", None))
    logger.info("QueryTools initialized for vehicle state search.")

    userPreferences = state.get("userPreferences")
    agentFilters = state.get("userFilters")

    query_tools = QueryTools()
    result = await query_tools.vehicle_state_search(user_preferences=userPreferences, agent_filters=agentFilters)
    logger.info(f"Vehicle state search result count: {len(result)}")

    state["recommendation_data"] = result
    state["next_step"] = "recommendation_node"
    return AgentState(**state)