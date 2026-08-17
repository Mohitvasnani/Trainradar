"""
Loaded application state.

Owns the two expensive objects the rest of the service layer reads: the
station coordinate lookup and the routed rail graph. Both load once, at
import time, and are treated as read-only afterwards.

Also holds the coverage configuration, which is the only thing that needs
changing to widen or move the area the deployment serves.
"""

from stations import load_station_coords
from osm_graph import load_rail_graph


# The corridor this deployment covers. Extending the area means adding
# codes here; no logic anywhere else changes.
CORRIDOR_STATIONS = ["MAN"]

print("Loading station coordinates...")
coords = load_station_coords()

print("Loading rail graph (this takes a moment)...")
G = load_rail_graph()
print(f"Graph ready: {len(G.nodes)} nodes")


# Last successful set of estimated positions. Served as stale data when RTT
# is unavailable, so a rate-limit blip holds the previous view rather than
# emptying the map.
_last_good_result = []


def set_last_good(results):
    global _last_good_result
    _last_good_result = results


def get_last_good():
    return _last_good_result