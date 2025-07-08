from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.timeseries import router as timeseries_api

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"]
)

app.include_router(timeseries_api, prefix="/v1")