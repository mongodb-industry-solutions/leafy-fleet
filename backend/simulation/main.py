import numpy as np  
import json  
import random  
import asyncio  
import aiohttp  
import logging  
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import app.state_manager
from geofence_manager import GeofenceManager  # geofence logic is here, avoiding gets to db throught the run

# FastAPI app
app = FastAPI(title="Car Simulation Microservice", version="1.0.0")

# Global route map  
ROUTES = {}  
  
# Global Geofences
geofence_manager = GeofenceManager()  

# HTTP Session used globally  
HTTP_SESSION: aiohttp.ClientSession = None  

# Global car registry and simulation control
GLOBAL_CARS: Dict[int, 'Car'] = {}  # Dictionary: car_id -> Car instance
SIMULATION_TASKS: List[asyncio.Task] = []  # Active simulation tasks
CARS_LOCK = asyncio.Lock()  # Lock for accessing global cars registry

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

# Pydantic models for API
class SessionRequest(BaseModel):
    session_id: str
    range1: int  # 0-100: cars 1 to range1
    range2: int  # 0-100: cars 101 to 101+range2-1  
    range3: int  # 0-100: cars 201 to 201+range3-1

class SimulationStatus(BaseModel):
    state: str
    total_cars: int
    running_cars: int
    registered_cars: int


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
        self.traveled_distance += (move_distance_m / 1000) # km 
        self.traveled_distance_since_start += move_distance_m  # m
        self.fuel_level = max(self.fuel_level - move_distance_m * constant_fuel_consumption_per_m, 0)
        self.run_time += time_per_step
        self.speed = max((self.traveled_distance / (time_per_step) * 3600 )+ random.uniform(-0.35, 0.25), 0) #  speed variation km/h,  non-negative
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

    async def run(self):
        try:
            while True:
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
                        await HTTP_SESSION.post(
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


# Car management functions
async def register_car(car):
    """Register a car in the global registry."""
    async with CARS_LOCK:
        GLOBAL_CARS[car.car_id] = car


async def get_car_by_id(car_id):
    """Get a car from the global registry by ID."""
    async with CARS_LOCK:
        return GLOBAL_CARS.get(car_id)

async def get_all_cars():
    """Get all cars from the global registry."""
    async with CARS_LOCK:
        return list(GLOBAL_CARS.values())

async def clear_all_cars():
    """Clear all cars from the global registry."""
    async with CARS_LOCK:
        GLOBAL_CARS.clear()

# State tracking functions
async def decrement_cars_correctly_running():  
    async with state_lock:  
        global cars_correctly_running  
        cars_correctly_running -= 1  

async def increment_cars_correctly_running():  
    async with state_lock:  
        global cars_correctly_running  
        cars_correctly_running += 1  

async def create_cars(num_cars: int):  
    """Initialize cars for simulation."""  
    cars = []  
    for car_id in range(1, num_cars + 1):  
        route_id = car_id % len(ROUTES) + 1 if ROUTES else car_id  # Cycle through available routes
        if route_id not in ROUTES:  
            logger.warning(f"Skipping car {car_id}: no route {route_id} available")
            continue  
  
        lat, lng = ROUTES[route_id][0][0]  
        car = Car(
            car_id=car_id,
            current_route=route_id,
            latitude=lat,
            longitude=lng,
            traveled_distance=random.uniform(0, 10000),
            traveled_distance_since_start=0.0,
            fuel_level=random.uniform(1000, 5000),
            max_fuel_level=5000.0,
            oil_temperature=random.uniform(70, 120),
            engine_oil_level=random.uniform(500, 2000),
            performance_score=random.uniform(80, 100),
            availability_score=random.uniform(80, 100),
            run_time=0.0,
            quality_score=1.0,
            is_oil_leak=False,
            is_engine_running=True,
            is_crashed=False,
            speed=0.0,
            average_speed=0.0,
            is_moving=False,
            current_geozone="No Geofence found",
            sessions=[]  # Initialize with an empty list
        ) 
        cars.append(car)
        await register_car(car)
    return cars  


def load_routes(filepath: str):
    global ROUTES
    try:
        with open(filepath, "r") as f:
            raw = json.load(f)
        for key, val in raw.items():
            ROUTES[int(key)] = (
                np.array([(s["lat"], s["lng"]) for s in val["steps"]], dtype=np.float32),
                float(val["distancePerStep"]),
                float(val["timePerStep"])
            )
        logger.info(f"Loaded {len(ROUTES)} routes")
    except FileNotFoundError:
        logger.error(f"Routes file {filepath} not found")
    except Exception as e:
        logger.error(f"Error loading routes: {e}")

async def pause_simulation():
    """Pause the simulation."""
    if not state_manager.is_running():
        raise HTTPException(status_code=400, detail="Simulation is not running")
    
    state_manager.set_state("paused")
    logger.info("Simulation paused")

async def resume_simulation():
    """Resume the paused simulation."""
    if not state_manager.is_paused():
        raise HTTPException(status_code=400, detail="Simulation is not paused")
    
    state_manager.set_state("running")
    logger.info("Simulation resumed")

async def stop_simulation_internal():
    """Internal function to stop simulation and clean up."""
    global SIMULATION_TASKS
    
    # Set state to stopped
    state_manager.set_state("stopped")
    
    # Cancel all tasks
    for task in SIMULATION_TASKS:
        if not task.done():
            task.cancel()
    
    # Wait for tasks to complete with timeout
    if SIMULATION_TASKS:
        try:
            await asyncio.wait_for(
                asyncio.gather(*SIMULATION_TASKS, return_exceptions=True),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            logger.warning("Some tasks did not complete within timeout")
    
    SIMULATION_TASKS.clear()
    await clear_all_cars()

async def stop_simulation():
    """Stop the simulation and clean up all resources."""
    if state_manager.is_stopped():
        raise HTTPException(status_code=400, detail="Simulation is already stopped")
    
    await stop_simulation_internal()
    logger.info("Simulation stopped and cleaned up")

# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize the microservice."""
    global HTTP_SESSION
    HTTP_SESSION = aiohttp.ClientSession()
    load_routes("processed_routes.json")
    try:  
        await geofence_manager.load_geofences("http://localhost:9004/geofences",HTTP_SESSION)  
  # Load geofences from an API  
    except Exception as e:  
        logger.error(f"Failed to load geofences from API during startup: {str(e)}")
    logger.info("Car Simulation Microservice started")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global HTTP_SESSION
    await stop_simulation_internal()
    if HTTP_SESSION:
        await HTTP_SESSION.close()
    logger.info("Car Simulation Microservice stopped")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Car Simulation Microservice is running"}

@app.get("/status", response_model=SimulationStatus)
async def get_status():
    """Get current simulation status."""
    cars = await get_all_cars()
    return SimulationStatus(
        state=state_manager.get_state(),
        total_cars=total_cars,
        running_cars=cars_correctly_running,
        registered_cars=len(cars)
    )
    
@app.post("/start/{num_cars}")
async def start_simulation_endpoint(num_cars: int):
    """Start simulation with specified number of cars."""
    if num_cars <= 0:
        raise HTTPException(status_code=400, detail="Number of cars must be greater than 0")
    
    if num_cars > 300: #could change in future, just need more routes in advance!
        raise HTTPException(status_code=400, detail="Maximum 300 cars allowed")
    
    if state_manager.is_running():
        raise HTTPException(status_code=400, detail="Simulation is already running")
    
    # Clear any existing cars and tasks
    await stop_simulation_internal()
    
    # Create cars
    cars = await create_cars(num_cars=num_cars)
    
    # Update global counters
    global total_cars, cars_correctly_running
    total_cars = len(cars)
    cars_correctly_running = total_cars
    
    # Start simulation
    state_manager.set_state("running")
    global SIMULATION_TASKS
    SIMULATION_TASKS = [asyncio.create_task(car.run()) for car in cars]
    
    logger.info(f"Started simulation with {len(cars)} cars")
    
    return {
        "message": f"Simulation started successfully",
        "cars_created": len(cars),
        "cars_correctly_running": cars_correctly_running,
        "total_cars": total_cars,
        "action": "start"
    }

@app.post("/pause")
async def pause_simulation_endpoint():
    """Pause the simulation."""
    if not state_manager.is_running():
        raise HTTPException(status_code=400, detail="Simulation is not running")
    
    state_manager.set_state("paused")
    logger.info("Simulation paused")
    return {"message": "Simulation paused", "action": "pause"}

@app.post("/resume")
async def resume_simulation_endpoint():
    """Resume the paused simulation."""
    if not state_manager.is_paused():
        raise HTTPException(status_code=400, detail="Simulation is not paused")
    
    state_manager.set_state("running")
    logger.info("Simulation resumed")
    return {"message": "Simulation resumed", "action": "resume"}

@app.post("/stop")
async def stop_simulation_endpoint(background_tasks: BackgroundTasks):
    """Stop the simulation and clean up all resources."""
    if state_manager.is_stopped():
        raise HTTPException(status_code=400, detail="Simulation is already stopped")
    
    # Run stop in background to avoid blocking the API response
    background_tasks.add_task(stop_simulation_internal)
    return {"message": "Simulation stopping...", "action": "stop"}

@app.post("/sessions")
async def add_sessions(request: SessionRequest):
    """Add session to cars based on three ranges: 1-x1, 101-x2, 201-x3."""
    if not state_manager.is_running():
        raise HTTPException(status_code=400, detail="Simulation is not running")
    
    # Validate ranges
    if not all(0 <= x <= 100 for x in [request.range1, request.range2, request.range3]):
        raise HTTPException(status_code=400, detail="All ranges must be between 0 and 100")
    
    # Generate car ID lists based on ranges
    car_ids = []
    
    # Range 1: cars 1 to range1 (if range1 > 0)
    if request.range1 > 0:
        car_ids.extend(list(range(1, request.range1 + 1)))
    
    # Range 2: cars 101 to 101+range2-1 (if range2 > 0)  
    if request.range2 > 0:
        car_ids.extend(list(range(101, 101 + request.range2)))
    
    # Range 3: cars 201 to 201+range3-1 (if range3 > 0)
    if request.range3 > 0:
        car_ids.extend(list(range(201, 201 + request.range3)))
    
    if not car_ids:
        return {
            "message": "No cars selected (all ranges are 0)",
            "session_id": request.session_id,
            "cars_updated": 0,
            "ranges": {
                "range1": f"1-{request.range1}" if request.range1 > 0 else "none",
                "range2": f"101-{100 + request.range2}" if request.range2 > 0 else "none", 
                "range3": f"201-{200 + request.range3}" if request.range3 > 0 else "none"
            }
        }
    
    # Add sessions to cars
    cars_updated = 0
    cars_not_found = []
    
    for car_id in car_ids:
        car = await get_car_by_id(car_id)
        if car:
            await car.add_session(request.session_id)
            cars_updated += 1
        else:
            cars_not_found.append(car_id)
    
    result = {
        "message": f"Session {request.session_id} added to {cars_updated} cars",
        "session_id": request.session_id,
        "cars_updated": cars_updated,
        "total_cars_requested": len(car_ids),
        "ranges": {
            "range1": f"1-{request.range1}" if request.range1 > 0 else "none",
            "range2": f"101-{100 + request.range2}" if request.range2 > 0 else "none",
            "range3": f"201-{200 + request.range3}" if request.range3 > 0 else "none"
        }
    }
    
    if cars_not_found:
        result["cars_not_found"] = cars_not_found
    
    return result

@app.delete("/sessions/{car_id}")
async def clear_car_sessions(car_id: int):
    """Clear all sessions from a specific car."""
    if not state_manager.is_running():
        raise HTTPException(status_code=400, detail="Simulation is not running")
    
    car = await get_car_by_id(car_id)
    if not car:
        raise HTTPException(status_code=404, detail=f"Car {car_id} not found")
    
    await car.clear_sessions()
    return {"message": f"Sessions cleared for car {car_id}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)