from datetime import datetime, date
 
from flask import Blueprint, jsonify, abort
 
from services import rtt

bp = Blueprint("api", __name__)



@bp.get("/")
def home():
    return "TrainRadar API is running"

@bp.get("/api/status")
def status():
    return jsonify(
        {
            "status": "ok",
            "service": "trainradar",
        "graphNodes": len(rtt.G.nodes),
        "routesCached": rtt.route_cache_size(),
        "coverage": rtt.CORRIDOR_STATIONS,
        }
    )

@bp.get("/api/departures/<crs>")
def departures(crs):
    crs =crs.upper()
    token=rtt.get_token()
    try:
        board = rtt.get_board_cached(token,crs)
    except Exception as e:
        abort(502, description=f"Could not fetch board for {crs}: {e}")
    services = [rtt.compile_serviceboard(svc) for svc in board.get("services",[])]
    return jsonify({
        "station": crs, "services": services
    })

# Last successful result, so a rate-limit blip returns stale positions
# rather than an empty map.

successful_result=[]



@bp.get("/api/trains")
def train_area():
    """estimated position of train inside the covered region"""
    global successful_result

    token =  rtt.get_token()
    today = date.today().isoformat()
    now=datetime.now()

# Gather candidates from every covered station, deduplicated by uid so a
    # service touching two boards is only estimated once.

    candidates ={}
    for crs in rtt.CORRIDOR_STATIONS:
        try:
            board = rtt.get_board_cached(token, crs)
        except Exception as e:
            print(f"board fetch failed for {crs}: {e}")
            continue
 
        for svc in board.get("services", []):
            if not rtt.is_possibly_running(svc, now):
                continue
            uid = svc.get("scheduleMetadata", {}).get("identity")
            if uid:
                candidates[uid] = svc
 
    results = []
    for uid, svc in candidates.items():
        try:
            train = rtt.estimate_train(svc, token, today, now)
            if train:
                results.append(train)
        except Exception as e:
            print(f"skipping {uid}: {e}")
 
    if results:
        successful_result = results
        return jsonify({
            "coverage": rtt.CORRIDOR_STATIONS,
            "count": len(results),
            "trains": results,
            "stale": False,
        })
 
    return jsonify({
        "coverage": rtt.CORRIDOR_STATIONS,
        "count": len(successful_result),
        "trains": successful_result,
        "stale": True,
    })
 
 
@bp.get("/api/leg/<crs_a>/<crs_b>")
def leg(crs_a, crs_b):
    """Routed track geometry between two stations, as [lat, lon] pairs."""
    crs_a = crs_a.upper()
    crs_b = crs_b.upper()
 
    track = rtt.get_route(crs_a, crs_b)
    if track is None:
        abort(404, description=f"No routable track between {crs_a} and {crs_b}")
 
    return jsonify({
        "from": crs_a,
        "to": crs_b,
        "coordinates": [[round(y, 6), round(x, 6)] for x, y in track.coords],
    })
 
