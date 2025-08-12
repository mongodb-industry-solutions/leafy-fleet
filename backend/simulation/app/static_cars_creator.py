import numpy as np
import json
from dataclasses import dataclass
from datetime import datetime
import random
import asyncio
import aiohttp
import logging
from fastapi.encoders import jsonable_encoder
from typing import Optional
import time
from global_context import static_service

ROUTES = {}  # Global route map: {route_id: {"steps": np.array, "distancePerStep": float, "timePerStep": float}}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


#variables 
hostname = static_service  # This will be used to connect to the backend service of static
#get on env

#in meantime localhost routes, will be replaced by the real 
async def create_cars_handler(num_cars: int):
    global HTTP_SESSION
    HTTP_SESSION = aiohttp.ClientSession()
    await create_cars_ONCE(num_cars)
    await HTTP_SESSION.close()
  
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
            car = car_original(
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
                availability_score=random.uniform(80, 100),
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
                    f"{static_service}:9005/static",
                    json=car.to_static()
                ) as response:
                    if response.status == 201:
                        logger.info(f" Static Car {car.car_id} created successfully")
                    else:
                        logger.warning(f" Failed to create static Car {car.car_id}: {response.status}")
            except Exception as e:
                logger.warning(f" Error creating static Car {car.car_id}: {e}")

        return cars


"""  
this class will be used to create the cars, it will be used in the simulation everytime it wakes up.
"""  

# Maintenance logs (must be done only once before running)\
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
                            date=str(random_date("4/8/2024 1:30:00", "4/8/2025 16:50:00", random.random())),
                            description=random.choice(maintenance_dict),
                            cost=random.uniform(500, 10000)  # Random cost between 500 and 10000
                        )
                        maintenance_logs.append(log)

                    # Send maintenance logs to the backend service
                    json=jsonable_encoder(maintenance_logs)
                    # print(f"Creating maintenance data for car {car_id} with logs: {json}")
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




async def main():
    print("Starting static cars creator...")
    # To create cars once
    # asyncio.run(create_cars_handler(300))

    # To run maintenance data creation
    # asyncio.run(run_maintenance())

    print("Static cars creator finished.")

if __name__ == "__main__":
    asyncio.run(main())