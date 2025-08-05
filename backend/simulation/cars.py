import numpy as np
import json
from dataclasses import dataclass
from datetime import datetime
import random
import asyncio

"""  
this class will be used to create the cars, it will be used in the simulation everytime it wakes up.
"""  

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
        print("car updated")


    def to_document(self):
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
        while True:
            
            self.current_route = self.route_ids[self.route_index]
            steps, dist_per_step, time_per_step = ROUTES[self.current_route]
            self.steps_route += len(steps) # para que oee nunca se quede como 0 despues de inicio
            while self.step_index < len(steps):
                self.latitude, self.longitude = steps[self.step_index]
                await self.update(dist_per_step, time_per_step)
                
                #will add logging here instead of print
                logger.info(f" Car {self.car_id} moved to ({self.latitude:.5f}, {self.longitude:.5f}) | total distance: {self.traveled_distance_since_start:.1f}m |  {self.step_index}")

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

                    logger.info(f"Car {self.car_id} updated geozone: {self.current_geozone}")
                # Send timeseries data every step
                try:
                    await HTTP_SESSION.post(
                        f"{hostname}:9002/timeseries",
                        json=self.to_document()
                    )
                except Exception as e:
                    logger.warning(f" Error sending timeseries for Car {self.car_id}: {e}")
                self.step_index += 1

                #agregue logica chocar y checar si el carro esta parado
                if self.is_engine_running==False:
                    logger.warning(f" Car {self.car_id} is not running, skipping step {self.step_index}")
                    await asyncio.sleep(600) # Wait for a minute before next step
                    await increment_cars_correctly_running()  
                    if self.is_crashed:
                        self.is_crashed = False  # Reset crash state after some time
                        self.is_engine_running = True  # Restart the engine after a crash
                    if self.fuel_level <= 0:
                        self.fuel_level = self.max_fuel_level
                        self.is_engine_running = True  # Refuel and restart the engine
                    if self.engine_oil_level <= 0:
                        self.engine_oil_level = 1000  # Reset oil level after a leak
                        self.is_oil_leak = False  #
                    
                    continue
                await asyncio.sleep(time_per_step)
            print(f" Car {self.car_id} finished route {self.current_route}")
            await asyncio.sleep(10)
            self.route_index = 1 - self.route_index
            self.step_index = 0

    async def add_session(self, session_id: str):  
        """Append a new session ID to metadata['sessions']."""  
        if not self.sessions:  
            self.sessions = []  
        self.sessions.append(session_id)  
        logger.info(f"Added session {session_id} to car {self.car_id}")  
  
    async def clear_sessions(self):  
        """Clear all session IDs."""  
        self.sessions.clear()  
        logger.info(f"Cleared all sessions for car {self.car_id}")  