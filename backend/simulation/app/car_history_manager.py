import asyncio  
import random  
import logging
from route_manager import ROUTES  

logger = logging.getLogger(__name__)

async def _create_car_range(start_id: int, num_cars: int, session: str, history_cars: list):
    from main import Car
    if num_cars <= 0 or num_cars > 100:
        logger.info(f"Skipping car creation for range {start_id}-{start_id+num_cars-1}: num_cars={num_cars} is out of allowed bounds (1-100)")
        return
    for car_id in range(start_id, start_id + num_cars):
        try:
            route_id = car_id % len(ROUTES) + 1 if ROUTES else car_id
            if route_id not in ROUTES:
                logger.info(f"error, route {route_id} not found in ROUTES")
                continue  # Skip invalid routes
            # Extract route coordinates (first lat/lng pair for initialization)
            lat, lng = ROUTES[route_id][0][0]
        except Exception as e:
            logger.error(f"Failed to initialize route for Car {car_id}: {e}")
            continue
        #logger.info(f"Initializing Car {car_id} for Route {route_id} at coordinates ({lat}, {lng}).")
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
            sessions=[session],
            is_historic=True
        )
        history_cars.append(car)
        await register_h_car(car)

async def create_hist_cars(num_cars_1: int, num_cars_2: int, num_cars_3: int, session: str):
    logger.info(f"{num_cars_1 + num_cars_2 + num_cars_3} past cars about to be created")
    history_cars = []
    await _create_car_range(1, num_cars_1, session, history_cars)
    await _create_car_range(101, num_cars_2, session, history_cars)
    await _create_car_range(201, num_cars_3, session, history_cars)
    logger.info(f"Successfully created {len(history_cars)} past cars")
    return history_cars


HISTORIC_CARS = {}
HISTORIC_LOCK = asyncio.Lock()

  
async def register_h_car(car):  
    """Register a car in the global registry."""  
    async with HISTORIC_LOCK:  
        HISTORIC_CARS[car.car_id] = car  
  
async def get_h_car_by_id(car_id: int):  
    """Retrieve a car by its ID."""  
    async with HISTORIC_LOCK:  
        return HISTORIC_CARS.get(car_id)  
  
async def get_h_all_cars():  
    """Retrieve all cars from the registry."""  
    async with HISTORIC_LOCK:  
        return list(HISTORIC_CARS.values())  
  
async def clear_h_all_cars():  
    """Clear all registered cars."""  
    async with HISTORIC_LOCK:  
        HISTORIC_CARS.clear()  
