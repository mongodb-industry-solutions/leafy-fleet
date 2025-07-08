from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

print("Doing database connection...")

MONGODB_URL = os.getenv("MONGODB_URI")
DATABASE_NAME = "leafy_fleet"
TIMESERIES_COLLECTION = "vehicleTelemetry"


mdb_conn = MongoClient(MONGODB_URL)
db_fleet = mdb_conn[DATABASE_NAME]
timeseries_coll = db_fleet[TIMESERIES_COLLECTION]
