from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = "fleet_management_2025"
TIMESERIES_COLLECTION = "timeseries_data"

mdb_conn = MongoClient(MONGODB_URL)
db_hostpital = mdb_conn[DATABASE_NAME]
timeseries_coll = db_hostpital[TIMESERIES_COLLECTION]