from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.geofences import router as geofences_api


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"]
)

print("Starting Simulation Geofence Location Microservice...")


app.include_router(geofences_api)
