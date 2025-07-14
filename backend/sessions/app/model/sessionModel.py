
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

def generate_thread_id():  
    # Get the current date in DDMMYYYY format  
    date_string = datetime.utcnow().strftime("%d%m%Y")  
    # Generate a random number (you can adjust the range as needed)  
    random_number = random.randint(1000, 9999)  
    # Create the thread ID string  
    thread_id = f"thread_id{date_string}_{random_number}"  
    return thread_id 

# Nested Class for the Telemetry/Timeseries Model
class Fleet(BaseModel):  
    # _id: PyObjectId = Field(default_factory=PyObjectId) # Mongo assignes a unique ID to each document
    selectedFleets: int
    fleetNames: List[str] = Field(default_factory=list)  # List of fleet names ["Fleet A", "Fleet B"]
    fleetIDs: List[int] = Field(default_factory=list)  # List of fleet IDs [50,70,90], vechiles 0 - 50, 100 - 170, 200-290

class AgentRunDocuments(BaseModel):
    title: str = Field(default="Default Title")
    result: str = Field(default="Default Result")


class Message(BaseModel):
    message: str = Field(default="Default Message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender: str = Field(default="bot")
    messageID: int = Field(default=0)
    historicalRecommendations: AgentRunDocuments
    agentProfile: AgentRunDocuments
    queries: AgentRunDocuments
    telemetryData: AgentRunDocuments
    lastCheckpoint: AgentRunDocuments


class Agent(BaseModel):   
    agent_id: str = Field(default="DEFAULT")
    profile: str = Field(default="Default Agent Profile")
    role: str = Field(default="Expert Advisor")
    kind_of_data: str = Field(default="Specific Data")
    motive: str = Field(default="diagnose the query and provide recommendations")
    instructions: str = Field(default="Follow procedures meticulously.")
    rules: str = Field(default="Document all steps.")
    goals: str = Field(default="Provide actionable recommendations.")

class SessionModel(BaseModel):
    """
    This Model captures the session data for every instance of the demo being used
    """
    threadID: str = Field(default_factory=generate_thread_id)  # Unique thread/session ID
    vehicle_fleet: Fleet
    agentRunDocuments: AgentRunDocuments
    chatHistory: List[Message] = Field(default_factory=list) 
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    lastUsedAt: datetime = Field(default_factory=datetime.utcnow)