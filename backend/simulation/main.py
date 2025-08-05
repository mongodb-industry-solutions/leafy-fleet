import numpy as np  
import json  
import random  
import asyncio  
import aiohttp  
import logging  
import argparse  
from dataclasses import dataclass
from datetime import datetime
import state_manager
# Global route map  
ROUTES = {}  
  
# HTTP Session used globally  
HTTP_SESSION: aiohttp.ClientSession = None  
  
# Logging setup  
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')  
logging.basicConfig(  
    level=logging.INFO,  
    format='%(asctime)s - %(levelname)s - %(message)s',  
    handlers=[  
        logging.FileHandler("simulation.log"),  # Write logs to "simulation.log"  
        logging.StreamHandler()  # Keep logs in the console for interactive monitoring  
    ]  
) 
logger = logging.getLogger(__name__)  

  
# Constants  
constant_fuel_consumption_per_m = 0.0009  # ml/m  
constant_oil_consumption_per_m = 0.0005  # ml/m  
hostname = "http://localhost"  # Backend service base URL  
state_lock = asyncio.Lock()  
  
# Helpers for tracking simulation state  
cars_correctly_running = 10  # Example starting value  
total_cars = 10  


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
    sessions_lock: asyncio.Lock = asyncio.Lock()
    step_index: int = 0
    real_step: int = 0
    route_index: int = 0  # 0 or 1
    is_oil_leak: bool = False
    has_driver: bool = True 
    oee: int = 0
    speed_total: int = 0
    

    def __post_init__(self):
        self.route_ids = [self.car_id, self.car_id + 1] if self.car_id % 2 == 1 else [self.car_id, self.car_id - 1]

    async def update(self, move_distance_m: float, time_per_step: float):
        self.real_step+=1
        self.engine_oil_level = max(self.engine_oil_level - move_distance_m * constant_oil_consumption_per_m, 0)
        self.traveled_distance += (move_distance_m / 1000) # km 
        self.traveled_distance_since_start += move_distance_m  # m
        self.fuel_level = max(self.fuel_level - move_distance_m * constant_fuel_consumption_per_m, 0)
        self.run_time += time_per_step
        self.speed = max((move_distance_m / (time_per_step * 1000) * 3600 )+ random.uniform(-0.35, 0.25), 0) #  speed variation km/h,  non-negative
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
        self.performance_score = (self.real_step /self.steps_route)
        self.quality_score = cars_correctly_running/total_cars
        self.availability_score = min(1, self.availability_score + (random.uniform(-0.02, 0.02)))
        self.oee = self.quality_score * self.availability_score* self.performance_score


    async def to_document(self):
        async with self.sessions_lock:
            
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
                    "sessions": self.sessions if self.sessions else []  # Ensure sessions is always a list
                            }
            }
            return doc

    async def run(self):
        try:
            while True:
                if state_manager.is_paused():  
                    logger.info(f"Car {self.car_id}: Simulation paused.")  
                    while state_manager.is_paused():  
                        await asyncio.sleep(1)  # Wait for the pause state to change  
                elif state_manager.is_stopped():  
                    logger.info(f"Car {self.car_id}: Simulation stopped. Exiting.")  
                    break  # Exit the simulation loop when stopped  
                self.current_route = self.route_ids[self.route_index]
                steps, dist_per_step, time_per_step = ROUTES[self.current_route]
                self.steps_route += len(steps) # para que oee nunca se quede como 0 despues de inicio
                while self.step_index < len(steps) and state_manager.is_running():
                        
                            self.latitude, self.longitude = steps[self.step_index]
                            await self.update(dist_per_step, time_per_step)
                            
                            #will add logging here instead of print
                            #logger.info(f" Car {self.car_id} moved to ({self.latitude:.5f}, {self.longitude:.5f}) | total distance: {self.traveled_distance_since_start:.1f}m |  {self.step_index}")
                            logger.info(f"Car {self.car_id} has {self.sessions}")
                            if self.step_index % 10 == 0:
                                try:
                                    json_payload = {'coordinates': [float(self.longitude), float(self.latitude)]}  
            
                                    # Print or log the JSON payload  
                                    #print(f"Sending JSON payload: {json_payload}")  
                                    async with HTTP_SESSION.get(
                                    f"{hostname}:9004/geofences/check",
                                        json=json_payload  
                                    ) as response:
                                        if response.status == 200:
                                            data = await response.json()
                                            self.current_geozone = (
                                                f"{data['geofence_name']}"
                                                if data.get("geofence_name")
                                                else "No active geofence"
                                            )
                                        else:
                                            self.current_geozone = "Geofence check error"
                                except Exception as e:
                                    logger.warning(f" Geofence check error: {e}")
                                    self.current_geozone = "Error checking geofence"

                                #logger.info(f"Car {self.car_id} updated geozone: {self.current_geozone}")
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

                            #agregue logica chocar y checar si el carro esta parado
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
                #print(f" Car {self.car_id} finished route {self.current_route}")
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
            logger.info(f"Added  session {session_id} to car {self.car_id}. Current sessions: {self.sessions}")  

  
    async def clear_sessions(self): 
        async with self.sessions_lock: 
            """Clear all session IDs."""  
            self.sessions.clear()  
            #logger.info(f"Cleared all sessions for car {self.car_id}")  
  
  
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
        route_id = car_id  
        if route_id not in ROUTES:  
            #logger.info(f"Skipping car {car_id}: no starting route {route_id}")  
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
            sessions=[] , # Initialize with an empty list
            sessions_lock = asyncio.Lock()  
        ) 
        cars.append(car)  
    return cars  
  
  
