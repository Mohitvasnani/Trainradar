"""
TrainRadar service layer.

Owns everything that is not HTTP: the loaded rail graph and station
coordinates, RTT access token lifecycle, the three caches, and the
position estimation logic.

Nothing in here imports Flask. Routes import from here, never the reverse.
"""

import time
from datetime import datetime, timedelta

import rtt_client
from stations import load_station_coords
from osm_graph import load_rail_graph
from route_leg import route_leg
from estimate import estimate_position
from live_train import find_live_leg


# The corridor this deployment covers. Today: one station.
# Extending the area = adding codes here, no logic changes.
CORRIDOR_STATIONS = ["MAN"]

print("Loading station coordinates...")
coords = load_station_coords()

print("Loading rail graph (this takes a moment)...")
G = load_rail_graph()
print(f"Graph ready: {len(G.nodes)} nodes")


# ---------------------------------------------------------------------------
# RTT access token management
# ---------------------------------------------------------------------------
_token = None
_token_expiry = None

def get_token():
    """Return a valid access token, refreshing it if expired or missing."""
    global _token, _token_expiry
    now = datetime.now().timestamp()
    if _token is None or _token_expiry is None or now >= _token_expiry:
        token, valid_until = rtt_client.get_access_token()
        expiry = datetime.fromisoformat(valid_until).timestamp() - 60
        _token = token
        _token_expiry = expiry
    return _token


# ---------------------------------------------------------------------------
# Caches
#   board   -> short TTL, changes as services come and go
#   service -> longer TTL, calling point schedules barely move
#   route   -> permanent, track geometry never changes
# ---------------------------------------------------------------------------
_board_cache = {}
BOARD_TTL = 120

def get_board_cached(token, crs):
    hit = _board_cache.get(crs)
    if hit and time.time() - hit[0] < BOARD_TTL:
        return hit[1]
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
    """Exposed for the status endpoint without leaking the cache itself."""
    return len(_route_cache)


# ---------------------------------------------------------------------------
# Estimation
# ---------------------------------------------------------------------------
def is_possibly_running(svc, now):
    """Cheap pre-filter using only board data. Costs no API call."""
    temporal = svc.get("temporalData", {})
    arrival = temporal.get("arrival") or {}
    departure = temporal.get("departure") or {}
    if arrival.get("isCancelled") or departure.get("isCancelled"):
        return False

    origin = (svc.get("origin") or [{}])[0]
    dest = (svc.get("destination") or [{}])[0]
    origin_dep = (origin.get("temporalData") or {}).get("scheduleAdvertised")
    dest_arr = (dest.get("temporalData") or {}).get("scheduleAdvertised")
    if not origin_dep or not dest_arr:
        return False

    start = datetime.fromisoformat(origin_dep)
    end = datetime.fromisoformat(dest_arr) + timedelta(minutes=30)
    return start <= now <= end


def estimate_train(svc, token, run_date, now):
    """Estimate one service's position. Returns a dict, or None if not placeable."""
    meta = svc.get("scheduleMetadata", {})
    identity = meta.get("identity")
    service = get_service_cached(token, identity, run_date)

    leg = find_live_leg(service, now)
    if leg is None:
        return None

    a, b = leg
    track = get_route(a["crs"], b["crs"])
    if track is None:
        return None

    pos = estimate_position(track, a["departure"], b["arrival"], now)

    temporal = svc.get("temporalData", {})
    arrival = temporal.get("arrival") or {}
    departure = temporal.get("departure") or {}
    lateness = departure.get("realtimeAdvertisedLateness")
    if lateness is None:
        lateness = arrival.get("realtimeAdvertisedLateness")

    return {
        "uid": identity,
        "headcode": meta.get("trainReportingIdentity"),
        "operator": meta.get("operator", {}).get("name"),
        "legFrom": a["name"],
        "legTo": b["name"],
        "legFromCrs": a["crs"],
        "legToCrs": b["crs"],
        "lat": round(pos.y, 6),
        "lon": round(pos.x, 6),
        "latenessMinutes": lateness,
        "status": temporal.get("status"),
        "estimatedAt": now.isoformat(timespec="seconds"),
        "isEstimate": True,
    }


def compile_serviceboard(svc):
    """Flatten one board service into the shape the departures endpoint returns."""
    meta = svc.get("scheduleMetadata", {})
    operator = meta.get("operator", {})

    origin_list = svc.get("origin") or [{}]
    dest_list = svc.get("destination") or [{}]

    temporal = svc.get("temporalData", {})
    arrival = temporal.get("arrival") or {}
    departure = temporal.get("departure") or {}
    lateness = departure.get("realtimeAdvertisedLateness")
    if lateness is None:
        lateness = arrival.get("realtimeAdvertisedLateness")

    return {
        "uid": meta.get("identity"),
        "headcode": meta.get("trainReportingIdentity"),
        "runDate": meta.get("departureDate"),
        "operator": operator.get("name"),
        "origin": origin_list[0].get("location", {}).get("description"),
        "destination": dest_list[0].get("location", {}).get("description"),
        "latenessMinutes": lateness,
        "isCancelled": arrival.get("isCancelled", False) or departure.get("isCancelled", False),
        "status": temporal.get("status"),
    }