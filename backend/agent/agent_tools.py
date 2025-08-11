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

from dateutil.parser import parse

import json

import voyageai

import asyncio  
import websockets 


# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class AgentTools(MongoDBConnector):
    def __init__(self, collection_name: str=None, uri=None, database_name: str=None, appname: str=None):
        """
        AgentTools class to perform various actions for the agent.

        Args:
            collection_name (str): Collection name. Default is None.
            uri (str, optional): MongoDB URI. Default parent class value.
            database_name (str, optional): Database name. Default parent class value.
            appname (str, optional): Application name. Default parent class value.
        """
        super().__init__(uri, database_name, appname)

        # Load configuration
        config = ConfigLoader()
        self.config = config

        # Get configuration values
        self.mdb_timeseries_collection = self.config.get("MDB_TIMESERIES_COLLECTION")
        self.mdb_timeseries_timefield = self.config.get("MDB_TIMESERIES_TIMEFIELD")
        self.mdb_timeseries_granularity = self.config.get("MDB_TIMESERIES_GRANULARITY")

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

        if collection_name:
            # Set the collection name
            self.collection_name = collection_name
            self.collection = self.get_collection(self.collection_name)


    def vector_search(self, state: dict, ) -> dict:
        """Performs a vector search in a MongoDB collection."""
        message = "[Tool] Performing MongoDB Atlas Vector Search"
        logger.info(message)

        # Set default update message
        state.setdefault("updates", []).append(message)
        # Get embedding key - use "embedding" to match the actual field name in MongoDB
        # if state.get("embedding_key"):
        #     embedding_key = state["embedding_key"]
        # else:
            # Use "embedding" to match the field name in the collection and index
        embedding_key = "embedding"

        logger.info(f"Embedding key: {embedding_key}")
        # Get the embedding vector from the state, this is the embedded message
        embedding = state.get("embedding_vector", [])

        try:
            # Check if the index exists
            search_indexes = list(self.collection.list_search_indexes())
            index_names = [idx['name'] for idx in search_indexes]
            if self.mdb_vs_index in index_names:
                logger.info(f"Vector Search index '{self.mdb_vs_index}' already exists.")
                vector_index_creator_result = index_name = self.mdb_vs_index
                
            else:
                logger.info(f"Vector Search index '{self.mdb_vs_index}' does not exist. Creating...")
                vector_index_creator = VectorSearchIDXCreator()
                vector_index_creator_result = vector_index_creator.create_index()
                index_name = vector_index_creator_result.get("agentic_framework_queries_vs_idx", self.mdb_vs_index)
        except Exception as e:
            logger.error(f"[MongoDB] Error checking vector search index: {e}")
            state.setdefault("updates", []).append("[MongoDB] Error checking vector search.")
            index_name = vector_index_creator_result.get("agentic_framework_queries_vs_idx", self.mdb_vs_index)
        try:
            logger.info(f"[MongoDB] Performing vector search in collection: {self.collection_name} with index: {index_name}")
            # Perform vector search
            if self.collection is not None:
                pipeline = [
                    {
                        "$vectorSearch": {
                            "index": index_name,
                            "path": embedding_key,
                            "queryVector": embedding,
                            "numCandidates": 5,
                            "limit": 2
                        }
                    },
                    {
                        "$addFields": {"score": {"$meta": "vectorSearchScore"}}
                    },
              ]
                # Execute the aggregation pipeline
                results = self.collection.aggregate(pipeline)

                results = list(results)

                # logger.info(f"[MongoDB] Vector Search results: {type(results)}")

                filtered_results = []
                for i in results:
                    if "_id" in i:
                        del i["_id"]  # Remove the _id field from the results
                        del i[embedding_key]  # Remove the embedding field from the results
                        if "score" in i and i["score"] < 0.95:
                            # logger.info(f"[MongoDB] Vector Search result with low score: {i}")
                            continue
                    filtered_results.append(i)

                results = filtered_results

                # logger.info(f"[MongoDB] Vector Search result: {i}")

            if results:
                logger.info(f"[MongoDB] Retrieved similar data from vector search.")
                state.setdefault("updates", []).append("[MongoDB] Retrieved similar data.")
                similar_queries = results

                


                # logger.info(f"Similar queries - Vector Search results: {similar_queries}")
            else:
                logger.info(f"[MongoDB] No similar data found. Returning default message.")
                state.setdefault("updates", []).append("[MongoDB] No similar data found.")
                similar_queries = None
        except Exception as e:
            logger.error(f"Error during MongoDB Vector Search operation: {e}")
            state.setdefault("updates", []).append("[MongoDB] Error during Vector Search operation.")
            similar_queries = [{"query": "MongoDB Vector Search operation error", "recommendation": "Please try again later.", "score": 0.0}]
            
            return similar_queries

        return similar_queries

    def generate_chain_of_thought(self, state: AgentState) -> AgentState:
        """Generates the tool that should be used and a timestamp range based on the user query."""
        logger.info("[LLM Chain-of-Thought Reasoning]")
        # Instantiate the AgentProfiles class
        profiler = AgentProfiles(collection_name=self.mdb_agent_profiles_collection)
        # Get the agent profile
        p = profiler.get_agent_profile(agent_id="DECIDING_AGENT") # For this first call to the agent, we use the DECIDING_AGENT profile
        logger.info(f"Agent profile retrieved: {p}")
        # Get the Query Reported from the state
        query_reported = state["query_reported"]

        

        CHAIN_OF_THOUGHTS_PROMPT = get_chain_of_thoughts_prompt(
            agent_profile=p["profile"],
            agent_rules=p["rules"],
            agent_instructions=p["instructions"],
            agent_goals=p["goals"],
            query_reported=query_reported,
            agent_motive=p["goals"],
            agent_kind_of_data=p["kind_of_data"],
            embedding_model_name=self.embeddings_model_name,
            chat_completion_model_name=self.chatcompletions_model_name
        )

        # CHAIN_OF_THOUGHTS_PROMPT = (f"""Just provide an answer to the user query: {query_reported}. """)
        # logger.info("Chain-of-Thought Reasoning Prompt:")
        # logger.info(CHAIN_OF_THOUGHTS_PROMPT)
        try:
            # Instantiate the chat completion model
            chat_completions = BedrockAnthropicChatCompletions(model_id=self.chatcompletions_model_id)
            # Generate a chain of thought based on the prompt
            chain_of_thought = chat_completions.predict(CHAIN_OF_THOUGHTS_PROMPT)
            JSON_chain_of_thought = json.loads(chain_of_thought)

            logger.info(f"[LLM] Chain-of-Thought Reasoning: {JSON_chain_of_thought}")
            logger.info(f"[LLM] Chain-of-Thought Reasoning: {chain_of_thought}")

            next_step = JSON_chain_of_thought.get("tool", "vehicle_state_search_tool")
            
            # Map the LLM response to valid query tools
            tool_mapping = {
                "vehicle_state_search_tool": "vehicle_state_search_tool",
                "fleet_position_search_tool": "fleet_position_search_tool", 
                "get_vehicle_maintenance_data_tool": "get_vehicle_maintenance_data_tool",
                "vehicle_state_search": "vehicle_state_search_tool",
                "fleet_position_search": "fleet_position_search_tool",
                "maintenance_data": "get_vehicle_maintenance_data_tool",
                "vehicle_health": "get_vehicle_maintenance_data_tool",
                "location": "fleet_position_search_tool",
                "position": "fleet_position_search_tool"
            }
            
            # Resolve the tool name
            resolved_tool = tool_mapping.get(next_step, "vehicle_state_search_tool")
            
            logger.info(f"[LLM] Resolved tool: {resolved_tool}")
            
            state["next_step"] = resolved_tool  # This will be used by the router
            state["chain_of_thought"] = chain_of_thought
            state["response"] = next_step

        except Exception as e:
            logger.error(f"Error generating chain of thought: {e}")
            chain_of_thought = '{"tool": "vehicle_state_search_tool", "time_range": "last_7_days", "fields": ["default"]}'
            
            # Fallback to default tool
            state["next_step"] = "vehicle_state_search_tool"
            state["chain_of_thought"] = chain_of_thought
            state["response"] = "vehicle_state_search_tool"

        state.setdefault("updates", []).append("Chain-of-thought generated.")
        # chain_of_thought is already set above
        state["selected_tool"] = state.get("next_step", "vehicle_state_search_tool")
        state["agent_profile1"] = p["profile"]
        self.add_used_tools(state, "reasoning_node")
        return {**state}

    def get_query_embedding(self, state: AgentState) -> AgentState:
        """Generates the query embedding from voyage AI."""
        logger.info("[Action] Generating Query Embedding...")
        state.setdefault("updates", []).append("Generating query embedding...")

        # Get the query text
        text = state["query_reported"]

        try: 
            # Instantiate the Voyage AI Embedder

            # https://docs.voyageai.com/docs/embeddings

            # This will automatically use the environment variable VOYAGE_API_KEY.
            # Alternatively, you can use vo = voyageai.Client(api_key="<your secret key>")

            embedder = voyageai.Client()
            embedding_response = embedder.embed(text, model="voyage-3.5", input_type="document")
            embedding = embedding_response.embeddings[0]
            # logger.info(f"Generated embedding: {embedding}")
            state["embedding_vector"] = embedding
            state.setdefault("updates", []).append("Query embedding generated!")
            logger.info("Query embedding generated!")
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            state.setdefault("updates", []).append("Error generating query embedding; using dummy vector.")
            embedding = [0.0] * 1024
        return {**state, "embedding_vector": embedding, "next_step": "vector_search_tool"}
    
    def save_query_embedding(self, state: AgentState) -> AgentState:
        """Saves the query embedding to the state."""
        text = state.get("query_reported", "")
        embedding = state.get("embedding_vector", [])
        additional_fields = state.get("chain_of_thought", "")
        additional_fields = json.loads(additional_fields)

        try: 
            # Instantiate the Embedder
            embedder = Embedder(collection_name=self.mdb_embeddings_collection) # historical_recommendations collection
            # embedding = embedder.get_embedding(text)


            # Save the embedded question with the answer to MongoDB
            historical_recommendation = {
                "query": text,
                "recommendation": state.get("selected_tool", ""),
                "time_field": additional_fields.get("time_range", ""),
                "fields": additional_fields.get("fields", []),
                "embedding": embedding,
                "thread_id": state.get("thread_id", ""),
                "created_at": datetime.datetime.now(datetime.timezone.utc)
            }

            state["botPreferences"] = additional_fields

            # logger.info(f"Bot preferences updated in state: {state.get('botPreferences', '')}")

            # Convert ObjectIds to strings
            # historical_recommendation = convert_objectids(historical_recommendation)
            # Insert the historical recommendation into the MongoDB collection
            self.get_collection(self.mdb_historical_recommendations_collection).insert_one(historical_recommendation)
            logger.info(f"[MongoDB] Historical recommendation saved")
            state.setdefault("updates", []).append("Query embedding generated!")
            
            logger.info("Query embedding generated!")
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            state.setdefault("updates", []).append("Error generating query embedding; using dummy vector.")
            embedding = [0.0] * 1024
        
        # We go to the intended tool based on the response from the LLM
        
        return state
        
    def get_llm_recommendation(self, state: AgentState) -> AgentState:
        """Generates the LLM recommendation based on the data provided and the user question."""
        state.setdefault("updates", []).append("Generating final recommendation...")
        logger.info("[Final Answer] Generating final recommendation...")
        
        # Use default timeseries data if none is provided
        timeseries_data = state.get("recommendation_data")

        logger.info(f"[LLM] Timeseries data: {timeseries_data[0:3]}")
        logger.info(f"[LLM] Timeseries data length: {len(timeseries_data)}")

        # Instantiate the AgentProfiles class
        profiler = AgentProfiles(collection_name=self.mdb_agent_profiles_collection)
        # Get the agent profile
        p = profiler.get_agent_profile(agent_id="RECOMMENDING_AGENT")

        state["agent_profile2"] = p["profile"]

        # Generate the LLM recommendation prompt
        LLM_RECOMMENDATION_PROMPT = get_llm_recommendation_prompt(
            agent_role=p["role"],
            agent_kind_of_data=p["kind_of_data"],
            critical_info="No critical info",
            timeseries_data=timeseries_data,
            historical_recommendations_list=state.get("historical_recommendations_list", []),
            user_question = state["query_reported"]
        )
        try:
            # Instantiate the chat completion model
            chat_completions = BedrockAnthropicChatCompletions(model_id=self.chatcompletions_model_id)
            # Generate a chain of thought based on the prompt
            llm_recommendation = chat_completions.predict(LLM_RECOMMENDATION_PROMPT)
            
        except Exception as e:
            logger.error(f"Error generating LLM recommendation: {e}")
            llm_recommendation = "Unable to generate recommendation at this time."
        state.setdefault("updates", []).append("Final recommendation generated.")
        self.add_used_tools(state, "recommendation_node")
        logger.info(f"[LLM] Recommendation generated")
        state["recommendation_text"] = llm_recommendation
        return {**state, "recommendation_text": llm_recommendation, "next_step": "end"}

    def add_used_tools(self, state: AgentState, tool_name: str) -> AgentState:
        """Adds the used tools to the state."""
        logger.info(f"Adding used tool: {tool_name} to state")
        used_tools = state.get("used_tools", [])
        
        used_tools.append(tool_name)
        state["used_tools"] = used_tools
        return state

