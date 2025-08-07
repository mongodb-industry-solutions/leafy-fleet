import aiohttp  
  
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