import numpy as np  
import json  
import random  
import asyncio  
import aiohttp  
import logging  
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
from fastapi.middleware.cors import CORSMiddleware  
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import state_manager 
from geofence_manager import GeofenceManager  # geofence logic is here, avoiding gets to db throught the run
from routes.simulation import stop_simulation_internal, SIMULATION_TASKS
from routes.sessions import router as sessions_api  
from routes.simulation import router as simulation_api
from route_manager import load_routes, ROUTES  
from global_context import HTTP_SESSION, set_session,get_session


# FastAPI app
app = FastAPI(title="Car Simulation Microservice", version="1.0.0")

app.add_middleware(  
    CORSMiddleware,  
    allow_origins=["*"],  
    allow_credentials=True,  
    allow_methods=["*"],  
    allow_headers=["*"],  
)  


# Global route map  
  
# Global Geofences
geofence_manager = GeofenceManager()  
# HTTP Session used globally  


# Logging setup  
logging.basicConfig(  
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s - %(message)s',  
    handlers=[  
        logging.FileHandler("simulation.log"),  
        logging.StreamHandler()  
    ]  
) 
logger = logging.getLogger(__name__)  

# Constants  
constant_fuel_consumption_per_m = 0.0009  # ml/m  
constant_oil_consumption_per_m = 0.0005  # ml/m  
hostname = "http://localhost"  # Backend service base URL  
state_lock = asyncio.Lock()  
  
# Helpers for tracking simulation state  
cars_correctly_running = 300  # Updated for 300 cars
total_cars = 300  



