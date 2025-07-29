from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

print("Doing database connection...")

MONGODB_URL = os.getenv("MONGODB_URI")
DATABASE_NAME = "leafy_fleet"
SESSIONS_COLLECTION = "sessions"


mdb_conn = MongoClient(MONGODB_URL)
db_fleet = mdb_conn[DATABASE_NAME]
sessions_coll = db_fleet[SESSIONS_COLLECTION]
