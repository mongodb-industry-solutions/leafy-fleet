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



#  Class for the Static Model will no longer be nested 
class VehicleModel(BaseModel):  
    # _id: PyObjectId = Field(default_factory=PyObjectId) # Mongo assignes a unique ID to each document
    Brand: str
    Model: str
    LicensePlate: str
    DriverName: str
    VIN: int
    Year: int
    Length: float 
    BodyType: str
    VehicleExteriorColor: str
    WMI: str
    Weight: float
    carID: int # del 1 al 300, carID is used to connect with timeseriesModel, 
    # good if want to preload the data of 300 cars, else for easy comparision routes with carID

#Class for the Timeseries Model
class TimeseriesModel(BaseModel):
    """
    Timeseries data for vehicle telemetry.
    This model captures various metrics related to vehicle performance, fuel levels, and operational efficiency.
    It is designed to be used in a time-series database, allowing for efficient storage and retrieval

    se conectara a su ruta mediante el carID, para conectar con vehicleModel usamos VIN
    """
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    # _id: PyObjectId = Field(default_factory=PyObjectId)
    VIN: int 
    FuelLevel: float # In ml
    maxFuelLevel: float # In ml, no creo que se ocupe
    OilTemperature: float # In Celsius
    EngineOilLevel: float # In ml
    TraveledDistance : float # Field(default=31220.0, description="Total distance traveled by the vehicle in km")
    TraveledDistanceSinceStart: float # Field(default=0.0, description="Distance traveled since the start of the route in km")
    performanceScore: float # From 0 to 100, used to check whether the vehicle is achieving its objective, visiting all needed keypoints
    avaliabilityScore: float # From 0 to 100, also for OEE, run time vs planned time, in our case run time of a route with traffic vs a planned route without traffic
    RunTime: float # is Used to measure type:"sensor". datatype:"float" deprecation:"v5.0 OBD-branch is deprecated." description:"PID 1F - Engine run time" unit:"s"
    qualityScore: float # From 0 to 100, for example that the package was delivered on to the correct house instead of the neighbours house, in our simulation this can be also always 100% correct
    isOilLeak: bool
    isEngineRunning: bool
    isCrashed: bool
    currentRoute: int
    #Latitude: float 
    #Longitude: float 
    Speed: float # Field(default=0.0, description="Average speed of the vehicle in km/h")
    AverageSpeed: float # Field(default=0.0, description="Average speed of the vehicle in km/h over the route")
    IsMoving: bool # Field(default=True, description="Indicates if the vehicle is currently moving")
    currentGeozone: str # will update every 10 steps
    coordinates: List[float] 