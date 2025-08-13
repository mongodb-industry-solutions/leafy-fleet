import numpy as np  
import json  
import random  
import asyncio  
import aiohttp  
import logging  
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from fastapi.middleware.cors import CORSMiddleware  
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic_settings import BaseSettings  
import uvicorn
import state_manager 
from geofence_manager import GeofenceManager  # geofence logic is here, avoiding gets to db throught the run
from routes.simulation import stop_simulation_internal
from routes.sessions import router as sessions_api  
from routes.simulation import router as simulation_api
from route_manager import load_routes, ROUTES  
from global_context import  set_session,get_session, constant_fuel_consumption_per_m, constant_oil_consumption_per_m, geofences_service, timeseries_post, HTTP_SESSION

# FastAPI app
app = FastAPI(title="Car Simulation Microservice", version="1.0.0")
import os  
app.add_middleware(  
    CORSMiddleware,  
    allow_origins=["*"],  
    allow_credentials=True,  
    allow_methods=["*"],  
    allow_headers=["*"],  
)  



  
# Global Geofences
geofence_manager = GeofenceManager()  
# telemetry global time for history  
latest_telemetry= datetime.now().timestamp()-3600

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


state_lock = asyncio.Lock()  
  
# Helpers for tracking simulation state  
cars_correctly_running = 300  # Updated for 300 cars
total_cars = 300  
cdt = timezone(timedelta(hours=-5))

