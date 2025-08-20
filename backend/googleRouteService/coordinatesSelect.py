"""
Generating random geographic routes with constraints (e.g., max connections, distance filter)...
"""

import pandas as pd
import itertools
from geopy.distance import geodesic
import random
from collections import defaultdict
import logging
logger = logging.getLogger(__name__)
# Coordinates list
data = [
    (1, 30.296986, -97.832127),
    (2, 30.221040, -97.681799),
    (3, 30.359567, -97.766573),
    (4, 30.230474, -97.717504),
    (5, 30.296432, -97.814473),
    (6, 30.272717, -97.740823),
    (7, 30.258789, -97.810058),
    (8, 30.185833, -97.815580),
    (9, 30.245822, -97.805155),
    (10, 30.150807, -97.753726),
    (11, 30.156923, -97.757975),
    (12, 30.225401, -97.688043),
    (13, 30.336417, -97.660609),
    (14, 30.294488, -97.732563),
    (15, 30.299824, -97.750876),
    (16, 30.281009, -97.731868),
    (17, 30.240863, -97.768576),
    (18, 30.192435, -97.826359),
    (19, 30.186454, -97.871151),
    (20, 30.301303, -97.697977),
    (21, 30.287116, -97.673473),
    (22, 30.262037, -97.751868),
    (23, 30.280186, -97.738406),
    (24, 30.285145, -97.755073),
    (25, 30.220119, -97.693330),
    (26, 30.399307, -97.729538),
    (27, 30.185734, -97.816620),
    (28, 30.286535, -97.621343),
    (29, 30.265234, -97.703418),
    (30, 30.275064, -97.753407),
    (31, 30.277924, -97.754302),
    (32, 30.242669, -97.752357),
    (33, 30.219920, -97.749806),
    (34, 30.207294, -97.815315),
    (35, 30.264262, -97.756131),
    (36, 30.324136, -97.773892),
    (37, 30.282748, -97.703885),
    (38, 30.250842, -97.727524),
    (39, 30.258019, -97.739631),
    (40, 30.255308, -97.783954),
    (41, 30.233186, -97.74112),
    (42, 30.288216, -97.741557),
    (43, 30.232504, -97.765659),
    (44, 30.301002, -97.673810),
    (45, 30.342581, -97.749496),
    (46, 30.220813, -97.764890),
    (47, 30.200783, -97.775854),
    (48, 30.217483, -97.828380),
    (49, 30.249226, -97.782660),
    (50, 30.228844, -97.712896),
    (51, 30.265790, -97.725314),
    (52, 30.316821, -97.793624),
]

# variables
number_routes = 150 # will do back and forward, so 150 connections or edges generate 300 routes in routeGen.py
max_connections = 6 # maximum connections per coordinate
min_distance = 2.4  # miles

coordinates = {id: (lat, lon) for id, lat, lon in data}

# generate all unique unordered pairs
pairs = list(itertools.combinations(data, 2))

# compute distances
distance_data = []
for (id1, lat1, lon1), (id2, lat2, lon2) in pairs:
    dist = geodesic((lat1, lon1), (lat2, lon2)).miles
    distance_data.append(((id1, id2), dist))

# Filter by distance ? 
filtered_pairs = [((id1, id2), dist) for ((id1, id2), dist) in distance_data if dist >= min_distance]

# Remove reverse duplicates
seen_keys = set()
unique_filtered = []
for (id1, id2), dist in filtered_pairs:
    key = tuple(sorted((id1, id2)))
    if key not in seen_keys:
        unique_filtered.append(((id1, id2), dist))
        seen_keys.add(key)

# Limit connections per coordinate (looks better ig)
connection_count = defaultdict(int)
selected_routes = []



# Shuffle to randomize
random.shuffle(unique_filtered)

for (id1, id2), dist in unique_filtered:
    if connection_count[id1] < max_connections and connection_count[id2] < max_connections:
        selected_routes.append({"From_ID": id1, "To_ID": id2, "Distance_miles": round(dist, 3)})
        connection_count[id1] += 1
        connection_count[id2] += 1
    if len(selected_routes) >= number_routes:
        break

# Create DataFrame
limited_df = pd.DataFrame(selected_routes)
limited_df.to_csv("random_routes.csv", index=False)


#print("  CSV saved as random_routes.csv")
logger.info(f"CSV saved as random_routes.csv")