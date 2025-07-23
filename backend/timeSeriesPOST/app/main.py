from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.timeseries import router as timeseries_api

import logging  


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"]
)

print("Starting Timeseries Post Microservice...")


app.include_router(timeseries_api)