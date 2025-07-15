import numpy as np
import json
from dataclasses import dataclass
from datetime import datetime
import random
import asyncio

ROUTES = {}  # Global route map: {route_id: {"steps": np.array, "distancePerStep": float, "timePerStep": float}}

@dataclass
class Car:
    carID: int
    brand: str
    model: str
    driverName: str
    currentGeozone: str
    currentRoute: int
    lat: float
    lng: float

    # Dynamic state
    gasLevel: float = 100.0
    oilLevel: float = 100.0
    distanceTraveled: float = 0
    runTime: int = 0
    isCrashed: bool = False
    isOilLeak: bool = False
    isEngineRunning: bool = True
    hasDriver: bool = True

    # Internal state
    step_index: int = 0
    route_index: int = 0  # 0 or 1

    def __post_init__(self):
        # Car uses route pair (carID, carID+1)
        self.route_ids = [self.carID, self.carID + 1] if self.carID % 2 == 1 else [self.carID, self.carID - 1]
        self.currentRoute = self.route_ids[self.route_index]

    def update(self, move_distance_m: float):
        self.distanceTraveled += move_distance_m
        self.gasLevel = max(self.gasLevel - move_distance_m * 0.00009, 0)
        self.oilLevel = max(self.oilLevel - move_distance_m * 0.00005, 0)
        self.runTime += int(move_distance_m / 10)

    def to_document(self):
        doc = {
            "timestamp": datetime.utcnow().isoformat(),
            "vehicle": {
                "carID": self.carID,
                "brand": self.brand,
                "model": self.model,
                "driverName": self.driverName,
                "currentGeozone": self.currentGeozone,
                "currentRoute": self.currentRoute,
                "hasDriver": self.hasDriver,
                "isCrashed": self.isCrashed,
                "isEngineRunning": self.isEngineRunning,
                "isOilLeak": self.isOilLeak,
            },
            "gasLevel": round(self.gasLevel, 1),
            "oilLevel": round(self.oilLevel, 1),
            "distanceTraveled": round(self.distanceTraveled, 1),
            "runTime": self.runTime,
            "performanceScore": random.randint(80, 100),
            "qualityScore": random.randint(80, 100),
            "avalabilityScore": random.randint(80, 100),
            "maxGasLevel": 100,
            "oilTemperature": round(85 + random.uniform(-5, 5), 1),
            "coordinates": {
                "type": "Point",
                "coordinates": [round(self.lng, 6), round(self.lat, 6)]
            }
        }
        return doc

    async def run(self):
        
        while True:
            
            self.currentRoute = self.route_ids[self.route_index]
            steps, dist_per_step, time_per_step = ROUTES[self.currentRoute]

            while self.step_index < len(steps):
                self.lat, self.lng = steps[self.step_index]
                self.update(dist_per_step)
                print(f"📤 Car {self.carID} moved to ({self.lat:.5f}, {self.lng:.5f}) | Distance: {self.distanceTraveled:.1f}m")
                #aqui mando a db mongo
                self.to_document()
                self.step_index += 1
                await asyncio.sleep(time_per_step)

            print(f"✅ Car {self.carID} finished route {self.currentRoute}")
            await asyncio.sleep(10)
            self.route_index = 1 - self.route_index
            self.step_index = 0


def load_routes(filepath="processed_routes_2.json"): #este json tiene 4 rutas, despuest quitar el _2
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
        lat, lng = ROUTES[route_id][0][0]  # First coord of starting route
        car = Car(
            carID=car_id,
            brand=random.choice(["Toyota", "Ford", "Honda", "Chevrolet", "Nissan", "Aston Martin"]),
            model=random.choice(["Model A", "Model B", "Model C"]),
            driverName=f"Driver {car_id}",
            currentGeozone=random.choice(["Zone 1", "Zone 2", "Zone 3"]),
            currentRoute=route_id,
            lat=lat,
            lng=lng
        )
        cars.append(car)
    return cars


async def main():
    load_routes()
    cars = create_cars()
    await asyncio.gather(*(car.run() for car in cars))


if __name__ == "__main__":
    asyncio.run(main())
