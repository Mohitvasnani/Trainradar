import time

import rtt_client
from app.route_leg import route_leg

from services.state import G, coords


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
    if key not in _route_cache:
        track, snap_a, snap_b = route_leg(G, coords, crs_a, crs_b)
        _route_cache[key] = track
    return _route_cache[key]


def route_cache_size():
    return len(_route_cache)