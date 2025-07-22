# Timeseries GET Service

This should be used as the sole method of getting data from the database. This handles the embedding and transforming the data so it’s ready to be vector searched and indexed correctly.

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
