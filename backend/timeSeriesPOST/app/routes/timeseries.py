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
        VIN=entry.VIN,
        FuelLevel=entry.FuelLevel,
        maxFuelLevel=entry.maxFuelLevel,
        OilTemperature=entry.OilTemperature,
        EngineOilLevel=entry.EngineOilLevel,
        TraveledDistance=entry.TraveledDistance,
        TraveledDistanceSinceStart=entry.TraveledDistanceSinceStart,
        performanceScore=entry.performanceScore,
        avaliabilityScore=entry.avaliabilityScore,
        RunTime=entry.RunTime,
        qualityScore=entry.qualityScore,
        isOilLeak=entry.isOilLeak,
        isEngineRunning=entry.isEngineRunning,
        isCrashed=entry.isCrashed,
        currentRoute=entry.currentRoute,
        # Latitude and longitude come in entry, but will only be used for coordinates
        Speed=entry.Speed,
        AverageSpeed=entry.AverageSpeed,
        IsMoving=entry.IsMoving,
        currentGeozone=entry.currentGeozone
    )
    # Convert coordinates to GeoJSON format
    entry.coordinates = {
        "type": "Point",
        "coordinates": [round(entry.Longitude, 6), round(entry.Latitude,6)]  
    }
    print("Prepared entry for insertion:", entry)

    try:  
        result = timeseries_coll.insert_one(entry.dict())  
        return {"message": "Timeseries entry created successfully", "id": str(result.inserted_id)}  
    except Exception as e:  
        print(f"Error: {e}")  # Log the error for debugging  
        return {"message": "Error creating timeseries entry", "error": str(e)}  
    


