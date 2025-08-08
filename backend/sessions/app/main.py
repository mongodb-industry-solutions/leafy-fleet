from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.sessions import router as sessions_api
from routes.messages import router as messages_api
import logging  


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"]
)

print("Starting Sessions Microservice...")


app.include_router(sessions_api)
app.include_router(messages_api)