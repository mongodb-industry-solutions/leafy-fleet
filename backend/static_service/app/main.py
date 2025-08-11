from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.static import router as static_api

import logging  


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"]
)

print("Starting Static Post Microservice...")


app.include_router(static_api)