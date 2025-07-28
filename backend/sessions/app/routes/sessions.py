from fastapi import APIRouter, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  
from database import sessions_coll
from datetime import datetime, timezone
from model.sessionModel import SessionModel
from bson import ObjectId
import logging


router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/sessions/create")
def create_timeseries_entry(entry: SessionModel):
    logger.info("Creating new session...")
    logger.info(f"Received data: {entry}")

    try:  
        result = sessions_coll.insert_one(entry.dict())
        sessions_coll.update_one(
            {"_id": result.inserted_id}, 
            {"$set": {
                "last_used_at": datetime.now(timezone.utc)
            }}
        )
        logger.info(f"Session created with ID: {result.inserted_id}") 
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder({"session_id": str(result.inserted_id)})
        )
    except Exception as e:  
        logger.error(f"Error: {e}")  # Log the error for debugging  
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Error creating session", "error": str(e)}
        )

@router.get("/sessions/{thread_id}")
def get_session(thread_id: str):
    logger.info(f"Fetching session with thread_id: {thread_id}")
    try:
        # Validate thread_id as a valid ObjectId
        object_id = ObjectId(thread_id)
    except Exception:
        logger.error("Invalid thread_id format")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Invalid thread_id format (must be a valid ObjectId)."}
        )
    try:
        # Query using ObjectId
        session = sessions_coll.find_one({"_id": object_id})
        
        if session:
            # Convert ObjectId to string for JSON serialization
            if "_id" in session:
                session["_id"] = str(session["_id"])
            
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=jsonable_encoder(session)
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "Session not found"}
            )
    except Exception as e:
        logger.error(f"Error fetching session: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Internal server error", "error": str(e)}
        )