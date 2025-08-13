import ast
import logging
from fastapi import APIRouter, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  
from database import timeseries_coll
from datetime import datetime, timezone
from model.timeseriesModel import TimeseriesModel
from model.timeseriesModel import VehicleModel
import time
from fastapi import FastAPI, HTTPException, Request, Query, APIRouter, WebSocket, WebSocketDisconnect, Body

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)



router = APIRouter()

@router.get("/timeseries")
async def get_timeseries_entries(body: dict = Body(...)):

    if body:
        pipeline = [  
        {"$match": body}, 
        {"$sort": {"timestamp": -1}},  
        {"$limit": 400},               
        ]
    else:
        pipeline = [
            {"$sort": {"timestamp": -1}},  
            {"$limit": 400},               
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
async def get_latest_timeseries_entries(preferences = Query(..., description="User preferences for the query")):
    
    logger.info(f"Fetching latest timeseries entries with preferences: {preferences}")

    try:
        preferences = ast.literal_eval(preferences)
        if preferences:
            match_stage = build_match_stage(preferences)

        if match_stage:
            pipeline = [
                {
                    "$match": match_stage
                },
                {
                    "$group": {
                        "_id": "$car_id",
                        "car_id": {"$first": "$car_id"},
                        "timestamp": {"$first": "$timestamp"},
                        "availability_score": {"$first": "$availability_score"},
                        "current_route": {"$first": "$current_route"},
                        "run_time": {"$first": "$run_time"},
                        "performance_score": {"$first": "$performance_score"},
                        "oil_temperature": {"$first": "$oil_temperature"},
                        "current_geozone": {"$first": "$current_geozone"},
                        "engine_oil_level": {"$first": "$engine_oil_level"},
                        "is_crashed": {"$first": "$is_crashed"},
                        "metadata": {"$first": "$metadata"},
                        "average_speed": {"$first": "$average_speed"},
                        "quality_score": {"$first": "$quality_score"},
                        "is_moving": {"$first": "$is_moving"},
                        "coordinates": {"$first": "$coordinates"},
                        "oee": {"$first": "$oee"},
                        "fuel_level": {"$first": "$fuel_level"},
                        "max_fuel_level": {"$first": "$max_fuel_level"},
                        "speed": {"$first": "$speed"},
                        "is_engine_running": {"$first": "$is_engine_running"},
                        "is_oil_leak": {"$first": "$is_oil_leak"},
                        "traveled_distance": {"$first": "$traveled_distance"}
                    }
                },
                {
                    "$sort": {"timestamp": -1}
                },
            ]
        else:
            pipeline = [
                {
                    "$group": {
                        "_id": "$car_id",
                        "car_id": {"$first": "$car_id"},
                        "timestamp": {"$first": "$timestamp"},
                        "availability_score": {"$first": "$availability_score"},
                        "current_route": {"$first": "$current_route"},
                        "run_time": {"$first": "$run_time"},
                        "performance_score": {"$first": "$performance_score"},
                        "oil_temperature": {"$first": "$oil_temperature"},
                        "current_geozone": {"$first": "$current_geozone"},
                        "engine_oil_level": {"$first": "$engine_oil_level"},
                        "is_crashed": {"$first": "$is_crashed"},
                        "metadata": {"$first": "$metadata"},
                        "average_speed": {"$first": "$average_speed"},
                        "quality_score": {"$first": "$quality_score"},
                        "is_moving": {"$first": "$is_moving"},
                        "coordinates": {"$first": "$coordinates"},
                        "oee": {"$first": "$oee"},
                        "fuel_level": {"$first": "$fuel_level"},
                        "max_fuel_level": {"$first": "$max_fuel_level"},
                        "speed": {"$first": "$speed"},
                        "is_engine_running": {"$first": "$is_engine_running"},
                        "is_oil_leak": {"$first": "$is_oil_leak"},
                        "traveled_distance": {"$first": "$traveled_distance"}
                    }
                },
                {
                    "$sort": {"timestamp": -1}
                },
            ]


        entries_cursor = timeseries_coll.aggregate(pipeline)
        entries = list(entries_cursor)
        return JSONResponse(content=entries)
    except Exception as e:
        print(f"Error fetching latest timeseries entries: {e}")
        return JSONResponse(status_code=500, content={"message": "Error fetching latest timeseries entries", "error": str(e)})

# @router.get("/timeseries/getByCarRange/{fleet1Limit}/{fleet2Limit}/{fleet3Limit}")
# async def get_timeseries_by_car_range(fleet1Limit: int, fleet2Limit: int, fleet3Limit: int):
    
#     # Need to get the cars up to the given limits for each fleet then filtered by the user's reporting preference

def understand_fleet_number(user_preferences: str):
    """       
    Understand the fleet number from user preferences.

    Args:
        user_preferences (str): User preferences string.

    Returns:
        [int]: an array of the last car IDs in the fleet
        for example [50,150,250] for fleets 1,2,3 so we know we should search for car IDs 0-50, 100-150, 200-250
    """
    fleet_numbers = []
    for preference in user_preferences:
        if isinstance(preference[-1], int):
            fleet_numbers.append(preference[-1])
    return fleet_numbers

def build_match_stage(user_preferences: str = None):
    """
    Build the match stage for the MongoDB query based on user preferences and agent filters.
    """
    match_stage = {}
    fleet_capacity = understand_fleet_number(user_preferences)

    # Handle empty fleet_capacity
    if fleet_capacity and len(fleet_capacity) > 0:
        match_stage["$or"] = []
        for fleet_size in fleet_capacity:
            
            car_ids1 = None
            car_ids2 = None
            car_ids3 = None

            if fleet_size[0] > 0:
                car_ids1 = list(range(0, fleet_capacity[0]))  # Car IDs 0-99
                match_stage["$or"].append({"car_id": {"$in": car_ids1}})
            if fleet_size[2] > 0:
                car_ids2 = list(range(100, fleet_capacity[1]))  # Car IDs 100-199
                match_stage["$or"].append({"car_id": {"$in": car_ids2}})
            if fleet_size[3] > 0:
                car_ids3 = list(range(200, fleet_capacity[2]))  # Car IDs 200-299
                match_stage["$or"].append({"car_id": {"$in": car_ids3}})

    else:
        match_stage = {}  # No filtering applied

    return match_stage