from fastapi import APIRouter, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  
from database import timeseries_coll
from datetime import datetime
from model.timeseriesModel import TimeseriesModel
from typing import List  # Import List  
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/timeseries")
async def create_timeseries_entry(entry: TimeseriesModel):
    #print("Creating timeseries entry...")
    #print("Received data:", entry)

    if entry.timestamp is None:
        entry.timestamp = datetime.utcnow()
    # Convert coordinates to GeoJSON format
    
    #print("Prepared entry for insertion:", entry)

    try:  
        result = timeseries_coll.insert_one(entry.dict())  
        #print("Insert result:", result)
        return JSONResponse(  
            status_code=status.HTTP_201_CREATED,  
            content=jsonable_encoder({"message": "Timeseries entry created successfully", "id": str(result.inserted_id)})  
        )
       # return {"message": "Timeseries entry created successfully", "id": str(result.inserted_id)}  
    except Exception as e:  
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,  
            content=jsonable_encoder({"message": "Error creating timeseries entry", "error": str(e)})  
        )
    

@router.post("/historic-batch")  
async def create_historic_batch(entries: List[TimeseriesModel]):  
    try:
        # Convert entries directly to documents
        documents = []
        for doc in entries:
            doc_dict = doc.dict()
            # Ensure timestamp is a datetime object
            if isinstance(doc_dict['timestamp'], str):
                doc_dict['timestamp'] = datetime.fromisoformat(doc_dict['timestamp'].replace('Z', '+00:00'))
            documents.append(doc_dict)

        # Execute bulk insert_many instead of bulkWrite
        result = timeseries_coll.insert_many(documents)
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,   
            content=jsonable_encoder({
                "message": "Historical entries processed",
                "inserted_count": len(result.inserted_ids)
            })
        )
    except Exception as e:
        logger.error(f"Bulk insert error: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,   
            content=jsonable_encoder({
                "message": "Error creating historical entries", 
                "error": str(e)
            })
        )