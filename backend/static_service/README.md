# Static Service

This microservice is responsible for creating and storing static information about cars in the database. It is intended to be run **once** to populate the database with vehicle data before starting the rest of the fleet management system. After the initial population, you should not run this service again unless you want to reset or update the static car information.

## How to Use

### 1. Install Dependencies

Make sure you have Python 3.8+ and all required dependencies installed.  
Install dependencies using:

```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Ensure your .env file is set up with the correct MongoDB connection string (e.g., MONGODB_URI) and is located in the root of the backend service.

### 3. Start the Static Service
Navigate to the service directory and start the FastAPI app:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 9005
```

### 4. Populate the Database
Use the provided script (backend/simulation/static_cars_creator.py) to create and POST static car data to the /static endpoint.
This script will generate a set of cars and insert them into the database.

Example:
```bash
python [static_cars_creator.py]
```

### 5. Do Not Run Again
After the initial run, do not run the static car creation script again unless you intend to reset or overwrite the static car data in your database. For preference, delete previous cars. If for any reason want to scale up, will also need to use googleRouteService to have more routes (example add 200 more routes before adding 200 cars static so that also works correctly with 200 more time series cars).

## Endpoints
- POST /static — Create a new static car entry.
- GET /static — Retrieve all static car entries.
- GET /static/{car_id} — Retrieve a static car entry by car ID.
- UPDATE /static/{car_id} — Update maintenance logs for a car

## Notes: 
- This service is only for static (unchanging) vehicle information such as brand, model, VIN, etc.
- Dynamic or timeseries data should be handled by other services in your system.
- Running the creation script multiple times will result in duplicate or conflicting data.
