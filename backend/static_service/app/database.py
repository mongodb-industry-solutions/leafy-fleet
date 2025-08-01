from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

print("Doing database connection...")

MONGODB_URL = os.getenv("MONGODB_URI")
DATABASE_NAME = "leafy_fleet"
STATIC_COLLECTION = "vehicles"


mdb_conn = MongoClient(MONGODB_URL)
db_fleet = mdb_conn[DATABASE_NAME]
vehicles_coll = db_fleet[STATIC_COLLECTION]