@dataclass
class Car:
    car_id: int
    # Dynamic state, all items from timeseries model minus timestamp
    current_geozone: str
    fuel_level: float # In ml
    max_fuel_level: float # In ml
    oil_temperature: float # In Celsius
    engine_oil_level: float # In ml
    traveled_distance: float # Total distance traveled by the vehicle in km
    traveled_distance_since_start: float # Distance traveled since the start of the route in m
    availability_score: float # From 0 to 1
    run_time: float # Engine run time in s
    quality_score: float # From 0 to 1
    is_engine_running: bool
    is_crashed: bool
    current_route: int
    latitude: float 
    longitude: float 
    speed: float # Average speed of the vehicle in km/h
    average_speed: float # Average speed of the vehicle in km/h over the route
    is_moving: bool #  if the vehicle is currently moving
    
    steps_route:int =0 
    # Internal state
    performance_score: float =0 # From 0 to 1
    sessions: list = None  # List of session IDs, can be used for tracking or logging
    sessions_lock: asyncio.Lock = None  # Will be initialized in __post_init__
    step_index: int = 0
    real_step: int = 0
    route_index: int = 0  # 0 or 1
    is_oil_leak: bool = False
    has_driver: bool = True 
    oee: int = 0
    speed_total: int = 0
    

    def __post_init__(self):
        self.route_ids = [self.car_id, self.car_id + 1] if self.car_id % 2 == 1 else [self.car_id, self.car_id - 1]
        # Initialize sessions list and lock properly
        if self.sessions is None:
            self.sessions = []
        if self.sessions_lock is None:
            self.sessions_lock = asyncio.Lock()

    async def update(self, move_distance_m: float, time_per_step: float):
        self.real_step+=1
        self.engine_oil_level = max(self.engine_oil_level - move_distance_m * constant_oil_consumption_per_m, 0)
        self.traveled_distance += (move_distance_m ) # km 
        self.traveled_distance_since_start += move_distance_m  # m
        self.fuel_level = max(self.fuel_level - move_distance_m * constant_fuel_consumption_per_m, 0)
        self.run_time += time_per_step
        raw_speed = (move_distance_m / time_per_step) * 3600 + random.uniform(-0.35, 0.25)  
        logger.info(f"Raw Speed Calculation: {raw_speed} km/h")  
        self.speed = min(max(raw_speed, 0), 180)  
        self.speed_total+=self.speed
        self.average_speed = self.speed_total / self.real_step
        
        
        if (random.random() < 0.001):  # 0.1% chance of crash
            self.is_crashed = True
            self.is_engine_running = False
            logger.warning(f" Car {self.car_id} has crashed!")
            self.speed = 0
            await decrement_cars_correctly_running()  
        if self.fuel_level <= 0:
            self.is_engine_running = False
            self.speed = 0
            logger.warning(f" Car {self.car_id} has run out of fuel!")
            await decrement_cars_correctly_running()
        if self.engine_oil_level <= 0:
            self.is_oil_leak = True
            self.is_engine_running = False
            logger.warning(f" Car {self.car_id} has an oil leak!")
            await decrement_cars_correctly_running()
        self.is_moving = self.speed > 0
        self.performance_score = (self.real_step /self.steps_route) if self.steps_route > 0 else 0
        self.quality_score = cars_correctly_running/total_cars
        self.availability_score = min(1, max(0, self.availability_score + (random.uniform(-0.02, 0.02))))
        self.oee = self.quality_score * self.availability_score * self.performance_score

    async def get_sessions(self):
        """Safely get a copy of current sessions."""
        async with self.sessions_lock:
            return self.sessions.copy() if self.sessions else []

    async def to_document(self):
        # Get a safe copy of sessions
        sessions_copy = await self.get_sessions()
        
        doc = {
            "car_id": self.car_id,
            "fuel_level": float(round(self.fuel_level, 1)),
            "engine_oil_level": float(round(self.engine_oil_level, 1)),
            "traveled_distance": float(round(self.traveled_distance, 4)),
            "run_time": float(self.run_time),
            "performance_score": float(self.performance_score),
            "quality_score": float(self.quality_score),
            "availability_score": float(self.availability_score),
            "max_fuel_level": float(self.max_fuel_level),
            "oee": float(self.oee),
            "oil_temperature": float(self.oil_temperature),
            "is_oil_leak": self.is_oil_leak,
            "is_engine_running": self.is_engine_running,
            "is_crashed": self.is_crashed,
            "current_route": self.current_route,
            "speed": float(round(self.speed, 2)),
            "average_speed": float(round(self.average_speed, 2)),
            "is_moving": self.is_moving,
            "current_geozone": self.current_geozone,
            "coordinates": {
            "type": "Point",
            "coordinates": [float(round(self.longitude, 7)), float(round(self.latitude, 7))]
            },
            "metadata": {
                "sessions": sessions_copy
                        }
        }
        return doc

    async def run(self, session: aiohttp.ClientSession):
        try:
            while True:
                if session is None:  
                    raise RuntimeError("HTTP_SESSION is not initialized. Check startup_event.")  

                if state_manager.is_paused():  
                    logger.info(f"Car {self.car_id}: Simulation paused.")  
                    while state_manager.is_paused():  
                        await asyncio.sleep(5)  # Wait for the pause state to change 10 seconds, will stop completly after 15 minutes. 
                elif state_manager.is_stopped():  
                    logger.info(f"Car {self.car_id}: Simulation stopped. Exiting.")  
                    break  # Exit the simulation loop when stopped  
                
                self.current_route = self.route_ids[self.route_index]
                if self.current_route not in ROUTES:
                    logger.warning(f"Car {self.car_id}: Route {self.current_route} not found, skipping")
                    await asyncio.sleep(10)
                    continue
                    
                steps, dist_per_step, time_per_step = ROUTES[self.current_route]
                self.steps_route += len(steps) # para que oee nunca se quede como 0 despues de inicio
                
                while self.step_index < len(steps) and state_manager.is_running():
                    self.latitude, self.longitude = steps[self.step_index]
                    await self.update(dist_per_step, time_per_step)
                    # Access sessions with proper locking (reduced logging frequency)
                    if self.step_index % 50 == 0:  # Log less frequently
                        current_sessions = await self.get_sessions()
                        if current_sessions:  # Only log if there are sessions
                            logger.info(f"Car {self.car_id} has {current_sessions}")
                    if self.step_index % 10 == 0:
                        try:
                            self.current_geozone = geofence_manager.check_point_in_geofences(self.longitude, self.latitude)  
                            logger.info(f"Car {self.car_id}: Current geozone: {self.current_geozone}")
                        except Exception as e:
                            logger.warning(f" Geofence check error: {e}")
                            self.current_geozone = "Error checking geofence"

                    # Send timeseries data every step
                    try:
                        document = await self.to_document()  
                        await session.post(
                            f"{hostname}:9002/timeseries",
                            json=document
                        )
                    except Exception as e:
                        logger.warning(f" Error sending timeseries for Car {self.car_id}: {e}")
                    
                    self.step_index += 1

                    # Handle car failures
                    if self.is_engine_running==False:
                        logger.warning(f" Car {self.car_id} is not running, skipping step {self.step_index}")
                        await asyncio.sleep(60) # Wait for a minute before next step
                        await increment_cars_correctly_running()  
                        if self.is_crashed:
                            self.is_crashed = False  # Reset crash state after some time
                            self.is_engine_running = True  # Restart the engine after a crash
                        if self.fuel_level <= 0:
                            self.fuel_level = self.max_fuel_level
                            self.is_engine_running = True  # Refuel and restart the engine
                        if self.engine_oil_level <= 0:
                            self.engine_oil_level = 1000  # Reset oil level after a leak
                            self.is_oil_leak = False  
                        continue
                    await asyncio.sleep(time_per_step)
                
                # Finished route, switch to next one
                await asyncio.sleep(10)
                self.route_index = 1 - self.route_index
                self.step_index = 0
        except asyncio.CancelledError:  
            logger.info(f"Car {self.car_id} simulation task cancelled.")
        except Exception as e:  
            logger.error(f"Car {self.car_id}: Unexpected error occurred: {e}")       
    
    async def add_session(self, session_id: str):  
        async with self.sessions_lock:
            """Append a new session ID to metadata['sessions']."""      
            if not self.sessions:      
                self.sessions = []      
        
            self.sessions.append(session_id)      
            #logger.info(f"Added session {session_id} to car {self.car_id}. Current sessions: {self.sessions}")  

    async def clear_sessions(self): 
        async with self.sessions_lock: 
            """Clear all session IDs."""  
            if self.sessions:
                self.sessions.clear()  
            #logger.info(f"Cleared all sessions for car {self.car_id}")  

# State tracking functions
async def decrement_cars_correctly_running():  
    async with state_lock:  
        global cars_correctly_running  
        cars_correctly_running -= 1  

async def increment_cars_correctly_running():  
    async with state_lock:  
        global cars_correctly_running  
        cars_correctly_running += 1  


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize the microservice."""
    session = aiohttp.ClientSession()  
    set_session(session)

    load_routes("processed_routes.json")
    try:  
        await geofence_manager.load_geofences("http://localhost:9004/geofences",session) 

  # Load geofences from an API  
    except Exception as e:  
        logger.error(f"Failed to load geofences from API during startup: {str(e)}")
    logger.info("Car Simulation Microservice started")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    
    await stop_simulation_internal()
    session = get_session()  
    if session:
        await session.close()  
    set_session(None)
    logger.info("Car Simulation Microservice stopped")

app.include_router(sessions_api, prefix="/sessions")  
app.include_router(simulation_api, prefix="/simulation")  

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)