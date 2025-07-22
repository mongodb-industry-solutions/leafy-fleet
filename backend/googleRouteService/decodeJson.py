"""
Read JSON with encoded polylines, decode them, and save processed routes with distance and time per step.
"""


import json
import polyline
import logging

def process_routes(input_file : str, output_file: str):
    with open(input_file, "r") as f:
        raw_data = json.load(f)

    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logger = logging.getLogger("decodeJson")
    logger.info(f"Processing {len(raw_data)} routes from {input_file}")

    processed = {}
    counter = 1
    for route_id, data in raw_data.items():
        #print(f"\n Processing route: {route_id}")
        encoded = data.get("encoded_polyline")
        if not encoded:
            logger.info(f"Route {route_id} missing polyline")
            continue
        try:
            points = polyline.decode(encoded)
            logger.info(f" Decoded {len(points)} points")
        except Exception as e:
            logger.info(f" Decode failed for {route_id}: {e}")
            continue
        if len(points) < 2:
            logger.info(f" Route {route_id} has too few points")
            continue

        distance = data.get("distance_meters", 0)
        duration = data.get("duration_seconds", 0)
        num_segments = len(points) - 1

        distance_per_step = distance / num_segments
        time_per_step = duration / num_segments

        processed[counter] = {
            "routeId": route_id,
            "steps": [{"lat": lat, "lng": lng} for lat, lng in points],
            "distancePerStep": distance_per_step,
            "timePerStep": time_per_step
        }
        counter += 1

        logger.info(f" distancePerStep: {distance_per_step:.2f}, ⏱ timePerStep: {time_per_step:.2f}")

    if processed:
        with open(output_file, "w") as f:
            json.dump(processed, f, indent=2)
        logger.info(f"\n Saved {len(processed)} routes to {output_file}")
    else:
        logger.info(" No valid routes were processed.")

# Run, can add input and output file names if needed
process_routes("routes_final.json", "processed_routes.json")