def load_routes(filepath: str):
        global ROUTES
        with open(filepath, "r") as f:
            raw = json.load(f)
        for key, val in raw.items():
            ROUTES[int(key)] = (
                np.array([(s["lat"], s["lng"]) for s in val["steps"]], dtype=np.float32),
                float(val["distancePerStep"]),
                float(val["timePerStep"])
            )
        #print(f" Loaded {len(ROUTES)} routes")
        
  
async def shutdown_signal_handler():  
    """Handle graceful shutdown."""  
    #logger.info("Shutdown signal received, cleaning up...")  
    if HTTP_SESSION:  
        await HTTP_SESSION.close()  
        #logger.info("Session closed. Exiting.")  
  
  
async def signal_pause_handler(tasks):  
    """Handle pause signal."""  
    #logger.info("Pause signal received, pausing simulation...")  
    for task in tasks:  
        if not task.done():  
            task.cancel()  
  
  
async def signal_resume_handler(cars):  
    """Handle resume signal."""  
    #logger.info("Resume signal received, restarting simulation...")  
    tasks = [asyncio.create_task(car.run()) for car in cars]  
    return tasks  
  
  
def parse_cli_args():  
    """Parse command-line arguments."""  
    parser = argparse.ArgumentParser(description="Linux Manager for Simulation Control")  
    parser.add_argument("--start", action="store_true", help="Start the simulation")  
    parser.add_argument("--stop", action="store_true", help="pause the simulation")  
    parser.add_argument("--add-session", type=str, help="Add new session to metadata")  
    return parser.parse_args()  



tasks = []  # Global list to track simulation tasks (make this global)  
  
async def spawn_tasks(cars):  
    """Spawn asynchronous tasks for all cars."""  
    global tasks  
    tasks = [asyncio.create_task(car.run()) for car in cars]  
  
async def cancel_tasks():  
    """Cancel all simulation tasks."""  
    global tasks  
    for task in tasks:  
        task.cancel()  
    await asyncio.gather(*tasks, return_exceptions=True)  # Gather with exceptions for cancelled tasks  
    tasks.clear()  # Reset tasks list  

  
async def main():  
    args = parse_cli_args()  
  
    global HTTP_SESSION  
    HTTP_SESSION = aiohttp.ClientSession()  
  
    load_routes("processed_routes.json")  
    cars = await create_cars(num_cars=10)  
  
      
  
    if args.start:  
        if state_manager.is_stopped() or state_manager.is_paused():  
            state_manager.set_state("running")  
            logger.info("Simulation started/resumed.")  
    
            # Create tasks for all cars  
            tasks = [asyncio.create_task(car.run()) for car in cars]  
            # Concurrently run all car tasks using asyncio.gather  
            await asyncio.gather(*tasks)  

  
    elif args.stop:  
        if state_manager.is_running():  
            state_manager.set_state("paused")  
            logger.info("Simulation paused.")  
            await cancel_tasks()  # Cancel running tasks  
        elif state_manager.is_paused():  
            logger.info("Simulation already paused.")  
        elif state_manager.is_stopped():  
            logger.info("Simulation is not running.")  
 
  
    elif args.add_session:  
        # Add dynamic sessions based on the syntax: --add-session <sessionID> 10 10 10  
        session_args = args.add_session.split()  # Split input by spaces  
        if len(session_args) != 4:  # Expect sessionID + three numbers  
            logger.error("Invalid input. Please provide a session ID followed by three numbers separated by spaces (e.g., --add-session 'session123 10 20 30').")  
            return  
    
        try:  
            # Extract session ID and numbers  
            session_id = session_args[0]  
            number1, number2, number3 = map(int, session_args[1:])  
    
            # Validate input ranges (ensure numbers are between 0 and 100)  
            if not all(0 <= num <= 100 for num in (number1, number2, number3)):  
                logger.error("Numbers must be between 0 and 100. Please try again.")  
                return  
    
            # Generate session ranges  
            if number1 != 0:
                sessions_1 = list(range(1, number1 + 1)) 
            else:
                sessions_1=[]
            if number2!=0: 
                sessions_2 = list(range(101, 101 + number2))
            else:
                sessions_2=[]
            if number3!=0:   
                sessions_3 = list(range(201, 201 + number3)) 
            else:
                sessions_3=[] 
    
            all_sessions = sessions_1 + sessions_2 + sessions_3  
    
            # Add the session ID and generated sessions to cars  
            if state_manager.is_running():  
                for car in cars:
                    if car.car_id in all_sessions:  
                        if not car.sessions:  
                            car.sessions = []  # Ensure sessions list exists  
                        await car.add_session(session_id)  # Add the session ID  
            else:  
                logger.info("Cannot add sessions. Simulation is not running.")  
    
        except ValueError:  
            logger.error("Input parsing failed. Please provide valid integers for session ranges.")  
    
  
  
    await shutdown_signal_handler()  
  
  
if __name__ == "__main__":  
    asyncio.run(main())  
