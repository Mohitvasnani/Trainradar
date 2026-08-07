import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "app"))
import time
from flask import Flask, jsonify, abort
from flask_cors import CORS
from datetime import datetime, date, timedelta

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

app = Flask(__name__)
CORS(app)    

#####################################
#RTT access token management
_token = None 
_token_expiry = None

def get_token():
    """here we will return a valid token everytime if its expired or missing it will refresh"""
    global  _token, _token_expiry
    now = datetime.now().timestamp()
    if _token is None or _token_expiry is None or now>= _token_expiry:
        token, valid_until = rtt_client.get_access_token()
      
        expiry = datetime.fromisoformat(valid_until).timestamp()-60
        _token = token
        _token_expiry = expiry
    return _token

@app.route("/")
def home():
   return "TrainRadar API is running "


    
@app.route("/api/status")
def status():
    return jsonify({
        "status": "ok",
        "service": "trainradar"
    })

@app.route("/api/train")
def train():
    return jsonify({
        "serviceUid": "P70998",
        "operator": "Northern",
        "position": {"lat": 53.4839, "lon": -2.2446},
        "fraction": 0.42,
        "timestamp": datetime.now().isoformat()
    })



@app.route("/api/departures/<crs>")
def departures(crs):
    crs = crs.upper()
    token = get_token()
    board = rtt_client.get_location_board(token, code=crs)

    services = []
    for svc in board.get("services", []):
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

        services.append({
            "uid": meta.get("identity"),
            "runDate": meta.get("departureDate"),
            "operator": operator.get("name"),
            "origin": origin_list[0].get("location", {}).get("description"),
            "destination": dest_list[0].get("location", {}).get("description"),
            "latenessMinutes": lateness,
            "isCancelled": arrival.get("isCancelled", False) or departure.get("isCancelled", False),
            "status": temporal.get("status"),
        })

    return jsonify({"station": crs, "services": services})

def estimate_train(svc, token, run_date, now):
    """Estimate one service's position. Returns a dict, or None if not placeable."""
    identity = svc.get("scheduleMetadata", {}).get("identity")
    service = get_service_cached(token, identity, run_date)

    leg = find_live_leg(service, now)
    if leg is None:
        return None

    a, b = leg
    track = get_route(a["crs"], b["crs"])
    if track is None:
        return None

    pos = estimate_position(track, a["departure"], b["arrival"], now)
    return {
        "uid": identity,
        "operator": svc.get("scheduleMetadata", {}).get("operator", {}).get("name"),
        "legFrom": a["name"],
        "legTo": b["name"],
        "lat": round(pos.y, 6),
        "lon": round(pos.x, 6),
    }

_service_cache = {}
SERVICE_TTL = 60   # seconds

def get_service_cached(token, identity, run_date):
    key = (identity, run_date)
    hit = _service_cache.get(key)
    if hit and time.time() - hit[0] < SERVICE_TTL:
        return hit[1]
    data = rtt_client.get_service(token, identity=identity, departure_date=run_date)
    _service_cache[key] = (time.time(), data)
    return data

def is_possibly_running(svc, now):
    """Cheap pre-filter using only board data — costs no API call."""
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

_route_cache = {}

def get_route(crs_a, crs_b):
    key = (crs_a, crs_b)
    if key not in _route_cache:
        track, snap_a, snap_b = route_leg(G, coords, crs_a, crs_b)
        _route_cache[key] = track
    return _route_cache[key]

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
        "lat": round(pos.y, 6),
        "lon": round(pos.x, 6),
        "latenessMinutes": lateness,
        "status": temporal.get("status"),
        "estimatedAt": now.isoformat(timespec="seconds"),
        "isEstimate": True,
        "legFrom": a["name"],
        "legTo": b["name"],
        "legFromCrs": a["crs"],
        "legToCrs": b["crs"],
    }


@app.route("/api/trains")
def trains_area():
    token = get_token()
    today = date.today().isoformat()
    now = datetime.now()

    candidates = {}          # uid -> svc, deduplicated
    for crs in CORRIDOR_STATIONS:
        board = rtt_client.get_location_board(token, code=crs)
        for svc in board.get("services", []):
            if not is_possibly_running(svc, now):
                continue
            uid = svc.get("scheduleMetadata", {}).get("identity")
            if uid:
                candidates[uid] = svc

    results = []
    for uid, svc in candidates.items():
        try:
            train = estimate_train(svc, token, today, now)
            if train:
                results.append(train)
        except Exception as e:
            print(f"skipping {uid}: {e}")

    return jsonify({
        "coverage": CORRIDOR_STATIONS,
        "count": len(results),
        "trains": results,
    })


@app.route("/api/leg/<crs_a>/<crs_b>")
def leg(crs_a, crs_b):
    crs_a = crs_a.upper()
    crs_b = crs_b.upper()

    track = get_route(crs_a, crs_b)
    if track is None:
        abort(404, description=f"No routable track between {crs_a} and {crs_b}")

    return jsonify({
        "from": crs_a,
        "to": crs_b,
        "coordinates": [[round(y, 6), round(x, 6)] for x, y in track.coords],
    })


if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)


  