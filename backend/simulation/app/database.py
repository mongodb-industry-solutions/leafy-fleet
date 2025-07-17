from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

print("Doing database connection...")

MONGODB_URL = os.getenv("MONGODB_URI")
DATABASE_NAME = "leafy_fleet"
GEOFENCE_COLLECTION = "geofences"


mdb_conn = MongoClient(MONGODB_URL)
db_fleet = mdb_conn[DATABASE_NAME]
geofences_coll = db_fleet[GEOFENCE_COLLECTION]
