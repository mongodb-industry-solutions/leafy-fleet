from fastapi import APIRouter, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  
from database import timeseries_coll
from datetime import datetime, timezone
from model.timeseriesModel import TimeseriesModel
from model.timeseriesModel import VehicleModel
import time

router = APIRouter()

@router.post("/timeseries")
async def create_timeseries_entry(entry: TimeseriesModel):
    print("Creating timeseries entry...")
    print("Received data:", entry)

    entry = TimeseriesModel(
        timestamp=entry.timestamp,
        VIN=entry.vin,
        FuelLevel=entry.fuel_level,
        OilTemperature=entry.oil_temperature,
        EngineOilLevel=entry.engine_oil_level,
        TraveledDistance=entry.traveled_distance,
        TraveledDistanceSinceStart=entry.traveled_distance_since_start,
        performanceScore=entry.performance_score,
        avaliabilityScore=entry.avaliability_score,
        RunTime=entry.run_time,
        qualityScore=entry.quality_score,
        isOilLeak=entry.is_oil_leak,
        isEngineRunning=entry.is_engine_running,
        isCrashed=entry.is_crashed,
        currentRoute=entry.current_route,
        # Latitude and longitude come in entry, but will only be used for coordinates
        Speed=entry.speed,
        AverageSpeed=entry.average_speed,
        IsMoving=entry.is_moving,
        currentGeozone=entry.current_geozone
    )
    # Convert coordinates to GeoJSON format
    entry.coordinates = {
        "type": "Point",
        "coordinates": [round(entry.longitude, 6), round(entry.latitude,6)]  
    }
    print("Prepared entry for insertion:", entry)

    try:  
        result = timeseries_coll.insert_one(entry.dict())  
        return {"message": "Timeseries entry created successfully", "id": str(result.inserted_id)}  
    except Exception as e:  
        print(f"Error: {e}")  # Log the error for debugging  
        return {"message": "Error creating timeseries entry", "error": str(e)}  
    


