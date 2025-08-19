from fastapi import APIRouter, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  
from database import sessions_coll
from datetime import datetime
from model.sessionModel import Message
from model.sessionModel import MessageEntry
from bson import ObjectId
from fastapi.encoders import jsonable_encoder  
from pymongo import ReturnDocument  

router = APIRouter()

@router.post("/message")  
async def update_message(entry: MessageEntry): 
    # Validate thread_id  
    if not entry.thread_id:  
        return JSONResponse(  
            status_code=status.HTTP_400_BAD_REQUEST,  
            content={"message": "Field thread_id is required in the request body."}  
        )  
      
    try:  
        object_id = ObjectId(entry.thread_id)  
    except Exception:  
        return JSONResponse(  
            status_code=status.HTTP_400_BAD_REQUEST,  
            content={"message": "Invalid thread_id format (must be a valid ObjectId)."}  
        )  
    try:  
        # Find the session by _id  
        session = sessions_coll.find_one({"_id": object_id})  
        if not session:  
            return JSONResponse(  
                status_code=status.HTTP_404_NOT_FOUND,  
                content={"message": "Session not found"}  
            )  
          
        # Prepare new message  
        msg_index = len(session.get("chat_history", []))  # Use existing chat_history length  
        new_msg = Message(message=entry.message, index=msg_index, sender=entry.sender, completed=entry.completed).dict()  
          
        # Update chat_history and last_used_at  
        updated_session = sessions_coll.find_one_and_update(  
    {"_id": object_id},  
    {  
        "$push": {"chat_history": new_msg},  
        "$set": {"last_used_at": datetime.utcnow()},  
    },  
    return_document=ReturnDocument.AFTER ) 
        if updated_session:  
            # Convert last_used_at (datetime) to ISO format for JSON serialization  
            last_used_at = updated_session["last_used_at"].isoformat() if "last_used_at" in updated_session else None  
        
            return JSONResponse(  
                status_code=status.HTTP_200_OK,  
                content={  
                    "message": "Message added",  
                    "updated_chat_history": updated_session["chat_history"],  
                    "last_used_at": last_used_at  
                }  
            )  
        else:  
            return JSONResponse(  
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  
                content={"message": "Failed to update session"}  
            )  
    except Exception as e:  
        return JSONResponse(  
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  
            content={"message": "Error updating message", "error": str(e)}  
        )  

#no need to use this endpoint, as the messages are stored in the session
@router.get("/messages/{thread_id}")
async def get_messages(thread_id: str):
    try:  
            object_id = ObjectId(thread_id)  
    except Exception:  
            return JSONResponse(  
                status_code=status.HTTP_400_BAD_REQUEST,  
                content={"message": "Invalid thread_id format (must be a valid ObjectId)."}  
            )
    try:  
        session = sessions_coll.find_one({"_id": object_id})
        if not session:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "Session not found"}
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder({"chat_history": session.get("chat_history", [])})
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "Error retrieving messages", "error": str(e)}
        )
    