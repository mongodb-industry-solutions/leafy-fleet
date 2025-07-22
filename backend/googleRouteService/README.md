# Google Route Service

This service generates driving routes for simulation purposes using the Google Routes API. It is designed to create route data artifacts for use in fleet management simulations, allowing you to easily increase the number of simulated vehicles, generate new routes, or switch cities by updating the coordinate set.

> **Note:** This is not a microservice intended for production deployment, but a utility for generating route data as needed.

---

## 🚀 Quick Start

### 1. Prepare Your Environment

#### a. Create a `.env` File

Add your Google Routes API key to a `.env` file in this directory:

```
GOOGLE_ROUTES_API_KEY='<YOUR_GOOGLE_ROUTES_API_KEY>'
```

#### b. Navigate to the Service Directory

```bash
cd backend/googleRouteService
```

#### c. Create and Activate a Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate.ps1
```

#### d. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗺️ Workflow: Generating Routes

1. **Select Route Pairs:**  
   Run `coordinatesSelect.py` to generate a CSV of route pairs based on your chosen coordinates and constraints (e.g., max connections, minimum distance).  
   - Adjust the number of pairs to match your simulation needs (e.g., half the number of cars for bidirectional routes).

2. **Generate Google Routes:**  
   Use `routeGen.py` to call the Google Routes API for each pair in the CSV and save the resulting route data (including encoded polylines).

3. **Decode Route Data:**  
   Run `decodeJson.py` to convert the encoded polylines into usable JSON format for your simulation microservice.

---

## 📂 Project Structure

- `coordinatesSelect.py` — Selects coordinate pairs and generates a CSV of candidate routes.
- `routeGen.py` — Calls the Google Routes API to generate route details for each pair.
- `decodeJson.py` — Decodes the encoded polylines from Google into usable route data.
- `requirements.txt` — Python dependencies for this service.

---

## 📝 Notes

- You can change the city or expand your simulation by updating the coordinates in `coordinatesSelect.py` (and dictionary in `routeGen.py`)
- The generated route data can be used by other microservices or simulation tools in your fleet management platform.
- Make sure your Google Cloud project has the Routes API enabled and billing set up.
- There are some variables that work as limits, in case you dont need to generate much data (or want to generate even more.)

---

## 💡 Example Usage

```bash
# Step 1: Generate route pairs
python3 coordinatesSelect.py

# Step 2: Generate Google route data
python3 routeGen.py

# Step 3: Decode the route data for simulation
python3 decodeJson.py
```