# Define tools

async def vector_search_tool(state: dict) -> dict:
    """Performs a vector search in a MongoDB collection."""
    await manager.broadcast("Performing vector search for historical recommendations")
    # Load configuration
    config = ConfigLoader()
    # Get the MongoDB collection name
    mdb_embeddings_collection = config.get("MDB_EMBEDDINGS_COLLECTION")
    # Instantiate the AgentTools class
    agent_tools = AgentTools(collection_name=mdb_embeddings_collection)
    agent_tools.add_used_tools(state, "vector_search_tool")
    result = agent_tools.vector_search(state=state)

    if result and len(result) > 0 and result[0]['score'] > 0.95:
        # Check if tools exist in the recommendation field
        recommendation = result[0]['recommendation']  
        logger.info(f"Recommendation from vector search: {recommendation}")

        # Map the recommendation to valid query tools
        tool_mapping = {
            "vehicle_state_search_tool": "vehicle_state_search_tool",
            "fleet_position_search_tool": "fleet_position_search_tool", 
            "get_vehicle_maintenance_data_tool": "get_vehicle_maintenance_data_tool",
            "vehicle_state_search": "vehicle_state_search_tool",
            "fleet_position_search": "fleet_position_search_tool",
            "maintenance_data": "get_vehicle_maintenance_data_tool"
        }
        
        resolved_tool = tool_mapping.get(recommendation, "vehicle_state_search_tool")
        state["next_step"] = resolved_tool
        state["vector_search_found_match"] = True  # Flag for routing
        logger.info(f"Vector search found high-confidence match, routing directly to: {resolved_tool}")
        agent_tools.add_used_tools(state, resolved_tool)
    else:
        state["vector_search_found_match"] = False  # Flag for routing
        state["next_step"] = "reasoning_node"
        logger.info("Vector search found no high-confidence match, routing to reasoning node")
    # search_results = len(result.get("historical_recommendations_list", []))
    return state

