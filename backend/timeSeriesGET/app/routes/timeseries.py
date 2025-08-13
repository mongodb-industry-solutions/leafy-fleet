import ast
import logging
from fastapi import APIRouter, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  
from database import timeseries_coll, geofence_coll
from datetime import datetime, timezone
from model.timeseriesModel import TimeseriesModel
from model.timeseriesModel import VehicleModel
import time

from bson import ObjectId  
from typing import List, Optional  
from fastapi import Query  
import math  
import json

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
async def get_latest_timeseries_entries(preferences = Query(..., description="User preferences for the query"),
                                        thread_id: Optional[str] = Query(None, description="Thread ID for WebSocket messaging")):
    
    logger.info(f"Fetching latest timeseries entries with preferences: {preferences}")
    try:
        preferences = json.loads(preferences)
    except json.JSONDecodeError:
        # If not JSON, preprocess it into a valid Python list
        preferences_list = preferences.split(",")  # Split by commas
        logger.info(f"Preferences parsed as list: {preferences_list}")
        
    # match_stage = build_match_stage(preferences_list)

    # logger.info(f"Constructed match stage: {match_stage}")


    try:

        
        pipeline = [
            {
                "$match": {"metadata.sessions": {"$in": [thread_id]}}
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
       
            


        entries_cursor = timeseries_coll.aggregate(pipeline)
        entries = list(entries_cursor)
        return JSONResponse(content=entries)
    except Exception as e:
        print(f"Error fetching latest timeseries entries: {e}")
        return JSONResponse(status_code=500, content={"message": "Error fetching latest timeseries entries", "error": str(e)})

# @router.get("/timeseries/getByCarRange/{fleet1Limit}/{fleet2Limit}/{fleet3Limit}")
# async def get_timeseries_by_car_range(fleet1Limit: int, fleet2Limit: int, fleet3Limit: int):
    
#     # Need to get the cars up to the given limits for each fleet then filtered by the user's reporting preference
def calculate_distance(point1, point2):    
    """Calculate distance between two GeoJSON points in meters using Haversine formula"""    
    lat1, lon1 = point1["coordinates"][1], point1["coordinates"][0]    
    lat2, lon2 = point2["coordinates"][1], point2["coordinates"][0]    
        
    # Haversine formula    
    R = 6371000  # Earth's radius in meters    
        
    lat1_rad = math.radians(lat1)    
    lat2_rad = math.radians(lat2)    
    delta_lat = math.radians(lat2 - lat1)    
    delta_lon = math.radians(lon2 - lon1)    
        
    a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) +     
         math.cos(lat1_rad) * math.cos(lat2_rad) *     
         math.sin(delta_lon/2) * math.sin(delta_lon/2))    
        
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))    
    distance = R * c    
        
    return distance


def build_car_id_filter(car_id_filter: List[int]) -> dict:  
    """  
    Build car_id filter based on array containing 1, 2, and/or 3  
      
    Args:  
        car_id_filter: List containing any combination of [1, 2, 3] or empty []  
      
    Returns:  
        MongoDB match condition for car_id ranges  
    """  
    if not car_id_filter:  # Empty array - no car_id filtering  
        return {}  
      
    # Build car_id ranges based on filter array  
    car_id_conditions = []  
      
    if 1 in car_id_filter:  
        car_id_conditions.append({"car_id": {"$gte": 1, "$lte": 100}})  
      
    if 2 in car_id_filter:  
        car_id_conditions.append({"car_id": {"$gte": 101, "$lte": 200}})  
      
    if 3 in car_id_filter:  
        car_id_conditions.append({"car_id": {"$gte": 201, "$lte": 300}})  
      
    return {"$or": car_id_conditions}  
  
