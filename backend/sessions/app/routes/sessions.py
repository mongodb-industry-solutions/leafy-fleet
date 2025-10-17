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
    logger.info("[SESSIONS SERVICE] ========== Creating new session ==========")
    logger.info(f"[SESSIONS SERVICE] Received data: {entry.dict()}")
    logger.info(f"[SESSIONS SERVICE] Vehicle fleet config: {entry.vehicle_fleet}")

    try:
        entry_dict = entry.dict()
        logger.info(f"[SESSIONS SERVICE] Inserting document into MongoDB: {entry_dict}")

        result = sessions_coll.insert_one(entry_dict)
        logger.info(f"[SESSIONS SERVICE] MongoDB insert result - inserted_id: {result.inserted_id}")

        sessions_coll.update_one(
            {"_id": result.inserted_id},
            {"$set": {
                "last_used_at": datetime.now(timezone.utc)
            }}
        )

        session_id_str = str(result.inserted_id)
        logger.info(f"[SESSIONS SERVICE] Session created successfully with ID: {session_id_str}")
        logger.info(f"[SESSIONS SERVICE] Returning session_id to frontend: {session_id_str}")

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder({"session_id": session_id_str})
        )
    except Exception as e:
        logger.error(f"[SESSIONS SERVICE] ERROR creating session: {e}")
        logger.error(f"[SESSIONS SERVICE] Exception type: {type(e).__name__}")
        logger.error(f"[SESSIONS SERVICE] Exception details: {str(e)}")
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
        # Query and update last_used_at if document exists  
        session = sessions_coll.find_one_and_update(  
            {"_id": object_id},  
            {"$set": {"last_used_at": datetime.utcnow()}},  
            return_document=True  # Return the updated document  
        )  
            
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