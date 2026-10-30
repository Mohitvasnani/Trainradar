"""TrainRadar API routes."""

from datetime import datetime, date
from flask import Blueprint, jsonify
from services import state, auth, cache, estimation
from zoneinfo import ZoneInfo

UK = ZoneInfo("Europe/London")

bp = Blueprint( "api",   __name__)


@bp.get("/")
def home():    return "TrainRadar API is running"


@bp.get("/api/status")
def status():  return jsonify({
        "status": "k",
        "graphNodes":len(state.G.nodes),
        "routesCached":cache.route_cache_size(),
        "coverage": state.CORRIDOR_STATIONS})


@bp.get("/api/departures/<crs>")
def departures(crs):
    crs =crs.upper()
    token=auth.get_token()
    try:        board = cache.get_board_cached(token, crs)
    except Exception:

        return jsonify({"error": f"not getting depature {crs}"}), 502

    
    services =[estimation.full_depboard(ser) for ser in board.get("services",[])]
    return jsonify({
        "station": crs, "services": services})


@bp.get("/api/trains")
def train_area():
    token =auth.get_token()
    now = datetime.now(UK).replace(tzinfo=None)

    today =  date.today().isoformat()
    now= datetime.now()

    candidates = {}
    for crs in state.CORRIDOR_STATIONS:


        try:

            board = cache.get_board_cached(token, crs)
        except Exception:  continue

        for ser in board.get("services", []):
            if not estimation.is_train_running(ser, now):   continue
            uid = ser.get("scheduleMetadata", {}).get("identity")
            if uid:               
                candidates[uid] =ser

    
    results = []
    for uid, ser in candidates.items():
        try:
            train = estimation.estimate_trainPosition(ser, token, today, now)
            if train:
                results.append(train)
        except Exception: continue

    
    if results:
        state.save_last_good(results)
        return jsonify({
            "coverage": state.CORRIDOR_STATIONS,
            "count": len(results),
            "trains": results, "stale": False })

    stale = state.get_last_good()
    return jsonify({
        "coverage":state.CORRIDOR_STATIONS,
        "count":len(stale),
        "trains":stale,
        "stale": True,
    })


@bp.get("/api/leg/<crs_a>/<crs_b>")
def leg(crs_a, crs_b):
    crs_a = crs_a.upper()
    crs_b = crs_b.upper()

    track = cache.get_route(crs_a, crs_b)
    if track is None:


        return jsonify({"error": f"no track between {crs_a} and {crs_b}"}), 404

    return jsonify({
        "from": crs_a, "to": crs_b,
        "coordinates": [[round(y, 6), round(x, 6)] for x, y in track.coords] })


@bp.get("/api/journey/<uid>/<run_date>")
def journey(uid,   run_date):
    token = auth.get_token()

    try:
        data=   estimation.journey_building(token,  uid,run_date)
    except Exception:
        return jsonify({"Error": f"unable to build {uid}"}), 502

    if not data["stops"]:
        return jsonify({
            "Error": f"no journey found for {uid} on{run_date}"
            }),404
    return jsonify(data)


@bp.get("/api/legs")
def all_legs():
    res =[]
    seen= set()

    for train in state.get_last_good():
        key= (train["legFromCrs"], train["legToCrs"])
        if key in seen:
            continue
        seen.add(key)

        track = cache.get_route(*key)
        if track is None:
            continue

        res.append({"from": key [ 0 ],  "to": key[ 1],
            "coordinates": [[round(y, 6), round(x, 6)] for x, y in track.coords]})
    return jsonify({"legs": res})
@bp.get("/api/save-routes")
def save_routes():
    count = cache.save_route_cache()
    return jsonify({"saved": count})