@router.post("/timeseries/nearest-geofence")          
async def get_vehicles_nearest_to_geofence(          
    session_id: str = Body(...),          
    geofence_names: List[str] = Body(...),          
    min_distance: Optional[float] = Body(0),  # meters          
    max_distance: Optional[float] = Body(10000),  # meters  
    car_id_filter: Optional[List[int]] = Body(default=[])  # NEW: Filter array for car_id ranges  
):          
    """          
    Get latest vehicle telemetry within distance range of geofence centroid(s)  
      
    Args:  
        session_id: Session identifier  
        geofence_names: List of geofence names to search near  
        min_distance: Minimum distance in meters (default: 0)  
        max_distance: Maximum distance in meters (default: 10000)  
        car_id_filter: Optional filter array [1,2,3] for car_id ranges:  
            - 1: car_id 1-100  
            - 2: car_id 101-200    
            - 3: car_id 201-300  
            - []: no filtering (default)  
    """          
    try:          
        # Validate car_id_filter values  
        valid_car_filters = [f for f in car_id_filter if f in [1, 2, 3]]  
          
        # First, get the geofence(s) centroid(s)          
        geofences = list(geofence_coll.find({"name": {"$in": geofence_names}}))          
                  
        if not geofences:          
            return JSONResponse(status_code=404, content={"message": "Geofences not found"})          
                  
        # Create centroids list      
        if len(geofences) == 1:          
            center_point = geofences[0]["centroid"]          
        else:          
            # Calculate center point of multiple centroids          
            avg_lng = sum(gf["centroid"]["coordinates"][0] for gf in geofences) / len(geofences)          
            avg_lat = sum(gf["centroid"]["coordinates"][1] for gf in geofences) / len(geofences)          
            center_point = {"type": "Point", "coordinates": [avg_lng, avg_lat]}          
              
        # Convert max distance from meters to radians (for $centerSphere)      
        # Earth radius = 6378100 meters      
        max_distance_radians = max_distance / 6378100      
              
        # Build the $geoWithin query      
        geo_query = {      
            "coordinates": {      
                "$geoWithin": {      
                    "$centerSphere": [      
                        center_point["coordinates"],  # [longitude, latitude]      
                        max_distance_radians      
                    ]      
                }      
            }      
        }      
              
        # If min_distance > 0, we need to exclude the inner circle      
        if min_distance > 0:      
            min_distance_radians = min_distance / 6378100      
            geo_query = {      
                "$and": [      
                    {      
                        "coordinates": {      
                            "$geoWithin": {      
                                "$centerSphere": [      
                                    center_point["coordinates"],      
                                    max_distance_radians      
                                ]      
                            }      
                        }      
                    },      
                    {      
                        "coordinates": {      
                            "$not": {      
                                "$geoWithin": {      
                                    "$centerSphere": [      
                                        center_point["coordinates"],      
                                        min_distance_radians      
                                    ]      
                                }      
                            }      
                        }      
                    }      
                ]      
            }      
          
        # Build car_id filter  
        car_id_match = build_car_id_filter(valid_car_filters)  
          
        # Build the base match condition  
        base_match = {  
            "metadata.sessions": {"$in": [session_id]},  
            **geo_query  # Unpack the geo query  
        }  
          
        # Add car_id filter if provided  
        if car_id_match:  
            base_match.update(car_id_match)  
                  
        # Pipeline using $geoWithin (compatible with time-series)      
        pipeline = [          
            # Stage 1: Match by session, car_id filter AND geospatial proximity using $geoWithin      
            {          
                "$match": base_match  
            },      
            # Stage 2: Sort by timestamp desc to get latest entries first      
            {          
                "$sort": {"timestamp": -1}          
            },          
            # Stage 3: Group by car_id to get latest entry per car          
            {          
                "$group": {          
                    "_id": "$car_id",          
                    "latest_telemetry": {"$first": "$$ROOT"}          
                }          
            },          
            # Stage 4: Replace root with latest telemetry          
            {          
                "$replaceRoot": {"newRoot": "$latest_telemetry"}          
            }      
        ]          
                  
        vehicles = list(timeseries_coll.aggregate(pipeline))      
              
        # Calculate actual distances and sort by distance      
        result = []          
        for vehicle in vehicles:      
            # Handle ObjectId serialization      
            if "_id" in vehicle:      
                vehicle["_id"] = str(vehicle["_id"])      
                  
            # Calculate actual distance      
            if "coordinates" in vehicle:      
                distance = calculate_distance(vehicle["coordinates"], center_point)      
                      
                vehicle_data = TimeseriesModel(**vehicle).model_dump(mode="json")          
                vehicle_data["distance_to_geofence"] = distance      
                #vehicle_data["target_geofences"] = [gf["name"] for gf in geofences]          
                #vehicle_data["car_id_filter_applied"] = valid_car_filters  # NEW: Show applied filter  
                result.append(vehicle_data)      
              
        # Sort by distance (since we can't use $near)      
        result.sort(key=lambda x: x["distance_to_geofence"])      
                  
        return JSONResponse(content=result)          
                  
    except Exception as e:          
        return JSONResponse(          
            status_code=500,           
            content={"message": "Error fetching vehicles near geofence", "error": str(e)}          
        )      
  
