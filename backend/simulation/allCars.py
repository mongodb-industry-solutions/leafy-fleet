import time
from typing import Optional
import numpy as np
import json
from dataclasses import dataclass
from datetime import datetime
import random
import asyncio
import aiohttp
import logging
import signal

from fastapi.encoders import jsonable_encoder



ROUTES = {}  # Global route map: {route_id: {"steps": np.array, "distancePerStep": float, "timePerStep": float}}

HTTP_SESSION: aiohttp.ClientSession = None
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


#variables 
constant_fuel_consumption_per_m = 0.0009  # in ml/m
constant_oil_consumption_per_m = 0.0005  # in ml/m
hostname = "http://localhost"  # This will be used to connect to the backend service,
state_lock = asyncio.Lock()  
cars_correctly_running = 10  # Example starting value  
total_cars = 10              # Total cars in simulation  
 # Total number of cars in the simulation, can be used to check if all cars are running correctly
#get on env

#in meantime localhost routes, will be replaced by the real 

async def decrement_cars_correctly_running():  
    async with state_lock:  
        global cars_correctly_running  
        cars_correctly_running -= 1  
  
async def increment_cars_correctly_running():  
    async with state_lock:  
        global cars_correctly_running  
        cars_correctly_running += 1  


"""  
this class and function were used to create the cars, and insert in the database, 
i reused my post component, which is why some of the variables are not used here (timeseries)
 but they are used in the create_cars function that "creates" the cars for the simulation (timeseries)

""" 

@dataclass 
class car_original:
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
    sessions: list = None  # List of session IDs, can be used for tracking or logging
    # Internal state
    step_index: int = 0
    route_index: int = 0  # 0 or 1
    is_oil_leak: bool = False
    has_driver: bool = True  


    def to_static(self):
            static_doc = {
                "brand": self.brand,
                "model": self.model,
                "license_plate": self.license_plate,
                "driver_name": self.driver_name,
                "vin": self.vin,
                "year": self.year,
                "length": self.length,
                "body_type": self.body_type,
                "vehicle_exterior_color": self.vehicle_exterior_color,
                "wmi": self.wmi,
                "weight": self.weight,
                "car_id": self.car_id
            }
            return static_doc
  
