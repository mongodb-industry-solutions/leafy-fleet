
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
        # Get the actual collection object, not the string name
        collection = self.get_collection(self.mdb_timeseries_collection)
        
        # Execute the query on the collection
        cursor = collection.find({}, {"_id": 0, "current_geozone": 1, "car_id": 1}).limit(350)
        
        # Convert cursor to list
        result = list(cursor)
        
        # If you want unique results, you can use a set, but you need to convert dicts to tuples first
        # Or just return the list directly
        return result

async def fleet_position_search_tool(state: dict) -> AgentState:
    await manager.send_to_thread("Performing timeseries search", state.get("thread_id", None))

    query_tools = QueryTools()
    logger.info("QueryTools initialized for fleet position search.")
    result = query_tools.fleet_position_search()
    logger.info(f"Fleet position search result: {result}")

    state["recommendation_data"] = result
    state["next_step"] = "recommendation_node"
    return AgentState(**state)