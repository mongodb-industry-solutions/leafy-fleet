
from random import random
import string
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
class Fleet(BaseModel):  
    # _id: PyObjectId = Field(default_factory=PyObjectId) # Mongo assignes a unique ID to each document
    selectedFleets: int
    fleetNames: List[str] = Field(default_factory=list)  # List of fleet names ["Fleet A", "Fleet B"]
    fleetIDs: List[int] = Field(default_factory=list)  # List of fleet IDs [50,70,90], vechiles 0 - 50, 100 - 170, 200-290



class Message(BaseModel):
    message: str = Field(default="Default Message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender: str = Field(default="bot")
    messageID: int = Field(default=0)

class SessionModel(BaseModel):
    """
    This Model captures the session data for every instance of the demo being used
    """
    threadID: str = Field(default_factory=lambda: f"thread_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")  # Unique thread/session ID
    vehicle_fleet: Fleet
    chatHistory: List[Message] = Field(default_factory=list) 
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    lastUsedAt: datetime = Field(default_factory=datetime.utcnow)