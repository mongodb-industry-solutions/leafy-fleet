
from pydantic import ConfigDict, BaseModel, Field
from typing import Optional, List
from typing_extensions import Annotated
from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument
from pydantic.functional_validators import BeforeValidator
from datetime import datetime, timezone
from pydantic import BaseModel, Field  
PyObjectId = Annotated[str, BeforeValidator(str)]
import time

  
# Custom ObjectId type for Pydantic  
class PyObjectId(ObjectId):  
    @classmethod  
    def __get_validators__(cls):  
        yield cls.validate  
  
    @classmethod  
    def validate(cls, v):  
        if not ObjectId.is_valid(v):  
            raise ValueError("Invalid ObjectId")  
        return ObjectId(v)  
  
    @classmethod  
    def __modify_schema__(cls, field_schema):  
        field_schema.update(type="string") 



# Nested Class for the Telemetry/Timeseries Model
class VehicleModel(BaseModel):  
    # _id: PyObjectId = Field(default_factory=PyObjectId) # Mongo assignes a unique ID to each document
    currentGeozone: str
    hasDriver: bool
    isOilLeak: bool
    isEngineRunning: bool
    isCrashed: bool
    currentRoute: int
     



class TimeseriesModel(BaseModel):
    """
    Timeseries data for vehicle telemetry.
    This model captures various metrics related to vehicle performance, fuel levels, and operational efficiency.
    It is designed to be used in a time-series database, allowing for efficient storage and retrieval
    """
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # _id: PyObjectId = Field(default_factory=PyObjectId)
    vehicle_number : int
    vehicle: VehicleModel
    gasLevel: float # In ml
    maxGasLevel: float # In ml
    oilTemperature: float # In Celsius
    oilLevel: float # In ml
    distanceTraveled: float # In meters, used to calculate fuel efficiency
    performanceScore: float # From 0 to 100, used to check whether the vehicle is achieving its objective, visiting all needed keypoints
    avaliabilityScore: float # From 0 to 100, also for OEE, run time vs planned time, in our case run time of a route with traffic vs a planned route without traffic
    runTime: float # is Used to measure
    qualityScore: float # From 0 to 100, for example that the package was delivered on to the correct house instead of the neighbours house, in our simulation this can be also always 100% correct
    # OEE = avaliabilityScore * performanceScore * qualityScore