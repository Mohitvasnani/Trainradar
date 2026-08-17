"""
TrainRadar HTTP routes.

Thin layer: parse the request, call the service layer, shape the response.
Failures from the service layer are translated into HTTP statuses here;
nothing below this file knows what an HTTP status is.
"""

from datetime import datetime, date

from flask import Blueprint, jsonify, abort

from services import state, auth, cache, estimation

bp = Blueprint("api", __name__)


@bp.get("/")
def home():
    return "TrainRadar API is running"


@bp.get("/api/status")
def status():
    return jsonify({
        "status": "ok",
        "service": "trainradar",
        "graphNodes": len(state.G.nodes),
        "routesCached": cache.route_cache_size(),
        "coverage": state.CORRIDOR_STATIONS,
    })


@bp.get("/api/departures/<crs>")
def departures(crs):
    """Reshaped departure board for one station."""
    crs = crs.upper()
    token = auth.get_token()

    try:
        board = cache.get_board_cached(token, crs)
    except Exception as e:
        abort(502, description=f"Could not fetch board for {crs}: {e}")

    services = [estimation.compile_serviceboard(svc) for svc in board.get("services", [])]
    return jsonify({"station": crs, "services": services})


@bp.get("/api/trains")
def train_area():
    """
    Estimated positions for every train running across the covered corridor.

    Returns the last good result flagged as stale if RTT is unavailable, so
    a rate-limit blip holds the previous view rather than emptying the map.
    """
    token = auth.get_token()
    today = date.today().isoformat()
    now = datetime.now()

    # Gather candidates from every covered station, deduplicated by uid so a
    # service appearing on two boards is only estimated once.
    candidates = {}
    for crs in state.CORRIDOR_STATIONS:
        try:
            board = cache.get_board_cached(token, crs)
        except Exception as e:
            print(f"board fetch failed for {crs}: {e}")
            continue

        for svc in board.get("services", []):
            if not estimation.is_possibly_running(svc, now):
                continue
            uid = svc.get("scheduleMetadata", {}).get("identity")
            if uid:
                candidates[uid] = svc

    # One try/except per service, so a single unroutable leg drops that train
    # rather than failing the whole response.
    results = []
    for uid, svc in candidates.items():
        try:
            train = estimation.estimate_train(svc, token, today, now)
            if train:
                results.append(train)
        except Exception as e:
            print(f"skipping {uid}: {e}")

    if results:
        state.set_last_good(results)
        return jsonify({
            "coverage": state.CORRIDOR_STATIONS,
            "count": len(results),
            "trains": results,
            "stale": False,
        })

    stale = state.get_last_good()
    return jsonify({
        "coverage": state.CORRIDOR_STATIONS,
        "count": len(stale),
        "trains": stale,
        "stale": True,
    })


@bp.get("/api/leg/<crs_a>/<crs_b>")
def leg(crs_a, crs_b):
    """Routed track geometry between two stations, as [lat, lon] pairs."""
    crs_a = crs_a.upper()
    crs_b = crs_b.upper()

    track = cache.get_route(crs_a, crs_b)
    if track is None:
        abort(404, description=f"No routable track between {crs_a} and {crs_b}")

    return jsonify({
        "from": crs_a,
        "to": crs_b,
        "coordinates": [[round(y, 6), round(x, 6)] for x, y in track.coords],
    })


@bp.get("/api/journey/<uid>/<run_date>")
def journey(uid, run_date):
    """Full journey for one service: calling points plus per-leg geometry."""
    token = auth.get_token()

    try:
        data = estimation.build_journey(token, uid, run_date)
    except Exception as e:
        abort(502, description=f"Could not build journey for {uid}: {e}")

    if not data["stops"]:
        abort(404, description=f"No journey data for {uid} on {run_date}")

    return jsonify(data)


@bp.get("/api/legs")
def all_legs():
    """
    Current leg geometry for every running train, drawn as background network.

    Costs no RTT calls: reads the last good result and pulls geometry from
    the permanent route cache.
    """
    result = []
    seen = set()

    for train in state.get_last_good():
        key = (train["legFromCrs"], train["legToCrs"])
        if key in seen:
            continue
        seen.add(key)

        track = cache.get_route(*key)
        if track is None:
            continue

        result.append({
            "from": key[0],
            "to": key[1],
            "coordinates": [[round(y, 6), round(x, 6)] for x, y in track.coords],
        })

    return jsonify({"legs": result})