async def create_cars_ONCE(num_cars: int):
        FIRST_NAMES = [
            "Emma", "Liam", "Olivia", "Noah", "Ava", "Elijah", "Isabella", "Lucas", "Mia", "Mason",
            "Sophia", "Logan", "Amelia", "Ethan", "Harper", "James", "Evelyn", "Benjamin", "Abigail", "Jack",
            "Charlotte", "Sebastian", "Emily", "Henry", "Luna"
        ]

        LAST_NAMES = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia", "Rodriguez", "Martinez",
            "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
            "Lee", "Perez", "Thompson", "White", "Harris"
        ]

        brand_model_bodytype_map = {
            "Ford": [
                ("F-150", "Truck"),
                ("Mustang", "Coupe"),
                ("Escape", "SUV"),
                ("Explorer", "SUV")
            ],
            "Tesla": [
                ("Model S", "Sedan"),
                ("Model 3", "Sedan"),
                ("Model X", "SUV"),
                ("Model Y", "SUV")
            ],
            "BMW": [
                ("3 Series", "Sedan"),
                ("5 Series", "Sedan"),
                ("X3", "SUV"),
                ("X5", "SUV")
            ],
            "Toyota": [
                ("Camry", "Sedan"),
                ("Corolla", "Sedan"),
                ("RAV4", "SUV"),
                ("Highlander", "SUV")
            ],
            "Volvo": [
                ("XC40", "SUV"),
                ("XC60", "SUV"),
                ("XC90", "SUV"),
                ("S60", "Sedan")
            ],
            "Nissan": [
                ("Altima", "Sedan"),
                ("Sentra", "Sedan"),
                ("Rogue", "SUV"),
                ("Pathfinder", "SUV")
            ],
            "Chevrolet": [
                ("Silverado", "Truck"),
                ("Malibu", "Sedan"),
                ("Equinox", "SUV"),
                ("Tahoe", "SUV")
            ],
            "Honda": [
                ("Civic", "Sedan"),
                ("Accord", "Sedan"),
                ("CR-V", "SUV"),
                ("Pilot", "SUV")
            ]
        }


        wmi_map = {
            "Ford": "1FTR",
            "Tesla": "5YJ",
            "BMW": "WBA",
            "Toyota": "JT2",
            "Volvo": "YV1",
            "Nissan": "1N4",
            "Chevrolet": "1G1",
            "Honda": "1HG"
        }


        cars = []
        for car_id in range(1, num_cars + 1):
            route_id = car_id 
            brand_car = random.choice(list(brand_model_bodytype_map.keys()))
            model_car, body_type_car = random.choice(brand_model_bodytype_map[brand_car])
            wmi_car = wmi_map.get(brand_car, "XXX")
            letters_part = ''.join(random.choices(list("BCDFGHJKLMNPRSTVWXYZ"), k=3))
            numbers_part = str(random.randint(0, 9999)).zfill(4)  # Generate a number between 0 and 9999, then pad with zeros to 4 digits.
            #if route_id not in ROUTES:
            #    print(f" Skipping car {car_id}: no starting route {route_id}")
            #    continue
            #lat, lng = ROUTES[route_id][0][0]
            lat, lng = random.uniform(-90, 90), random.uniform(-180, 180)  # Random coordinates for simplicity
            car = Car(
                car_id=car_id,
                driver_name= f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                current_route=route_id,
                latitude=lat,
                longitude=lng,
                brand=brand_car,
                model=model_car,
                body_type=body_type_car,
                wmi=wmi_car,
                license_plate= f"{letters_part}-{numbers_part}",
                vin=random.randint(1000000000, 9999999999),
                year=random.randint(2000, 2023),
                length=random.uniform(3.5, 5.0),
                vehicle_exterior_color=random.choice(["Red", "Blue", "Green", "Black", "White", "Gray"]),
                weight=random.uniform(1000, 3000),
                traveled_distance=random.uniform(0, 10000),
                traveled_distance_since_start=0.0,
                fuel_level=random.uniform(1000, 5000),
                max_fuel_level=5000.0,
                oil_temperature=random.uniform(70, 120),
                engine_oil_level=random.uniform(500, 2000),
                performance_score=random.uniform(80, 100),
                availability_score=random.uniform(90, 100),
                run_time=0.0,
                quality_score=90.0,
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
            try:    
                async with HTTP_SESSION.post(
                    f"{hostname}:9005/static",
                    json=car.to_static()
                ) as response:
                    if response.status == 201:
                        logger.info(f" Static Car {car.car_id} created successfully")
                    else:
                        logger.warning(f" Failed to create static Car {car.car_id}: {response.status}")
            except Exception as e:
                logger.warning(f" Error creating static Car {car.car_id}: {e}")

        return cars

async def run_maintenance(): # Handler for create maintenance data
        global HTTP_SESSION
        HTTP_SESSION = aiohttp.ClientSession()
        await create_maintenance_data()
        await HTTP_SESSION.close()

async def create_maintenance_data():
    """
    Create mock maintenance data for all cars in the database
    """

    maintenance_dict = [
        "Oil change",
        "Tire rotation",
        "Brake inspection",
        "Battery replacement",
        "Transmission fluid change",
        "Coolant flush",
        "Air filter replacement",
        "Fuel system cleaning",
        "Suspension check",
        "Exhaust system inspection",
        "Alignment check",
        "Windshield wiper replacement",
        "Headlight bulb replacement",
        "Interior cleaning",
        "Exterior detailing",
        "Paint touch-up",
        "Dent repair",
        "Glass replacement",
        "Wheel balancing",
        "Engine tune-up"
    ]


    try:
        async with HTTP_SESSION.get(f"{hostname}:9005/static") as response:
            if response.status == 200:
                static_entries = await response.json()
                print(f"Static entries retrieved: {len(static_entries)}")
                for entry in static_entries:
                    car_id = entry["car_id"]
                    maintenance_logs = []
                    for _ in range(random.randint(1, 5)):  # Random number of maintenance logs per car
                        log = Maintenance_Log(
                            date=str(random_date("4/8/2025 1:30:00", "4/8/2025 16:50:00", random.random())),
                            description=random.choice(maintenance_dict),
                            cost=random.uniform(500, 10000)  # Random cost between 500 and 10000
                        )
                        maintenance_logs.append(log)
                    
                    # Send maintenance logs to the backend service
                    json=jsonable_encoder(maintenance_logs)
                    print(f"Creating maintenance data for car {car_id} with logs: {json}")
                    async with HTTP_SESSION.put(
                        f"{hostname}:9005/static/{car_id}",
                        json=json
                    ) as put_response:
                        if put_response.status == 200:
                            print(f"Maintenance data for car {car_id} created successfully")
                        else:
                            print(f"Failed to create maintenance data for car {car_id}: {put_response.status}")
            
        

    except Exception as e:
        logger.error(f"Error creating maintenance data: {e}")

    

def str_time_prop(start, end, time_format, prop):
    """Get a time at a proportion of a range of two formatted times.

    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """

    stime = time.mktime(time.strptime(start, time_format))
    etime = time.mktime(time.strptime(end, time_format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(time_format, time.localtime(ptime))


def random_date(start, end, prop):
    return str_time_prop(start, end, '%d/%m/%Y %H:%M:%S', prop)



@dataclass
class Maintenance_Log:
    date: datetime
    description: str
    cost: Optional[float] = None


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
                        self.is_oil_leak = False  #
                    continue
                await asyncio.sleep(time_per_step)
            print(f" Car {self.car_id} finished route {self.current_route}")
            await asyncio.sleep(10)
            self.route_index = 1 - self.route_index
            self.step_index = 0

async def create_cars(num_cars: int):
    cars = []
    for car_id in range(1, num_cars + 1):
        route_id = car_id 
        if route_id not in ROUTES:
            logger.info(f" Skipping car {car_id}: no starting route {route_id}")
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
        print(f" Loaded {len(ROUTES)} routes")
        


async def shutdown_signal_handler():
        logger.info("Shutdown signal received, cleaning up...")
        await HTTP_SESSION.close()
        logger.info("Session closed. Exiting.")   


async def main():
    global HTTP_SESSION
    HTTP_SESSION = aiohttp.ClientSession()

    load_routes( "processed_routes.json")
    cars_correctly_running = len(ROUTES)
    total_cars = len(ROUTES)
    cars = await create_cars(num_cars=10)  # Create 300 cars

    
        
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)
#
    tasks = [asyncio.create_task(car.run()) for car in cars]

    try:
        await stop_event.wait()
        logger.info("Stop signal received, cancelling tasks...")
    finally:
        for task in tasks:
            task.cancel()
    await shutdown_signal_handler()


if __name__ == "__main__":
    # print(random_date("1/1/2024 1:30:51", "1/1/2025 16:50:00", random.random()))
    asyncio.run(main())
    # asyncio.run(run_maintenance())