@router.post("/timeseries/inside-geofence")          
async def get_vehicles_inside_geofence(          
    session_id: str = Body(...),          
    geofence_names: List[str] = Body(...),  
    car_id_filter: Optional[List[int]] = Body(default=[])  # NEW: Filter array for car_id ranges  
):          
    """          
    Get latest vehicle telemetry inside specified geofence(s)  
      
    Args:  
        session_id: Session identifier  
        geofence_names: List of geofence names to search within  
        car_id_filter: Optional filter array [1,2,3] for car_id ranges:  
            - 1: car_id 1-100  
            - 2: car_id 101-200    
            - 3: car_id 201-300  
            - []: no filtering (default)  
    """          
    try:  
        # Validate car_id_filter values  
        valid_car_filters = [f for f in car_id_filter if f in [1, 2, 3]]  
          
        # Get the geofence(s)          
        geofences = list(geofence_coll.find({"name": {"$in": geofence_names}}))          
                  
        if not geofences:          
            return JSONResponse(status_code=404, content={"message": "Geofences not found"})          
                  
        # Create geometry for spatial query          
        if len(geofences) == 1:          
            # Single polygon          
            search_geometry = geofences[0]["geometry"]          
        else:          
            # Multiple polygons - create MultiPolygon          
            coordinates = [gf["geometry"]["coordinates"] for gf in geofences]          
            search_geometry = {          
                "type": "MultiPolygon",          
                "coordinates": coordinates          
            }          
          
        # Build car_id filter  
        car_id_match = build_car_id_filter(valid_car_filters)  
          
        # Build the base match condition for initial filtering  
        base_match = {  
            "metadata.sessions": {"$in": [session_id]}  
        }  
          
        # Add car_id filter if provided  
        if car_id_match:  
            base_match.update(car_id_match)  
                  
        # Pipeline: Get latest telemetry per car, then filter by geofence          
        pipeline = [          
            # Stage 1: Match by session and car_id filter         
            {          
                "$match": base_match  
            },          
            # Stage 2: Sort by timestamp desc          
            {          
                "$sort": {"timestamp": -1}          
            },          
            # Stage 3: Group by car_id to get latest entry per car          
            {          
                "$group": {          
                    "_id": "$car_id",          
                    "latest_telemetry": {"$first": "$$ROOT"}          
                }          
            },          
            # Stage 4: Replace root with latest telemetry          
            {          
                "$replaceRoot": {"newRoot": "$latest_telemetry"}          
            },          
            # Stage 5: Filter vehicles inside geofence(s)          
            {          
                "$match": {          
                    "coordinates": {          
                        "$geoWithin": {          
                            "$geometry": search_geometry          
                        }          
                    }          
                }          
            }          
        ]          
                  
        vehicles = list(timeseries_coll.aggregate(pipeline))  # Use imported collection      
        # Convert to Pydantic models and add geofence info          
        result = []          
        for vehicle in vehicles:      
            # Handle ObjectId serialization      
            if "_id" in vehicle:      
                vehicle["_id"] = str(vehicle["_id"])      
                      
            vehicle_data = TimeseriesModel(**vehicle).model_dump(mode="json")          
            #vehicle_data["inside_geofences"] = [gf["name"] for gf in geofences]  
            #vehicle_data["car_id_filter_applied"] = valid_car_filters  # NEW: Show applied filter          
            result.append(vehicle_data)          
                  
        return JSONResponse(content=result)          
                  
    except Exception as e:          
        return JSONResponse(          
            status_code=500,           
            content={"message": "Error fetching vehicles inside geofence", "error": str(e)}          
        )      

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
        if isinstance(preference[-1], str):
            logger.info(f"Converting preference {preference[-1]} to int")
            try:
                fleet_numbers.append(int(preference[-1]))
            except ValueError:
                logger.error(f"Invalid fleet number in preferences: {preference[-1]}")
        else:
            fleet_numbers.append(preference[-1])
    return fleet_numbers

def build_match_stage(user_preferences: str = None):
    """
    Build the match stage for the MongoDB query based on user preferences and agent filters.
    """
    match_stage = {}
    fleet_capacity = understand_fleet_number(user_preferences)

    logger.info(f"Building match stage with fleet capacity: {fleet_capacity}")

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

