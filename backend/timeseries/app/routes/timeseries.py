from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.database import timeseries_coll
from datetime import datetime
from app.model.timeseriesModel import TimeseriesModel
from app.model.timeseriesModel import VehicleModel

router = APIRouter()

@router.post("/timeseries", summary="Create a new timeseries entry", 
             description="This endpoint allows you to create a new timeseries entry for vehicle telemetry data.", 
             response_description="=Entry created successfully")
async def create_timeseries_entry(data):

    vehicle = VehicleModel(
        carId=data.get("carId"),
        currentGeozone=data.get("currentGeozone"),
        hasDriver=data.get("hasDriver"),
        isOilLeak=data.get("isOilLeak"),
        isEngineRunning=data.get("isEngineRunning"),
        isCrashed=data.get("isCrashed"),
        currentRoute=data.get("currentRoute"),
    )

    entry = TimeseriesModel(
        timestamp=datetime.utcnow(),
        vehicle=vehicle,
        gasLevel=data.get("gasLevel"),
        maxGasLevel=data.get("maxGasLevel"),
        oilTemperature=data.get("oilTemperature"),
        oilLevel=data.get("oilLevel"),
        distanceTraveled=data.get("distanceTraveled"),
        performanceScore=data.get("performanceScore"),
        avaliabilityScore=data.get("avaliabilityScore"),
        runTime=data.get("runTime"),
        qualityScore=data.get("qualityScore")
    )

    try:
        await timeseries_coll.insert_one(entry.model_dump())
        return JSONResponse(status_code=status.HTTP_200_OK, content={"Entry created successfully"})
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": "Error creating entry", "error": str(e)})
