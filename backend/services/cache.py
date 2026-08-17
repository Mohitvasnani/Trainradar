"""
Caching layer.

Three caches, each with an invalidation rule matched to how its data
actually changes:

    board    120s TTL   services come and go from a station board
    service  300s TTL   a calling point schedule barely moves in five minutes
    route    permanent  track geometry between two stations does not change

The route cache stores failures as well as successes: a station pair that
could not be routed will not become routable, so there is no point retrying.
"""

import time

import rtt_client
from route_leg import route_leg

from services.state import G, coords


_board_cache = {}
BOARD_TTL = 120


def get_board_cached(token, crs):
    """Departure board for one station, refreshed at most every BOARD_TTL."""
    hit = _board_cache.get(crs)
    if hit and time.time() - hit[0] < BOARD_TTL:
        return hit[1]

    data = rtt_client.get_location_board(token, code=crs)
    _board_cache[crs] = (time.time(), data)
    return data


_service_cache = {}
SERVICE_TTL = 300


def get_service_cached(token, identity, run_date):
    """
    Full calling point list for one service.

    Keyed by (identity, run_date) because RTT reuses identities daily: the
    same code on two dates is two different physical runs.
    """
    key = (identity, run_date)
    hit = _service_cache.get(key)
    if hit and time.time() - hit[0] < SERVICE_TTL:
        return hit[1]

    data = rtt_client.get_service(token, identity=identity, departure_date=run_date)
    _service_cache[key] = (time.time(), data)
    return data


_route_cache = {}


def get_route(crs_a, crs_b):
    """Routed track between two stations, or None if it could not be routed."""
    key = (crs_a, crs_b)
    if key not in _route_cache:
        track, snap_a, snap_b = route_leg(G, coords, crs_a, crs_b)
        _route_cache[key] = track
    return _route_cache[key]


def route_cache_size():
    """Exposed for the status endpoint without handing out the cache itself."""
    return len(_route_cache)