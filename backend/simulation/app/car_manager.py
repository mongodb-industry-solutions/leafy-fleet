import asyncio  
import random  
import logging
from route_manager import ROUTES  

logger = logging.getLogger(__name__)

async def create_cars(num_cars: int):
    from main import Car
    """Create cars (register and initialize them)"""  
    logger.info(f"{num_cars} about to be created")
    cars = []  
    for car_id in range(1, num_cars + 1):  
        # Cycle through available routes  
        route_id = car_id % len(ROUTES) + 1 if ROUTES else car_id    
        if route_id not in ROUTES: 
            logger.info(f"ooof")
            continue  # Skip invalid routes  
        logger.info("continue")
        # Extract route coordinates (first lat/lng pair for initialization)  
        lat, lng = ROUTES[route_id][0][0]    
        logger.info(f"Initializing Car {car_id} for Route {route_id} at coordinates ({lat}, {lng}).")  
 
        # Initialize a new Car instance  
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
            sessions=[] 
        )  
  
        # Add car to list and register in the GLOBAL_CARS registry  
        cars.append(car)  
        await register_car(car)  
    logger.info(f"Successfully created {len(cars)} cars")  
    return cars  

GLOBAL_CARS = {}  
CARS_LOCK = asyncio.Lock()  
  
async def register_car(car):  
    """Register a car in the global registry."""  
    async with CARS_LOCK:  
        GLOBAL_CARS[car.car_id] = car  
  
async def get_car_by_id(car_id: int):  
    """Retrieve a car by its ID."""  
    async with CARS_LOCK:  
        return GLOBAL_CARS.get(car_id)  
  
async def get_all_cars():  
    """Retrieve all cars from the registry."""  
    async with CARS_LOCK:  
        return list(GLOBAL_CARS.values())  
  
async def clear_all_cars():  
    """Clear all registered cars."""  
    async with CARS_LOCK:  
        GLOBAL_CARS.clear()  
