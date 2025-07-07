import os
import requests
import json
from dotenv import load_dotenv

def compute_route(origin, destination):
    """
    Calls Google Routes API v2 with the given origin and destination coordinates.

    Args:
        origin (tuple): A tuple (latitude, longitude) for the origin.
        destination (tuple): A tuple (latitude, longitude) for the destination.

    Returns:
        dict: Parsed JSON response from the API.
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_ROUTES_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing GOOGLE_ROUTES_API_KEY environment variable.")

    url = f"https://routes.googleapis.com/directions/v2:computeRoutes?key={api_key}"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-FieldMask": "routes.legs.steps.startLocation,routes.legs.steps.endLocation,routes.legs.steps.distanceMeters,routes.legs.steps.staticDuration"
    }

    payload = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": origin[0],
                    "longitude": origin[1]
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": destination[0],
                    "longitude": destination[1]
                }
            }
        },
        "travelMode": "DRIVE"
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()


# example with my coordinates
if __name__ == "__main__":
    origin_coords = (37.4219999, -122.0840575)
    destination_coords = (37.423825, -122.091014)

    try:
        result = compute_route(origin_coords, destination_coords)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error calling Google Routes API: {e}")
