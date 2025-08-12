from fastapi import APIRouter, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  
from database import timeseries_coll
from datetime import datetime
from model.timeseriesModel import TimeseriesModel
from typing import List  # Import List  

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
    for doc in entries:  
        doc.timestamp = doc.timestamp or datetime.utcnow() 
    try:  
        # Insert multiple documents at once  
        result = timeseries_coll.insert_many([entry.dict() for entry in entries])  
        return JSONResponse(status_code=status.HTTP_201_CREATED,   
                            content=jsonable_encoder({"message": f"{len(result.inserted_ids)} historical entries added"}))
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,   
                            content=jsonable_encoder({"message": "Error creating historical entries", "error": str(e)})) 
    