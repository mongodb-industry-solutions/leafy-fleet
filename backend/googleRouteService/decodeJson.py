import json
import polyline

def process_routes(input_file="encoded_routes_2.json", output_file="processed_routes_2.json"):
    with open(input_file, "r") as f:
        raw_data = json.load(f)

    print(f" Loaded {len(raw_data)} routes from {input_file}")

    processed = {}
    counter = 1
    for route_id, data in raw_data.items():
        #print(f"\n Processing route: {route_id}")
        encoded = data.get("encoded_polyline")
        if not encoded:
            print(f"Route {route_id} missing polyline")
            continue
        try:
            points = polyline.decode(encoded)
            print(f" Decoded {len(points)} points")
        except Exception as e:
            print(f" Decode failed for {route_id}: {e}")
            continue
        if len(points) < 2:
            print(f" Route {route_id} has too few points")
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

        print(f" distancePerStep: {distance_per_step:.2f}, ⏱ timePerStep: {time_per_step:.2f}")

    if processed:
        with open(output_file, "w") as f:
            json.dump(processed, f, indent=2)
        print(f"\n Saved {len(processed)} routes to {output_file}")
    else:
        print(" No valid routes were processed.")

# Run it
process_routes()
