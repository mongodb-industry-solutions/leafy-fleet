


# Sessions & Messages

This should be the main enpoint that the app interacts with in regards to request information. 
This endpoint will serve as the filter for querying and obtaning the correct car information for a gven session

This enpoint will:

- Allow to configure a Leafy Fleet session obtaining a threadID
- Obtain all information from a previous session given a threadID
- Add message history to the session
- [Internal endpoint] Query all the necesary information for the RAG application to use with users current selected filters



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
cd backend/sessions
```

### Step 2: Create a virtual environment
Create a virtual environment using `venv`:

```bash
python3 -m venv sessions
```

> **Note:** On Windows, use:
```bash
python -m venv sessions
```

### Step 3: Activate the virtual environment
#### For Linux/Mac:
```bash
source sessions/bin/activate
```

#### For Windows (Command Prompt):
```bash
sessions\Scripts\activate
```

#### For Windows (PowerShell):
```powershell
.\sessions\Scripts\activate.ps1
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
