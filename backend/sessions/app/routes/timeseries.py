from fastapi import APIRouter, status, Body
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder  
from database import timeseries_coll
from datetime import datetime, timezone
from backend.sessions.app.model.sessionModel import TimeseriesModel
from backend.sessions.app.model.sessionModel import VehicleModel
import time

router = APIRouter()

@router.post("/timeseries")
async def create_timeseries_entry(entry: TimeseriesModel):
    print("Creating timeseries entry...")
    print("Received data:", entry)

    vehicle = VehicleModel(  
        carID=entry.vehicle.carID,  
        currentGeozone=entry.vehicle.currentGeozone,  
        hasDriver=entry.vehicle.hasDriver,  
        isOilLeak=entry.vehicle.isOilLeak,  
        isEngineRunning=entry.vehicle.isEngineRunning,  
        isCrashed=entry.vehicle.isCrashed,  
        currentRoute=entry.vehicle.currentRoute  
    )  
    

    entry = TimeseriesModel(  
        # timestamp=datetime.fromisoformat("2023-10-27T10:30:00").astimezone(timezone.utc),
        vehicle=vehicle,  
        gasLevel=entry.gasLevel,
        maxGasLevel=entry.maxGasLevel,
        oilTemperature=entry.oilTemperature,
        oilLevel=entry.oilLevel,
        distanceTraveled=entry.distanceTraveled,
        performanceScore=entry.performanceScore,
        avaliabilityScore=entry.avaliabilityScore,
        runTime=entry.runTime,
        qualityScore=entry.qualityScore
    )
    print("Prepared entry for insertion:", entry)

    try:  
        result = timeseries_coll.insert_one(entry.dict())  
        return {"message": "Timeseries entry created successfully", "id": str(result.inserted_id)}  
    except Exception as e:  
        print(f"Error: {e}")  # Log the error for debugging  
        return {"message": "Error creating timeseries entry", "error": str(e)}  
    


