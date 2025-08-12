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
  

@router.post("/timeseries/nearest-geofence")      
async def get_vehicles_nearest_to_geofence(      
    session_id: str = Body(...),      
    geofence_names: List[str] = Body(...),      
    min_distance: Optional[float] = Body(0),  # meters      
    max_distance: Optional[float] = Body(10000),  # meters      
):      
    """      
    Get latest vehicle telemetry within distance range of geofence centroid(s)      
    """      
    try:      
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
              
        # Pipeline using $geoWithin (compatible with time-series)  
        pipeline = [      
            # Stage 1: Match by session AND geospatial proximity using $geoWithin  
            {      
                "$match": {      
                    "metadata.sessions": {"$in": [session_id]},  
                    **geo_query  # Unpack the geo query  
                }      
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
                vehicle_data["target_geofences"] = [gf["name"] for gf in geofences]      
                result.append(vehicle_data)  
          
        # Sort by distance (since we can't use $near)  
        result.sort(key=lambda x: x["distance_to_geofence"])  
              
        return JSONResponse(content=result)      
              
    except Exception as e:      
        return JSONResponse(      
            status_code=500,       
            content={"message": "Error fetching vehicles near geofence", "error": str(e)}      
        )  
  
  
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

@router.post("/timeseries/inside-geofence")      
async def get_vehicles_inside_geofence(      
    session_id: str = Body(...),      
    geofence_names: List[str] = Body(...)      
):      
    """      
    Get latest vehicle telemetry inside specified geofence(s)      
    """      
    try:      
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
              
        # Pipeline: Get latest telemetry per car, then filter by geofence      
        pipeline = [      
            # Stage 1: Match by session      
            {      
                "$match": {      
                    "metadata.sessions": {"$in": [session_id]}      
                }      
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
            vehicle_data["inside_geofences"] = [gf["name"] for gf in geofences]      
            result.append(vehicle_data)      
              
        return JSONResponse(content=result)      
              
    except Exception as e:      
        return JSONResponse(      
            status_code=500,       
            content={"message": "Error fetching vehicles inside geofence", "error": str(e)}      
        )  
