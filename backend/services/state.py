import os
from app.stations import load_station_coords
from app.osm_graph import load_rail_graph


# Stations we're tracking
CORRIDOR_STATIONS = ["MAN"]

print("Loading station coordinates...")
coords = load_station_coords()

print("Loading rail graph...")
G = load_rail_graph()
print(f"Graph ready: {len(G.nodes)} nodes")


# Last good train positions (used when API fails)
last_good = []


def save_last_good(results):
    global last_good
    last_good = results


def get_last_good():
    return last_good