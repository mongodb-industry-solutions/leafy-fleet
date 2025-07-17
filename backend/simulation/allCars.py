import numpy as np
import json
from dataclasses import dataclass
from datetime import datetime
import random
import asyncio
import aiohttp

ROUTES = {}  # Global route map: {route_id: {"steps": np.array, "distancePerStep": float, "timePerStep": float}}

@dataclass
class Car:
    Brand: str
    Model: str
    LicensePlate: str
    driverName: str
    VIN: int
    Year: int
    Length: float 
    BodyType: str
    VehicleExteriorColor: str
    WMI: str
    Weight: float
    carID: int
    
    # Dynamic state, all items from timeseries model minus timestamop
    currentGeozone: str


    # right now variables follow names of Covesa (VSS) standard, can rewrite so that only follows that in document
    #model, and has snake_case while in python
      
    FuelLevel: float # In ml
    maxFuelLevel: float # In ml, no creo que se ocupe
    OilTemperature: float # In Celsius
    EngineOilLevel: float # In ml
    TraveledDistance : float # Field(default=31220.0, description="Total distance traveled by the vehicle in km")
    TraveledDistanceSinceStart: float # Field(default=0.0, description="Distance traveled since the start of the route in km")
    performanceScore: float # From 0 to 100, used to check whether the vehicle is achieving its objective, visiting all needed keypoints
    avaliabilityScore: float # From 0 to 100, also for OEE, run time vs planned time, in our case run time of a route with traffic vs a planned route without traffic
    RunTime: float # is Used to measure type:"sensor". datatype:"float" deprecation:"v5.0 OBD-branch is deprecated." description:"PID 1F - Engine run time" unit:"s"
    qualityScore: float # From 0 to 100, for example that the package was delivered on to the correct house instead of the neighbours house, in our simulation this can be also always 100% correct
    isEngineRunning: bool
    isCrashed: bool
    currentRoute: int
    Latitude: float 
    Longitude: float 
    Speed: float # Field(default=0.0, description="Average speed of the vehicle in km/h")
    AverageSpeed: float # Field(default=0.0, description="Average speed of the vehicle in km/h over the route")
    IsMoving: bool # Field(default=True, description="Indicates if the vehicle is currently moving")
    currentGeozone: str # will update every 10 steps

    # Internal state
    step_index: int = 0
    route_index: int = 0  # 0 or 1
    isOilLeak: bool = False
    hasDriver: bool = True  

    def __post_init__(self):
        # Car uses route pair (carID, carID+1)
        # IF carID is even, (1, 3, 5...), just follow next(carID, carID+1)= (1,2), else its (carID, carID-1)= (2,1)
        self.route_ids = [self.carID, self.carID + 1] if self.carID % 2 == 1 else [self.carID, self.carID - 1]

    def update(self, move_distance_m: float,time_per_step: float ):
        self.TraveledDistance +=  move_distance_m / 1000 # km 
        self.TraveledDistanceSinceStart += move_distance_m  # m
        self.FuelLevel = max(self.FuelLevel - move_distance_m * 0.00009, 0)
        self.EngineOilLevel = max(self.EngineOilLevel - move_distance_m * 0.00005, 0)
        self.RunTime += time_per_step
        self.Speed = move_distance_m / (time_per_step*1000) + random.uniform(-0.5, 0.5)  # Simulate speed variation, have to be in km/h
        self.AverageSpeed = (self.TraveledDistance / self.RunTime) * 3600  # Convert km/s to km/h
        self.IsMoving = self.Speed > 0
        




    #para el time series
    def to_document(self):
        doc = {
            "timestamp": datetime.utcnow().isoformat(),
            "carID": self.carID,
            "FuelLevel": round(self.FuelLevel, 1),
            "EngineOilLevel": round(self.EngineOilLevel, 1),
            "TraveledDistance": round(self.TraveledDistance, 4),
            "RunTime": self.RunTime,
            "PerformanceScore": self.performanceScore,
            "qualityScore": self.qualityScore,
            "AvalabilityScore": self.avaliabilityScore,
            "maxFuelLevel": self.maxFuelLevel,
            "oilTemperature": self.OilTemperature,
            "isOilLeak": self.isOilLeak,
            "isEngineRunning": self.isEngineRunning,
            "isCrashed": self.isCrashed,
            "currentRoute": self.currentRoute,
            "Speed": round(self.Speed, 2),
            "AverageSpeed": round(self.AverageSpeed, 2),
            "IsMoving": self.IsMoving,
            "currentGeozone": self.currentGeozone,
            "VIN": self.VIN,
            "coordinates": {
                "type": "Point",
                "coordinates": [round(self.Longitude, 6), round(self.Latitude, 6)] # mongo es long lat
            }
        }
        return doc

    async def run(self):
        
        while True:
            
            self.currentRoute = self.route_ids[self.route_index]
            steps, dist_per_step, time_per_step = ROUTES[self.currentRoute]
            # Global route map: {route_id: {"steps": np.array, "distancePerStep": float, "timePerStep": float}}
            while self.step_index < len(steps):
                self.Latitude, self.Longitude = steps[self.step_index]
                self.update(dist_per_step, time_per_step)
                print(f"📤 Car {self.carID} moved to ({self.Latitude:.5f}, {self.Longitude:.5f}) | Distance this: {self.TraveledDistanceSinceStart:.1f}m |  {self.step_index}" )

                
                self.step_index += 1
                
                if self.step_index % 10 == 0:
                    async with aiohttp.ClientSession() as session:
                        params = {"lng": self.Longitude, "lat": self.Latitude}
                        async with session.get("http://localhost:9003/geofences/check", params=params) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                self.currentGeozone = data.get("geofence_name")
                            else:
                                self.currentGeozone = "No Geofence found"
                    # GET GEOWITHIN ZONE, should be None or ZOne1, dtwn, etc
                
                #send to timeseries
                async with aiohttp.ClientSession() as session:
                    async with session.post("http://localhost:9000/timeseries", json=self.to_document()) as resp:
                        if resp.status != 200:
                            print(f"⚠️ Error sending data for car {self.carID}: {resp.status}")
                await asyncio.sleep(time_per_step)

            print(f" Car {self.carID} finished route {self.currentRoute}")
            await asyncio.sleep(10)
            self.route_index = 1 - self.route_index # if indx is 0, is 1, else 1-1= 0
            self.step_index = 0 # starts returning to start of route


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
            Brand=random.choice(["Toyota", "Ford", "Honda", "Chevrolet", "Nissan", "Aston Martin"]),
            Model=random.choice(["Model A", "Model B", "Model C"]),
            driverName=f"Driver {car_id}",
            currentRoute=route_id,
            Latitude=lat,
            Longitude=lng,
            # Static properties
            LicensePlate=f"ABC-{car_id:03d}",
            VIN=random.randint(1000000000, 9999999999),  # Random 10-digit VIN
            Year=random.randint(2000, 2023),
            Length=random.uniform(3.5, 5.0),  # Random length in
            BodyType=random.choice(["Sedan", "SUV", "Truck", "Coupe"]),
            VehicleExteriorColor=random.choice(["Red", "Blue", "Green", "Black"]),
            WMI=random.choice(["1HG", "1FTR", "1GNE", "1C4", "1N4"]),
            Weight=random.uniform(1000, 3000),  # Random weight in kg
            TraveledDistance= random.uniform(0, 10000),  # Random initial distance
            TraveledDistanceSinceStart=0.0,
            FuelLevel=random.uniform(1000, 5000),  # Random initial fuel level
            maxFuelLevel=5000.0,  # Assuming max fuel level is 500
            OilTemperature=random.uniform(70, 120),  # Random oil temperature in Celsius
            EngineOilLevel=random.uniform(500, 2000),  # Random initial engine oil
            performanceScore=random.uniform(80, 100),  # Random performance score
            avaliabilityScore=random.uniform(80, 100),  # Random availability score
            RunTime=0.0,  # Initial run time in seconds
            qualityScore=90.0,  # Assuming perfect quality for simulation
            isOilLeak=False,  # No oil leak at start
            isEngineRunning=True,  # Engine starts running
            isCrashed=False,  # No crash at start
            Speed=0.0,  # Initial speed in km/h
            AverageSpeed=0.0,  # Initial average speed in km/h
            IsMoving=False,  # Initially not moving
            currentGeozone="No Geofence found"  # Initial geozone

        )
        cars.append(car)
    return cars


async def main():
    load_routes()
    cars = create_cars()
    await asyncio.gather(*(car.run() for car in cars))


if __name__ == "__main__":
    asyncio.run(main())
