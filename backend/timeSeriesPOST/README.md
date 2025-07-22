# Timeseries POST Microservice

This should be used as the sole method of posting timeseries data into the database. This handles the embedding and transforming the data so it’s ready to be vector searched and indexed correctly.

## Installation for Development

### Step 0: Preparing the .env

Create a .env file that hold the following variables

```
MONGODB_URI='mongodb+srv://<YOUR_ATLAS_CONNECTION_STRING>'
APP_NAME="<YOUR_CLUSTER_NAME>"
AWS_REGION="<AWS_CLUSTER_REGION>"
AWS_PROFILE="<YOUR_PROFILE_WITH_ACCESS>"
ORIGINS=<YOUR_FRONTEND_URL> (Optional)
```

### Step 1: Navigate to the correct folder
Ensure you are in the correct folder:

```bash
cd backend/timeseries
```

### Step 2: Create a virtual environment
Create a virtual environment using `venv`:

```bash
python3 -m venv TimeseriesPost
```

> **Note:** On Windows, use:
```bash
python -m venv TimeseriesPost
```

### Step 3: Activate the virtual environment
#### For Linux/Mac:
```bash
source TimeseriesPost/bin/activate
```

#### For Windows (Command Prompt):
```bash
TimeseriesPost\Scripts\activate
```

#### For Windows (PowerShell):
```powershell
.\TimeseriesPost\Scripts\activate.ps1
```

### Step 4: Install required dependencies
Install the required Python packages:

```bash
pip install -r requirements.txt
```


## Docker instalation for development

```
sudo docker compose up -d
```
or just
```
docker compose up -d
```

windows (With WSL)
```
docker-compose up -d
```
## Model of timeseries documents in time series
```json
{
    "timestamp": "2025-07-22T14:30:00Z",
    "car_id": 1,
    "fuel_level": 3500.0,
    "engine_oil_level": 1200.0,
    "traveled_distance": 15234.5,
    "run_time": 3600.0,
    "performance_score": 98.5,
    "quality_score": 100.0,
    "availability_score": 95.0,
    "max_fuel_level": 5000.0,
    "oil_temperature": 90.0,
    "is_oil_leak": false,
    "is_engine_running": true,
    "is_crashed": false,
    "current_route": 2,
    "speed": 45.2,
    "average_speed": 42.8,
    "is_moving": true,
    "current_geozone": "Zone A",
    "vin": 12345678901234567,
    "coordinates": {
      "type": "Point",
      "coordinates": [-97.731842, 30.281019]
    }
}
```

## Model of static documents (will not be used in timeseries, but in meatime will stay here for reference)
```json
{
    "brand": "Toyota",
    "model": "Corolla",
    "license_plate": "ABC123",
    "driver_name": "Jane Doe",
    "vin": 12345678901234567,
    "year": 2022,
    "length": 4.5,
    "body_type": "Sedan",
    "vehicle_exterior_color": "Blue",
    "wmi": "JT2BG22K9V",
    "weight": 1300.5,
    "car_id": 1
  }
  ```