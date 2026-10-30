import time

import rtt_client

from services.state import coords, get_graph
import json
import os
from shapely.geometry import LineString

ROUTE_CACHE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "route_cache.json"
)


_board_cache = {}
BOARD_TTL = 120


def get_board_cached(token, crs):
    # Check if we already have this board cached
    hit = _board_cache.get(crs)
    if hit and time.time() - hit[0] < BOARD_TTL:
        return hit[1]

    # Fetch fresh data
    data = rtt_client.get_location_board(token, code=crs)
    _board_cache[crs] = (time.time(), data)
    return data


_service_cache = {}
SERVICE_TTL = 300


def get_service_cached(token, identity, run_date):
    
    key = (identity, run_date)
    hit = _service_cache.get(key)
    if hit and time.time() - hit[0] < SERVICE_TTL:
        return hit[1]

    data = rtt_client.get_service(token, identity=identity, departure_date=run_date)
    _service_cache[key] = (time.time(), data)
    return data


_route_cache = {}


def get_route(crs_a, crs_b):
    key = (crs_a, crs_b)
    if key in _route_cache:
        return _route_cache[key]

    G = get_graph()
    if G is None:
        return None

    from app.route_leg import route_leg
    track, snap_a, snap_b = route_leg(G, coords, crs_a, crs_b)
    _route_cache[key] = track
    return track


def route_cache_size():
    return len(_route_cache)
def save_route_cache(path=ROUTE_CACHE_PATH):
    out = {}
    skipped = []

    for (crs_a, crs_b), track in _route_cache.items():
        if track is None:
            continue
        if track.geom_type != "LineString":
            skipped.append(f"{crs_a}-{crs_b} ({track.geom_type})")
            continue
        out[f"{crs_a}-{crs_b}"] = [
            [round(x, 6), round(y, 6)] for x, y in track.coords
        ]

    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f)
    os.replace(tmp, path)

    if skipped:
        print(f"skipped {len(skipped)} non-LineString legs: {skipped}")
    print(f"saved {len(out)} legs to {path}")
    return len(out)


def load_route_cache(path=ROUTE_CACHE_PATH):
    if not os.path.exists(path):
        print(f"no route cache at {path}")
        return 0

    with open(path) as f:
        data = json.load(f)

    for key, points in data.items():
        crs_a, crs_b = key.split("-")
        _route_cache[(crs_a, crs_b)] = LineString(points)

    print(f"loaded {len(data)} legs from route cache")
    return len(data)