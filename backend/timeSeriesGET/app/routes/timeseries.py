from fastapi import APIRouter, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  
from database import timeseries_coll
from datetime import datetime, timezone
from model.timeseriesModel import TimeseriesModel
from model.timeseriesModel import VehicleModel
import time

router = APIRouter()

@router.get("/timeseries")
async def get_timeseries_entries(body: dict = Body(...)):

    if body:
        pipeline = [  
        {"$match": body}, 
        {"$sort": {"timestamp": -1}},  
        {"$limit": 100},               
        ]
    else:
        pipeline = [
            {"$sort": {"timestamp": -1}},  
            {"$limit": 100},               
        ]
    try:

        entries = timeseries_coll.aggregate(pipeline)
        entries = list(entries)  # Convert the cursor to a list
        return JSONResponse(content=entries)
    except Exception as e:
        
        return JSONResponse(status_code=500, content={"message": "Error fetching timeseries entries", "error": str(e)})
    
@router.get("/timeseries/{carID}")
async def get_timeseries_by_carID(carID: str):
    """
    Fetch timeseries entries for a specific carID.
    Its expected that the user preferences will be sent in the body to filter the results accordingly.
    """

    try:
        entries_result = []
        entries_list = timeseries_coll.find({"carID": carID})
        for entry in entries_list:
            entries_result.append(
                
                TimeseriesModel(**entry).model_dump(
                    mode="json"
                )
            )
        if entries_list:
            return entries_result
        else:
            return JSONResponse(status_code=404, content={"message": f"No timeseries entries found for carID {carID} with the given preferences"})
    except Exception as e:
        
        return JSONResponse(status_code=500, content={"message": f"Error fetching timeseries entries for carID {carID}", "error": str(e)})

@router.get("/timeseries/latest/{carID}")
async def get_latest_timeseries_by_carID(carID: str):
    print(f"Fetching latest timeseries entry for carID: {carID}")
    try:
        entry = await timeseries_coll.find_one({"vehicle.carID": carID}, sort=[("timestamp", -1)])  # Fetch the latest entry for the given carID
        if entry:
            return JSONResponse(content=entry)
        else:
            return JSONResponse(status_code=404, content={"message": f"No timeseries entry found for carID {carID}"})
    except Exception as e:
        print(f"Error fetching latest timeseries entry for carID {carID}: {e}")
        return JSONResponse(status_code=500, content={"message": f"Error fetching latest timeseries entry for carID {carID}", "error": str(e)})
    
@router.get("/timeseries/all/latest")
async def get_latest_timeseries_entries():
    
    try:
        entries = await timeseries_coll.findOne().sort([("timestamp", -1)])  # Fetch the latest entry
        return JSONResponse(content=entries)
    except Exception as e:
        print(f"Error fetching latest timeseries entries: {e}")
        return JSONResponse(status_code=500, content={"message": "Error fetching latest timeseries entries", "error": str(e)})

# @router.get("/timeseries/getByCarRange/{fleet1Limit}/{fleet2Limit}/{fleet3Limit}")
# async def get_timeseries_by_car_range(fleet1Limit: int, fleet2Limit: int, fleet3Limit: int):
    
#     # Need to get the cars up to the given limits for each fleet then filtered by the user's reporting preference


    