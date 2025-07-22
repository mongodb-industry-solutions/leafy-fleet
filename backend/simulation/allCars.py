import numpy as np
import json
from dataclasses import dataclass
from datetime import datetime
import random
import asyncio
import aiohttp
import logging
import signal


ROUTES = {}  # Global route map: {route_id: {"steps": np.array, "distancePerStep": float, "timePerStep": float}}

HTTP_SESSION: aiohttp.ClientSession = None
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


#variables 
constant_fuel_consumption_per_m = 0.0009  # in ml/m
constant_oil_consumption_per_m = 0.0005  # in ml/m
hostname = "http://localhost"  # This will be used to connect to the backend service,

#in meantime localhost routes, will be replaced by the real 

@dataclass
class Car:
    brand: str
    model: str
    license_plate: str
    driver_name: str
    vin: int
    year: int
    length: float 
    body_type: str
    vehicle_exterior_color: str
    wmi: str
    weight: float
    car_id: int
    
    # Dynamic state, all items from timeseries model minus timestamp
    current_geozone: str

    fuel_level: float # In ml
    max_fuel_level: float # In ml
    oil_temperature: float # In Celsius
    engine_oil_level: float # In ml
    traveled_distance: float # Total distance traveled by the vehicle in km
    traveled_distance_since_start: float # Distance traveled since the start of the route in m
    performance_score: float # From 0 to 100
    availability_score: float # From 0 to 100
    run_time: float # Engine run time in s
    quality_score: float # From 0 to 100
    is_engine_running: bool
    is_crashed: bool
    current_route: int
    latitude: float 
    longitude: float 
    speed: float # Average speed of the vehicle in km/h
    average_speed: float # Average speed of the vehicle in km/h over the route
    is_moving: bool #  if the vehicle is currently moving

    # Internal state
    step_index: int = 0
    route_index: int = 0  # 0 or 1
    is_oil_leak: bool = False
    has_driver: bool = True  

    def __post_init__(self):
        self.route_ids = [self.car_id, self.car_id + 1] if self.car_id % 2 == 1 else [self.car_id, self.car_id - 1]

    def update(self, move_distance_m: float, time_per_step: float):
        self.traveled_distance += move_distance_m / 1000 # km 
        self.traveled_distance_since_start += move_distance_m  # m
        self.fuel_level = max(self.fuel_level - move_distance_m * constant_fuel_consumption_per_m, 0)
        self.engine_oil_level = max(self.engine_oil_level - move_distance_m * constant_oil_consumption_per_m, 0)
        self.run_time += time_per_step
        self.speed = max((move_distance_m / (time_per_step * 1000) * 3600 )+ random.uniform(-0.35, 0.25), 0) #  speed variation km/h,  non-negative
        self.average_speed = (self.traveled_distance / self.run_time) * 3600  # Convert km/s to km/h
        self.is_moving = self.speed > 0

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
            "oil_temperature": float(self.oil_temperature),
            "is_oil_leak": self.is_oil_leak,
            "is_engine_running": self.is_engine_running,
            "is_crashed": self.is_crashed,
            "current_route": self.current_route,
            "speed": float(round(self.speed, 2)),
            "average_speed": float(round(self.average_speed, 2)),
            "is_moving": self.is_moving,
            "current_geozone": self.current_geozone,
            "vin": self.vin,
            "coordinates": {
            "type": "Point",
            "coordinates": [float(round(self.longitude, 6)), float(round(self.latitude, 6))]
        }
            
        }
        return doc
    


    async def run(self):
        while True:
            self.current_route = self.route_ids[self.route_index]
            steps, dist_per_step, time_per_step = ROUTES[self.current_route]
            while self.step_index < len(steps):
                self.latitude, self.longitude = steps[self.step_index]
                self.update(dist_per_step, time_per_step)

                
                #will add logging here instead of print
                logger.info(f" Car {self.car_id} moved to ({self.latitude:.5f}, {self.longitude:.5f}) | total distance: {self.traveled_distance_since_start:.1f}m |  {self.step_index}")

                if self.step_index % 10 == 0:
                    try:
                        url = f"{hostname}:9004/geofences/check"
                        payload = {'coordinates': [float(self.longitude), float(self.latitude)]}
                        async with HTTP_SESSION.get(url, params=payload) as response:
                            if response.status == 200:
                                data = await response.json()
                                self.current_geozone = (
                                    f"Geofence {data['geofence_id']} active"
                                    if data.get("geofence_id")
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
                await asyncio.sleep(time_per_step)
            print(f" Car {self.car_id} finished route {self.current_route}")
            await asyncio.sleep(10)
            self.route_index = 1 - self.route_index
            self.step_index = 0

def load_routes(filepath="processed_routes_2.json"):
    global ROUTES
    with open(filepath, "r") as f:
        raw = json.load(f)
    for key, val in raw.items():
        ROUTES[int(key)] = (
            np.array([(s["lat"], s["lng"]) for s in val["steps"]], dtype=np.float32),
            float(val["distancePerStep"]),
            float(val["timePerStep"])
        )
    print(f" Loaded {len(ROUTES)} routes")

def create_cars(num_cars=4):
    cars = []
    for car_id in range(1, num_cars + 1):
        route_id = car_id if car_id in ROUTES else car_id - 1
        if route_id not in ROUTES:
            print(f"⚠️ Skipping car {car_id}: no starting route {route_id}")
            continue
        lat, lng = ROUTES[route_id][0][0]
        car = Car(
            car_id=car_id,
            brand=random.choice(["Toyota", "Ford", "Honda", "Chevrolet", "Nissan", "Aston Martin"]),
            model=random.choice(["Model A", "Model B", "Model C"]),
            driver_name=f"Driver {car_id}",
            current_route=route_id,
            latitude=lat,
            longitude=lng,
            license_plate=f"ABC-{car_id:03d}",
            vin=random.randint(1000000000, 9999999999),
            year=random.randint(2000, 2023),
            length=random.uniform(3.5, 5.0),
            body_type=random.choice(["Sedan", "SUV", "Truck", "Coupe"]),
            vehicle_exterior_color=random.choice(["Red", "Blue", "Green", "Black"]),
            wmi=random.choice(["1HG", "1FTR", "1GNE", "1C4", "1N4"]),
            weight=random.uniform(1000, 3000),
            traveled_distance=random.uniform(0, 10000),
            traveled_distance_since_start=0.0,
            fuel_level=random.uniform(1000, 5000),
            max_fuel_level=5000.0,
            oil_temperature=random.uniform(70, 120),
            engine_oil_level=random.uniform(500, 2000),
            performance_score=random.uniform(80, 100),
            availability_score=random.uniform(80, 100),
            run_time=0.0,
            quality_score=90.0,
            is_oil_leak=False,
            is_engine_running=True,
            is_crashed=False,
            speed=0.0,
            average_speed=0.0,
            is_moving=False,
            current_geozone="No Geofence found"
        )
        cars.append(car)
    return cars


async def shutdown_signal_handler():
        logger.info("Shutdown signal received, cleaning up...")
        await HTTP_SESSION.close()
        logger.info("Session closed. Exiting.")   


async def main():
    global HTTP_SESSION
    HTTP_SESSION = aiohttp.ClientSession()

    load_routes()
    cars = create_cars()

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    tasks = [asyncio.create_task(car.run()) for car in cars]

    try:
        await stop_event.wait()
        logger.info("Stop signal received, cancelling tasks...")
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await shutdown_signal_handler()


if __name__ == "__main__":
    asyncio.run(main())
