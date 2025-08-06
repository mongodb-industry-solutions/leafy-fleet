from typing import Any, Dict, Optional
from db.mdb import MongoDBConnector

import ast

import logging
import datetime
import asyncio  
import websockets 
import asyncio

from async_workflow_runner import AsyncWorkflowRunner

import json
from bson import ObjectId
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter
from fastapi import WebSocket, WebSocketDisconnect

from config.config_loader import ConfigLoader
from utils import convert_objectids, format_document

from db.mdb import MongoDBConnector

from agent_workflow_graph import create_workflow_graph
from async_workflow_runner import create_async_workflow
from agent_state import AgentState
from agent_checkpointer import AgentCheckpointer

from websocketServer import manager 

import os
from dotenv import load_dotenv

load_dotenv()

# Load configuration
config = ConfigLoader()
# Get configuration values
# MongoDB URI
MDB_URI = os.getenv("MONGODB_URI")
# Database
MDB_DATABASE_NAME = config.get("MDB_DATABASE_NAME")
# Collections
MDB_HISTORICAL_RECOMMENDATIONS_COLLECTION = config.get("MDB_HISTORICAL_RECOMMENDATIONS_COLLECTION")
MDB_AGENT_SESSIONS_COLLECTION = config.get("MDB_AGENT_SESSIONS_COLLECTION")
MDB_EMBEDDINGS_COLLECTION = config.get("MDB_EMBEDDINGS_COLLECTION")
MDB_EMBEDDINGS_COLLECTION_VS_FIELD = config.get("MDB_EMBEDDINGS_COLLECTION_VS_FIELD")
MDB_TIMESERIES_COLLECTION = config.get("MDB_TIMESERIES_COLLECTION")
MDB_LOGS_COLLECTION = config.get("MDB_LOGS_COLLECTION")
MDB_AGENT_PROFILES_COLLECTION = config.get("MDB_AGENT_PROFILES_COLLECTION")
AGENT_PROFILE_CHOSEN_ID = config.get("AGENT_PROFILE_CHOSEN_ID")
# Checkpointer
MDB_CHECKPOINTER_COLLECTION = config.get("MDB_CHECKPOINTER_COLLECTION")
MDB_CHECKPOINTER_WRITES = MDB_CHECKPOINTER_COLLECTION + "_writes"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

@app.get("/")
async def read_root(request: Request):
    return {"message": "Server is running"}


