from fastapi import APIRouter, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  
from database import timeseries_coll
from datetime import datetime
from model.timeseriesModel import TimeseriesModel

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
        #print(f"Error: {e}")  # Log the error for debugging  
        return {"message": "Error creating timeseries entry", "error": str(e)}  
    


