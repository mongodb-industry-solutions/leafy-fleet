import aiohttp  
from pydantic_settings import BaseSettings  
from dotenv import load_dotenv
import os  

load_dotenv()

#context needed for global multithreading

HTTP_SESSION = None  # Placeholder for the global HTTP session  
geofences =[]

# Functions to safely manage HTTP_SESSION  
def set_session(session: aiohttp.ClientSession):  
    global HTTP_SESSION  
    HTTP_SESSION = session  

def get_session():  
    global HTTP_SESSION  
    if HTTP_SESSION is None:  
        raise RuntimeError("HTTP_SESSION is not initialized. Check startup_event.")  
    return HTTP_SESSION  

# Constants  
constant_fuel_consumption_per_m = 0.0009  # ml/m  
constant_oil_consumption_per_m = 0.0005  # ml/m  

cars_to_run=300

timeseries_post=os.getenv("TIMESERIES_POST_ENDPOINT")
geofences_service=os.getenv("GEOFENCES_SERVICE_ENDPOINT")
static_service=os.getenv("STATIC_SERVICE_ENDPOINT")
# Print to verify  
#print(f"Timeseries Endpoint: {timeseries_post}")  
#print(f"Geofences Endpoint: {geofences_service}")  