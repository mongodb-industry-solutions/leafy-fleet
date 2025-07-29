"""
Generating routes using Google Routes API from a CSV file of routes in Austin, TX.

"""

import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv
import itertools
import logging

coordinates = {
    1: (30.296986, -97.832127),
    2: (30.221040, -97.681799),
    3: (30.359567, -97.766573),
    4: (30.230474, -97.717504),
    5: (30.296432, -97.814473),
    6: (30.272717, -97.740823),
    7: (30.258789, -97.810058),
    8: (30.185833, -97.815580),
    9: (30.245822, -97.805155),
    10: ( 30.150807, -97.753726),
    11: ( 30.156923, -97.757975),
    12: ( 30.225401, -97.688043),
    13: ( 30.336417, -97.660609),
    14: ( 30.294488, -97.732563),
    15: ( 30.299824, -97.750876),
    16: ( 30.281009, -97.731868),
    17: ( 30.240863, -97.768576),
    18: ( 30.192435, -97.826359),
    19: ( 30.186454, -97.871151),
    20: ( 30.301303, -97.697977),
    21: ( 30.287116, -97.673473),
    22: ( 30.262037, -97.751868),
    23: ( 30.280186, -97.738406),
    24: ( 30.285145, -97.755073),
    25: ( 30.220119, -97.693330),
    26: ( 30.399307, -97.729538),
    27: ( 30.185734, -97.816620),
    28: ( 30.286535, -97.621343),
    29: ( 30.265234, -97.703418),
    30: ( 30.275064, -97.753407),
    31: ( 30.277924, -97.754302),
    32: ( 30.242669, -97.752357),
    33: ( 30.219920, -97.749806),
    34: ( 30.207294, -97.815315),
    35: ( 30.264262, -97.756131),
    36: ( 30.324136, -97.773892),
    37: ( 30.282748, -97.703885),
    38: ( 30.250842, -97.727524),
    39: ( 30.258019, -97.739631),
    40: ( 30.255308, -97.783954),
    41: ( 30.233186, -97.74112),
    42: ( 30.288216, -97.741557),
    43: ( 30.232504, -97.765659),
    44: ( 30.301002, -97.673810),
    45: ( 30.342581, -97.749496),
    46: ( 30.220813, -97.764890),
    47: ( 30.200783, -97.775854),
    48: ( 30.217483, -97.828380),
    49: ( 30.249226, -97.782660),
    50: ( 30.228844, -97.712896),
    51: ( 30.265790, -97.725314),
    52: ( 30.316821, -97.793624),
}

# load environment outisde of functions to avoid reloading
load_dotenv()
api_key = os.getenv("GOOGLE_ROUTES_API_KEY")

logging.basicConfig(filename='myapp.log', level=logging.INFO)
logger = logging.getLogger("routeGen")

# --- Google API call function ---
def compute_route(origin, destination):

    url = f"https://routes.googleapis.com/directions/v2:computeRoutes?key={api_key}"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-FieldMask": "routes.staticDuration,routes.distanceMeters,routes.polyline.encodedPolyline"
    }
    payload = {
        "origin": {
            "location": {"latLng": {"latitude": origin[0], "longitude": origin[1]}}
        },
        "destination": {
            "location": {"latLng": {"latitude": destination[0], "longitude": destination[1]}}
        },
        "travelMode": "DRIVE",
        "polylineQuality": "HIGH_QUALITY",
        "polylineEncoding": "ENCODED_POLYLINE"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        route = data["routes"][0]
        return {
            "distance_meters": route["distanceMeters"],
            "duration_seconds": float(route["staticDuration"].replace("s", "")),
            "encoded_polyline": route["polyline"]["encodedPolyline"]
        }
    except requests.exceptions.RequestException as e:
        logger.info("API request failed:", e)
        return None
    except (KeyError, IndexError) as e:
        logger.info("Unexpected response format:", e)
        return None



# --- Process only the first row (for testing) ---
def process_first_route(csv_file: str, output_file: str ):
    df = pd.read_csv(csv_file)
    first_row = df.iloc[1]

    from_id, to_id = int(first_row["From_ID"]), int(first_row["To_ID"])
    origin = coordinates[from_id]
    destination = coordinates[to_id]
    route_data = {}
    result_ab = compute_route(origin, destination)
    if result_ab:
        route_data[f"{from_id}_{to_id}"] = result_ab

    result_ba = compute_route(destination, origin)
    if result_ba:
        route_data[f"{to_id}_{from_id}"] = result_ba

    if route_data:
        with open(output_file, "w") as f:
            json.dump(route_data, f, indent=2)
        logger.info(f" Saved routes to {output_file}")
    else:
        logger.info(" error saving routes.  check to avoid using api calls unsuccesfully")


# --- Process all 300 routes --- update
def process_all_routes(csv_file :str, output_file: str ):
    df = pd.read_csv(csv_file)

    all_routes = {}
    #un array de routes fallidas
    failed_routes = []
    limit = 5 # limite 5, 10 carros 
    #  islice to limit the number of rows processed while testing
    rows = itertools.islice(df.iterrows(), limit) if limit else df.iterrows()


    for i, row in rows:
        from_id, to_id = int(row["From_ID"]), int(row["To_ID"])
        origin = coordinates.get(from_id)
        destination = coordinates.get(to_id)

        if not origin or not destination:
            logger.info(f"[{i+1}] Skipping invalid coordinates: {from_id} → {to_id}")
            failed_routes.append((from_id, to_id, "Invalid coordinates"))
            continue

        result_ab = compute_route(origin, destination)
        result_ba = compute_route(destination, origin)

        if result_ab:
            all_routes[f"{from_id}_{to_id}"] = result_ab
        else:
            logger.info(f" {from_id} → {to_id} failed")
            failed_routes.append((from_id, to_id, " request failed"))

        if result_ba:
            all_routes[f"{to_id}_{from_id}"] = result_ba
            
        else:
            logger.info(f"{to_id} → {from_id} failed")
            failed_routes.append((to_id, from_id, " request failed"))

    # Save combined JSON file with all successful routes
    with open(os.path.join( output_file), "w") as f:
        json.dump(all_routes, f, indent=2)
    logger.info(f"\n All saved to {output_file}")

    #  print failed ones
    if failed_routes:
        logger.info("\n Failed Routes:")
        for from_id, to_id, reason in failed_routes:
            logger.info(f"- {from_id} → {to_id}: {reason}")


# --- Main trigger ---
if __name__ == "__main__":
    #process_first_route()
    if not os.getenv("GOOGLE_ROUTES_API_KEY"):
        logger.info(" GOOGLE_ROUTES_API_KEY not set in .env")
    else:
        process_all_routes("random_150_routes.csv", "routes_final.json") 