from typing import Optional, List
from typing_extensions import Annotated
from bson import ObjectId
from pydantic.functional_validators import BeforeValidator
from datetime import datetime
from pydantic import BaseModel, Field  
PyObjectId = Annotated[str, BeforeValidator(str)]

  
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

class MaintenanceLog(BaseModel):
    date: datetime
    description: str
    cost: Optional[float] = None

#  Class for the Static Model will no longer be nested 
class VehicleModel(BaseModel):  
    # _id: PyObjectId = Field(default_factory=PyObjectId) # Mongo assignes a unique ID to each document
    brand: str
    model: str
    license_plate: str
    driver_name: str
    vin: int
    year: int
    length: float 
    body_type: str
    vehicle_exterior_color: str
    wmi: str
    weight: float
    car_id: int # del 1 al 300, carID is used to connect with timeseriesModel, 
    # good if want to preload the data of 300 cars, else for easy comparision routes with carID

