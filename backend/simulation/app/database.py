from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging
load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Doing database connection...")

MONGODB_URL = os.getenv("MONGODB_URI")
DATABASE_NAME = "leafy_fleet"
GEOFENCE_COLLECTION = "geofences"
CARS_COLLECTION = "vehicles"

mdb_conn = MongoClient(MONGODB_URL)
db_fleet = mdb_conn[DATABASE_NAME]
geofences_coll = db_fleet[GEOFENCE_COLLECTION]
vehicles_coll = db_fleet[CARS_COLLECTION]