@app.get("/run-agent")
async def run_agent(query_reported: str = Query("Default query reported by the user", 
                                                description="Query reported text"), thread_id: str = Query(..., description="Thread ID for the session"), 
                                                filters = Query(..., description="User selected checkbox filters"), 
                                                preferences = Query(..., description="User preferences for the query")): #This is a literal string, not a list or anything
    """Run the agent with the given query.

    Args:
        query_reported (str, optional): _description_. Defaults to Query("Default query reported by the user", description="Query reported text").

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """
    
    parsed_filters = ast.literal_eval(filters) if filters else []
    parsed_preferences = ast.literal_eval(preferences) if preferences else []
    initial_state: AgentState = {
        "userFilters": parsed_filters,
        "userPreferences": parsed_preferences,
        "botPreferences": [],
        "query_reported": query_reported,
        "chain_of_thought": "",
        "timeseries_data": [],
        "embedding_vector": [],
        "historical_recommendations_list": [],
        "recommendation_text": "",
        "next_step": "reasoning_node",
        "updates": [],
        "thread_id": thread_id,
        "used_tools": [],
    }
    await manager.send_to_thread("Agent started with query: " + query_reported, thread_id=thread_id)
    # thread_id = f"thread_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}" # Old definition of thread_id, this was moved to the session microservice
    initial_state["thread_id"] = thread_id
    config = {"configurable": {"thread_id": thread_id}} # https://langchain-ai.github.io/langgraph/concepts/persistence/#threads
    mongodb_checkpointer = AgentCheckpointer(database_name=MDB_DATABASE_NAME, collection_name=MDB_CHECKPOINTER_COLLECTION).create_mongodb_saver()
    logger.info("checkpointer state: " + str(mongodb_checkpointer))
    
    try:
        await manager.send_to_thread(message="Starting agent workflow execution...", thread_id=thread_id)
        logger.info(f"Starting agent workflow execution for thread ID: {thread_id}")
        async with mongodb_checkpointer as checkpointer:
            # Create the workflow graph with the checkpointerz
            # Pass the AgentCheckpointer instance

            """
            Version 1: Use everything in the async_workflow_runner.py
            Custom implementation of ainvoke that uses the checkpointer
            gets the context manager error if checkpoint is used
            """
            
            await manager.send_to_thread(message="Starting agent workflow execution...", thread_id=thread_id)
            logger.info(f"Starting agent workflow execution for thread ID: {thread_id}")
            
            # Pass the AgentCheckpointer instance
            workflow = await create_async_workflow(checkpointer=checkpointer)
            logger.info(f"Workflow created for thread ID: {thread_id}")
            final_state = await workflow.ainvoke(initial_state, config=config, thread_id=thread_id, query_reported=query_reported)
            await manager.send_to_thread(message="Workflow execution completed", thread_id=thread_id)
            



            """
            Version 2: Use directly the ainvoke method of the workflow graph
            This gives the error aget_tuple raise NotImplementedError
            """
            """
            async_workflow = AsyncWorkflowRunner()
            # async_workflow.checkpointer = checkpointer
            workflow = async_workflow._build_langgraph_workflow(checkpointer=checkpointer)

            logger.info(f"Workflow created for thread ID: {thread_id}")
            logger.info(f"Workflow type: {type(workflow)}")
            logger.info(f"Workflow has ainvoke method: {hasattr(workflow, 'ainvoke')}")

            logger.info(f"Workflow created for thread ID: {thread_id}")
            try:
                final_state = await workflow.ainvoke(initial_state, config=config)
                logger.info("Workflow invocation completed successfully")
            except Exception as workflow_error:
                logger.error(f"Workflow invocation failed: {type(workflow_error).__name__}: {str(workflow_error)}")
                logger.error("Workflow error traceback:", exc_info=True)
                raise  # Re-raise to be caught by outer exception handler
            await manager.send_to_thread(message="Workflow execution completed", thread_id=thread_id)
            """

        agent_profiles = []
        agent_profiles.append({
            "agent_profile_1": final_state.get("agent_profile1", {}),
            "agent_profile_2": final_state.get("agent_profile2", {})
        })
        final_state["agent_profiles"] = agent_profiles

        # For some reason I get problems returning final_state
        final_answer = {
            "thread_id": thread_id,
            "query_reported": query_reported,
            "recommendation_text": final_state.get('recommendation_text', 'No recommendation found'),
            "recommendation_data": final_state.get('recommendation_data', []),
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "checkpoint": final_state.get('checkpoint', None),
            "used_tools": final_state.get("used_tools", []),
            "agent_profiles": final_state.get('agent_profiles', []),
        }


        return final_answer
    except Exception as e:
        await manager.broadcast(f"Error occurred: {str(e)}")
        logger.info(f"[Error] An error occurred during execution: {e}")
        logger.info(f"You can resume this session later using thread ID: {thread_id}")
        try:
            with MongoDBConnector(uri=MDB_URI, database_name=MDB_DATABASE_NAME) as mdb_connector: 
                session_metadata = {
                    "thread_id": thread_id,
                    # "query_number": query_number,
                    "query_reported": query_reported,
                    "created_at": datetime.datetime.now(datetime.timezone.utc),
                    "status": "error",
                    "error_message": str(e)
                }
                session_metadata = convert_objectids(session_metadata)
                mdb_connector.insert_one(collection_name=MDB_AGENT_SESSIONS_COLLECTION, document=session_metadata)
                logger.info("[MongoDB] Error state recorded in session metadata")
        except Exception as db_error:
                logger.info(f"[MongoDB] Error storing session error state: {db_error}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, thread_id: str = Query(..., description="Thread ID for the session")):
    """
    WebSocket endpoint. Handles connection, disconnection, and keeps the connection alive.
    """
    await manager.connect(websocket, thread_id=thread_id)
    try:
        # This loop is essential. It keeps the connection open.
        # You could also receive messages from the client here if needed.
        while True:
            # We wait for a message from the client. If they disconnect,
            # a WebSocketDisconnect exception will be raised.
            await websocket.receive_text()
            # Note: In a real app, you might want to process the received text.
            # For this example, we just keep the connection alive.
            
    except WebSocketDisconnect:
        manager.disconnect(websocket) 
    
    
    



@app.get("/resume-agent")
async def resume_agent(thread_id: str = Query(..., description="Thread ID to resume session")):
    """Resume the agent with the given thread ID. 
    
    Args:
        thread_id (str, optional): Thread ID to resume session. Defaults to Query(..., description="Thread ID to resume session").

    Raises:
        HTTPException: _description_
    
    Returns:
        session: The session to resume.
    """
    try:
        with MongoDBConnector(uri=MDB_URI, database_name=MDB_DATABASE_NAME) as mdb_connector: 
            mdb_sessions_collection = mdb_connector.get_collection(MDB_AGENT_SESSIONS_COLLECTION)
            logger.info(f"Resuming agent for thread ID: {thread_id}")
            session = mdb_sessions_collection.find_one({"thread_id": thread_id})
        if session:
            session = convert_objectids(session)
            return session
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/get-sessions")
async def get_sessions():
    """Get the last 10 sessions. 
    
    Returns:
        sessions: The last 10 sessions.

    Raises:
        HTTPException
    """
    try:
        with MongoDBConnector(uri=MDB_URI, database_name=MDB_DATABASE_NAME) as mdb_connector:
            mdb_sessions_collection = mdb_connector.get_collection(MDB_AGENT_SESSIONS_COLLECTION)
            sessions = list(mdb_sessions_collection.find().sort("created_at", -1).limit(10))
        sessions = convert_objectids(sessions)
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/get-run-documents")
async def get_run_documents(thread_id: str = Query(..., description="Thread ID of the agent run")):
    """Get all documents for a given run. 
    
    Args:
        thread_id (str, optional): Thread ID of the agent run. Defaults to Query(..., description="Thread ID of the agent run").

    Returns:
        docs: The documents for the given run.
    """
    try:
        docs = {}

        # For collections where thread_id is stored with extra characters, use regex to find the right data
        query = {"thread_id": {"$regex": f"^{thread_id}"}}

        # Retrieve documents
        logger.info(f"Retrieving documents for thread ID: {thread_id}")
        with MongoDBConnector(uri=MDB_URI, database_name=MDB_DATABASE_NAME) as mdb_connector:
            mdb_historical_recommendations_collection = mdb_connector.get_collection(MDB_HISTORICAL_RECOMMENDATIONS_COLLECTION)
            mdb_agent_sessions_collection = mdb_connector.get_collection(MDB_AGENT_SESSIONS_COLLECTION)
            mdb_timeseries_collection = mdb_connector.get_collection(MDB_TIMESERIES_COLLECTION)
            mdb_logs_collection = mdb_connector.get_collection(MDB_LOGS_COLLECTION)
            mdb_agent_profiles_collection = mdb_connector.get_collection(MDB_AGENT_PROFILES_COLLECTION)
            mdb_embeddings_collection = mdb_connector.get_collection(MDB_EMBEDDINGS_COLLECTION)
            mdb_checkpoint_collection = mdb_connector.get_collection(MDB_CHECKPOINTER_COLLECTION)
        
            # Retrieve agent_sessions document
            session = mdb_agent_sessions_collection.find_one(query)

            # Retrieve historical_recommendations for the run
            historical = mdb_historical_recommendations_collection.find_one(query)

            # Retrieve 3 timeseries data points
            timeseries = list(mdb_timeseries_collection.find().limit(3))

            # Retrieve logs for the run
            log = mdb_logs_collection.find_one(query)

            # Retrieve the agent profile
            chosen_agent_id = AGENT_PROFILE_CHOSEN_ID or "DEFAULT"
            profile = mdb_agent_profiles_collection.find_one({"agent_id": chosen_agent_id})

            # Retrieve 3 queries from the embeddings collection
            queries = list(mdb_embeddings_collection.find().limit(3))

            # Retrieve the last checkpoint
            last_checkpoint = mdb_checkpoint_collection.find_one(query)
        
        logger.info(f"Formatting documents for thread ID: {thread_id}")
        # Format the documents
        docs["agent_sessions"] = format_document(session) if session else {}
        docs["historical_recommendations"] = format_document(historical) if historical else {}
        docs["agent_profile"] = format_document(profile) if profile else {}
        docs[MDB_TIMESERIES_COLLECTION] = [format_document(record) for record in timeseries] if timeseries else {}
        docs["queries"] = [format_document(record) for record in queries] if queries else {}
        docs["logs"] = format_document(log) if log else {}
        docs["last_checkpoint"] = format_document(last_checkpoint) if last_checkpoint else {}
        logger.info(f"Documents formatted for thread ID: {thread_id}")

        return docs
    except Exception as e:
        logger.error(f"Error while retrieving documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))