def convert_numpy_types(obj):
        """Convert numpy types to native Python types for JSON serialization."""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(item) for item in obj]
        return obj



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
    is_historic: bool  #useful to know if should skip asyncio or not.
    #brand : str
    #body_type: str
    #license_plate: str

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
        self.speed = max(((move_distance_m / 1000) / (time_per_step / 3600)), 0) + random.uniform(-4.35, 4.25) #  speed variation km/h,  non-negative
        self.speed = max(self.speed, 0)  # Ensure non-negative

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

                if  state_manager.is_paused():  
                    logger.info(f"Car {self.car_id}: Simulation paused.")  
                    while  state_manager.is_paused():  
                        await asyncio.sleep(5)  # Wait for the pause state to change 10 seconds, will stop completly after 15 minutes. 
                elif  state_manager.is_stopped():  
                    logger.info(f"Car {self.car_id}: Simulation stopped. Exiting.")  
                    break  # Exit the simulation loop when stopped  
                
                self.current_route = self.route_ids[self.route_index]
                if self.current_route not in ROUTES:
                    logger.warning(f"Car {self.car_id}: Route {self.current_route} not found, skipping")
                    await asyncio.sleep(10)
                    continue
                    
                steps, dist_per_step, time_per_step = ROUTES[self.current_route]
                self.steps_route += len(steps) # para que oee nunca se quede como 0 despues de inicio
                
                while self.step_index < len(steps) and  state_manager.is_running():
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
                            f"{timeseries_post}:9002/timeseries",
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

    async def update_history(self, move_distance_m: float, time_per_step: float):
        self.real_step+=1
        self.engine_oil_level = max(self.engine_oil_level - move_distance_m * constant_oil_consumption_per_m, 0)
        self.traveled_distance += (move_distance_m ) # km 
        self.traveled_distance_since_start += move_distance_m  # m
        self.fuel_level = max(self.fuel_level - move_distance_m * constant_fuel_consumption_per_m, 0)
        self.run_time += time_per_step
        self.speed = max(((move_distance_m / 1000) / (time_per_step / 3600)), 0) + random.uniform(-4.35, 4.25) #  speed variation km/h,  non-negative
        self.speed = max(self.speed, 0)  # Ensure non-negative

        self.average_speed = self.speed_total / self.real_step
        self.is_moving = self.speed > 0
        self.performance_score = (self.real_step /self.steps_route) if self.steps_route > 0 else 0
        self.quality_score = cars_correctly_running/total_cars
        self.availability_score = min(1, max(0, self.availability_score + (random.uniform(-0.02, 0.02))))
        self.oee = self.quality_score * self.availability_score * self.performance_score    
    
    async def run_history(self, session):
        """Run historic simulation for this car - emulates run() logic but for past data."""
        logger.info(f"Car {self.car_id}: Starting history simulation")
        
        try:
            
            # Calculate target steps for 1 hour of simulation
            target_duration_seconds = 3600  # 1 hour
            total_steps_processed = 0
            batch_data = []
            batch_size = 350  # Larger batch for efficiency

            start_time = datetime.now(cdt)
            counter = start_time.timestamp() - target_duration_seconds
            # Initialize route switching variables (same as run function)
            route_step_index = 0
            route_index = 0  # Start with first route (0 or 1)
            
            while counter < start_time.timestamp():
                # Get current route (same logic as run function)
                self.current_route = self.route_ids[route_index]
                
                if self.current_route not in ROUTES:
                    logger.warning(f"Car {self.car_id}: Route {self.current_route} not found in history, skipping")
                    break
                    
                steps, dist_per_step, time_per_step = ROUTES[self.current_route]
                self.steps_route = len(steps)  # Update for performance calculation
                
                #logger.info(f"Car {self.car_id}: History processing route {self.current_route} with {len(steps)} steps")
                
                # Process steps in current route (same logic as run function)
                while route_step_index < len(steps) and counter < start_time.timestamp():
                    try:
                        # Update position (same as run function)
                        self.latitude, self.longitude = steps[route_step_index]
                        
                        # Update car state using history method
                        await self.update_history(dist_per_step, time_per_step)
                        
                        # Check geofence every 10 steps (same as run function)
                        if route_step_index % 10 == 0:
                            try:
                                self.current_geozone = geofence_manager.check_point_in_geofences(self.longitude, self.latitude)  
                            except Exception as e:
                                logger.warning(f"Car {self.car_id}: Geofence check error in history: {e}")
                                self.current_geozone = "Error checking geofence"
                        
                        # Create document with historical timestamp
                        data_point = await self.to_document()
                        counter+=time_per_step
                        # Set timestamp to simulate past data (going backwards from current time)
                        historical_timestamp = counter
                        local_dt = datetime.fromtimestamp(historical_timestamp, tz=cdt)
                        utc_dt = local_dt.astimezone(timezone.utc)
                        data_point["timestamp"] = utc_dt.isoformat()

                        
                        batch_data.append(data_point)
                        route_step_index += 1
                        total_steps_processed += 1
                        
                        # Send batch when full (optimized for history)
                        if len(batch_data) >= batch_size:
                            success = await self._send_historic_batch(session, batch_data)
                            if success:
                                logger.info(f"Car {self.car_id}: Sent history batch of {len(batch_data)} records")
                                batch_data = []
                            else:
                                logger.error(f"Car {self.car_id}: Failed to send history batch - stopping history simulation")
                                return  # Exit gracefully instead of breaking inner loop
                        
                        # Handle car failures in history (same logic as run function, but no sleep)
                        if not self.is_engine_running:
                            logger.info(f"Car {self.car_id}: Engine stopped in history at step {route_step_index}")
                            # Reset conditions immediately in history (no waiting)
                            if self.is_crashed:
                                self.is_crashed = False
                                self.is_engine_running = True
                            if self.fuel_level <= 0:
                                self.fuel_level = self.max_fuel_level
                                self.is_engine_running = True
                            if self.engine_oil_level <= 0:
                                self.engine_oil_level = 1000
                                self.is_oil_leak = False
                                self.is_engine_running = True
                            
                    except Exception as e:
                        logger.error(f"Car {self.car_id}: Error processing history step {route_step_index}: {e}")
                        continue
                
                # Finished current route - switch to next route (same as run function)
                route_index = 1 - route_index  # Switch between 0 and 1
                route_step_index = 0  # Reset step index for new route
                
                logger.info(f"Car {self.car_id}: Switched to route {self.route_ids[route_index]} for history")
            
            # Send remaining batch data
            if batch_data:
                success = await self._send_historic_batch(session, batch_data)
                if success:
                    logger.info(f"Car {self.car_id}: Sent final history batch of {len(batch_data)} records")
                else:
                    logger.warning(f"Car {self.car_id}: Failed to send final history batch - simulation may have been stopped")
            
            elapsed_time = (datetime.now(cdt) - start_time).total_seconds()
            logger.info(f"Car {self.car_id}: Completed history simulation - {total_steps_processed} steps in {elapsed_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Car {self.car_id}: Unexpected error during history simulation: {e}")
            import traceback
            logger.error(f"Car {self.car_id}: History traceback: {traceback.format_exc()}")
    
    async def _send_historic_batch(self, session, batch_data):
        """Send batch data to historic API endpoint."""
        try:
            # Check if session is closed before attempting request
            if session.closed:
                logger.warning(f"Car {self.car_id}: Session is closed, cannot send batch")
                return False
                
            # Debug: Log the request details
            logger.info(f"Car {self.car_id}: Preparing to send {len(batch_data)} records to /historic-batch")
            
            # Convert numpy types to regular Python types
            formatted_data = convert_numpy_types(batch_data)
            
            # Debug: Log first item to check format
            if formatted_data:
                logger.debug(f"Car {self.car_id}: Sample coordinates: {formatted_data[0].get('coordinates', 'None')}")
            
            # Make the API call
            response = await session.post(
                f"{timeseries_post}:9002/historic-batch",
                json=formatted_data,
                headers={"Content-Type": "application/json"}
            )
            # Debug: Log response details            
            if response.status == 201:
                response_text = await response.text()
                logger.info(f"Car {self.car_id}: API success: {response_text}")
                return True
            else:
                response_text = await response.text()
                logger.error(f"Car {self.car_id}: API error {response.status}: {response_text}")
                return False
                
        except RuntimeError as e:
            if "Session is closed" in str(e):
                logger.warning(f"Car {self.car_id}: HTTP session was closed - simulation likely stopped")
                return False
            else:
                logger.error(f"Car {self.car_id}: Runtime error sending batch: {e}")
                return False
        except Exception as e:
            logger.error(f"Car {self.car_id}: Error sending batch to API: {e}")
            import traceback
            logger.error(f"Car {self.car_id}: API call traceback: {traceback.format_exc()}")
            return False
    
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
    global latest_telemetry 
    latest_telemetry= datetime.now(cdt).timestamp()-3600
    load_routes("processed_routes.json") # if want to try with 10 cars, use smaller_sim_routes/processed_routes_10.json
    try:  
        
        await geofence_manager.load_geofences(f"{geofences_service}:9004/geofences",session) 

  # Load geofences from an API  
    except Exception as e:  
        logger.error(f"Failed to load geofences from API during startup: {str(e)}")
    logger.info("Car Simulation Microservice started")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    
    # Stop simulation first (this will handle task cleanup)
    try:
        await stop_simulation_internal()
    except Exception as e:
        logger.error(f"Error during simulation cleanup: {e}")
    
    # Close session after all tasks are done
    session = get_session()  
    if session and not session.closed:
        await session.close()  
    set_session(None)
    
    logger.info("Car Simulation Microservice stopped")

app.include_router(sessions_api, prefix="")  
app.include_router(simulation_api, prefix="/simulation")  

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9006)

