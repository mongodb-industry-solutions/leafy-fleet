import string
from pydantic import BaseModel, Field
from typing import  List
from typing_extensions import Annotated

from pydantic.functional_validators import BeforeValidator
from datetime import datetime
from typing import Optional 

PyObjectId = Annotated[str, BeforeValidator(str)]

# Nested Class for the Telemetry/Timeseries Model
class Fleet(BaseModel):  
    # _id: PyObjectId = Field(default_factory=PyObjectId) # Mongo assignes a unique ID to each document
    selected_fleets: int
    fleet_names: List[str] = Field(default_factory=list)  # List of fleet names ["Fleet A", "Fleet B"
    fleet_size: List[int] = Field(default_factory=list)  # List of fleet IDs [50,70,90], vechiles 0 - 50, 100 - 170, 200-290
    attribute_list: List[List[str]] = Field(default_factory=list)  # List of attributes for each fleet [["attribute1", "attribute2"], ["attribute3", "attribute4"]]
class Message(BaseModel):
    message: str = Field(default="any question") #text
    index: int = Field(default=0) #from 0 to n, to kniow the order of the messages. in theory should not be needed if appended to list in order, but just in case
    sender: str = Field(default="bot") #bot or user
    completed: bool = Field(default=True) #if the message is completed or not, to know if the bot is still typing
class MessageEntry(BaseModel):
    thread_id: PyObjectId = Field(default_factory=PyObjectId)  # Unique identifier for the message thread
    message: str = Field(..., description="The content of the message")
    sender: str = Field(..., description="The sender of the message (e.g., 'user' or 'bot')")
    completed: bool = Field(default=True, description="Indicates if the message is completed or not")

class SessionModel(BaseModel):
    """
    This Model captures the session data for every instance of the demo being used
    """
    vehicle_fleet: Fleet
    chat_history: List[Message] = Field(default_factory=list) 
    last_used_at: Optional[datetime] = None  