async def generate_chain_of_thought_tool(state: AgentState) -> AgentState:
    """Generates the chain of thought for the agent."""
    agent_tools = AgentTools()
    await manager.send_to_thread("Deciding which tools to use next", state.get("thread_id", ""))

    result = agent_tools.generate_chain_of_thought(state=state)
    
    # The next_step should already be set by generate_chain_of_thought method
    # Just ensure we pass through the state properly
    updated_state = {**state, **result}
    
    agent_tools.add_used_tools(updated_state, "reasoning_node")
    selected_tool = updated_state.get("selected_tool", "vehicle_state_search_tool")
    agent_tools.add_used_tools(updated_state, selected_tool)
    
    return updated_state
    return result

async def get_query_embedding_tool(state: AgentState) -> AgentState:
    """Generates the query embedding."""
    await manager.broadcast("Generating query embedding vector")
    agent_tools = AgentTools()
    result = agent_tools.get_query_embedding(state=state)
    embedding_size = len(result.get("embedding_vector", []))
    agent_tools.add_used_tools(state, "embedding_node")
    await manager.broadcast(f"Generated {embedding_size}-dimensional embedding")
    return result

async def get_llm_recommendation_tool(state: AgentState) -> AgentState:
    """Generates the LLM recommendation."""
    await manager.broadcast("Generating AI recommendation...")
    # Load configuration
    config = ConfigLoader()
    # Get the MongoDB collection name
    mdb_historical_recommendations_collection = config.get("MDB_HISTORICAL_RECOMMENDATIONS_COLLECTION")
    # Instantiate the AgentTools class
    agent_tools = AgentTools(collection_name=mdb_historical_recommendations_collection)
    result = agent_tools.get_llm_recommendation(state=state)
    return result

