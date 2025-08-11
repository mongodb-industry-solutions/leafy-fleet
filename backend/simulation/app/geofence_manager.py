from shapely.geometry import shape, Point  
import logging
import aiohttp  
from global_context import geofences 
logger = logging.getLogger(__name__)  

class GeofenceManager:  
    def __init__(self):  
        self.geofences = []  # Store geofences as a list  
        
    async def load_geofences(self, url: str, session: aiohttp.ClientSession):  
        """  
        Load geofences directly into memory using the provided HTTP session.  
        Args:  
            url (str): The endpoint to fetch geofences from.  
            session (aiohttp.ClientSession): The session to use for the HTTP request.  

        """ 
        global geofences 
        try:  
            async with session.get(url) as response:  
                if response.status == 200:  
                    data = await response.json()  # Parse the response as JSON  
                    geofences = []  # Clear any existing geofences  
  
                    # Process fetched geofences  
                    for geofence in data.get("geofences", []):  
                        polygon = shape(geofence["geometry"])  # Convert geometry to shapely polygons  
                        geofences.append({  
                            "name": geofence["name"],  
                            "geometry": polygon  
                        })  
  
                    logger.info(f"Loaded {len(geofences)} geofences into memory from API.")  
                else:  
                    logger.error(f"Failed to fetch geofences. HTTP status: {response.status}")  
        except Exception as e:  
            logger.error(f"Error loading geofences from API: {str(e)}")  


    def check_point_in_geofences(self, longitude: float, latitude: float) -> str:  
        """  
        Check if the given coordinates are inside any loaded geofence.  
  
        Args:  
            longitude (float): The longitude of the point.  
            latitude (float): The latitude of the point.  
  
        Returns:  
            str: The name of the geofence if the point is inside one, otherwise "No active geofence".  
        """  
        point = Point(longitude, latitude)  # Create a point from the car's position  
        global geofences
        for geofence in geofences:  
            if geofence["geometry"].contains(point):  # Check if the point is within the polygon  
                return geofence["name"]  # Return the name of the matching geofence  
  
        return "No active geofence"  

