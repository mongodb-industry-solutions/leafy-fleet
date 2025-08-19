import numpy as np  
import json  
import logging  

logger = logging.getLogger(__name__)  
ROUTES = {}  # Global dictionary for routes  
  
def load_routes(filepath: str):  
    """  
    Load routes into memory from a JSON file.  
    Structure:  
    ROUTES = {  
        route_id: (  
            np.array([(lat1, lng1), (lat2, lng2), ...]),  
            distancePerStep,  
            timePerStep  
        )  
    }  
    """  
    global ROUTES  
    try:  
        with open(filepath, "r") as f:  
            raw = json.load(f)  
        for key, val in raw.items():  
            ROUTES[int(key)] = (  
                np.array([(s["lat"], s["lng"]) for s in val["steps"]], dtype=np.float32),  
                float(val["distancePerStep"]),  
                float(val["timePerStep"]),  
            )  
        logger.info(f"Loaded {len(ROUTES)} routes.")  
    except FileNotFoundError:  
        logger.error(f"Routes file '{filepath}' not found.")  
    except Exception as e:  
        logger.error(f"Error loading routes: {e}")  