async def save_query_embedding_tool(state: dict) -> dict:
    """Saves the query embedding to the state."""
    await manager.broadcast("Saving new question's result to MongoDB")
    logger.info("Saving new question's result to MongoDB")
    # Instantiate the AgentTools class
    agent_tools = AgentTools()
    result = agent_tools.save_query_embedding(state=state)
    # We go to the intended tool based on the response from the LLM
    selected_tool = state.get("selected_tool", {})
    agent_tools.add_used_tools(state, "save_embedding_tool")
    logger.info(f"Selected tool: {selected_tool}")
    state["next_step"] = selected_tool if selected_tool else "end"
    return result

async def router_tool(state: dict) -> dict:
    """Router tool that prepares state for conditional routing."""
    logger.info("Router tool: preparing for conditional routing")
    
    # The routing decision should already be set in state["next_step"] 
    # by the reasoning_node or vector_search_tool
    next_step = state.get("next_step", "vehicle_state_search_tool")
    
    logger.info(f"Router tool directing to: {next_step}")
    await manager.broadcast(f"Routing to {next_step}")
    
    # Ensure the next_step is valid
    valid_tools = [
        "vehicle_state_search_tool", 
        "fleet_position_search_tool", 
        "get_vehicle_maintenance_data_tool"
    ]
    
    if next_step not in valid_tools:
        logger.warning(f"Invalid routing target: {next_step}, defaulting to vehicle_state_search_tool")
        next_step = "vehicle_state_search_tool"
        state["next_step"] = next_step
    
    return state

def route_to_query_tool(state: dict) -> str:
    """
    Condition function that determines which query tool to route to.
    This function is used by LangGraph's conditional edges.
    
    Returns:
        str: The name of the query tool to route to
    """
    next_step = state.get("next_step", "vehicle_state_search_tool")
    
    valid_tools = [
        "vehicle_state_search_tool", 
        "fleet_position_search_tool", 
        "get_vehicle_maintenance_data_tool"
    ]
    
    if next_step in valid_tools:
        logger.info(f"Conditional routing to: {next_step}")
        return next_step
    else:
        logger.warning(f"Invalid routing target: {next_step}, defaulting to vehicle_state_search_tool")
        return "vehicle_state_search_tool"

def route_from_vector_search(state: dict) -> str:
    """
    Condition function that determines whether to go to router_node or reasoning_node
    based on whether vector search found a high-confidence match.
    
    Returns:
        str: Either "router_node" or "reasoning_node"
    """
    found_match = state.get("vector_search_found_match", False)
    
    if found_match:
        logger.info("Vector search found high-confidence match, routing to router_node")
        return "router_node"
    else:
        logger.info("Vector search found no high-confidence match, routing to reasoning_node")
        return "reasoning_node"