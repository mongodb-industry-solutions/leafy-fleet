from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.timeseries import router as timeseries_api

import logging  


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Starting Timeseries Get Microservice...")


app.include_router(timeseries_api)