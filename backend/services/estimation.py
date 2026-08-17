"""
Position estimation and response shaping.

Turns RTT's nested service data into the flat structures the API returns.
Every position produced here is an estimate derived from scheduled times;
nothing in this module observes an actual position, because no public feed
provides one.
"""

from datetime import datetime, timedelta

from estimate import estimate_position
from find_current_leg import find_live_leg

from services.cache import get_service_cached, get_route
from services.geometry import route_plausibility, is_implausible


# Grace period added to a service's scheduled arrival before it is treated
# as finished, so a late-running train is not filtered out prematurely.
RUNNING_GRACE = timedelta(minutes=30)


def is_possibly_running(svc, now):
    """
    Cheap pre-filter using only board data, costing no API call.

    A station board is mostly future departures. Testing whether now falls
    inside a service's scheduled window removes roughly half the candidates
    before any per-service request is made.
    """
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
    end = datetime.fromisoformat(dest_arr) + RUNNING_GRACE
    return start <= now <= end


def _lateness(temporal):
    """Reported lateness in minutes, preferring departure over arrival."""
    arrival = temporal.get("arrival") or {}
    departure = temporal.get("departure") or {}
    late = departure.get("realtimeAdvertisedLateness")
    if late is None:
        late = arrival.get("realtimeAdvertisedLateness")
    return late


def _endpoint_name(svc, key):
    """Origin or destination name. Both are lists, since services can split."""
    entries = svc.get(key) or [{}]
    return entries[0].get("location", {}).get("description")


def estimate_train(svc, token, run_date, now):
    """
    Estimate one service's position.

    Returns a flat dict, or None when the service is not currently between
    two stations or its current leg cannot be routed.
    """
    meta = svc.get("scheduleMetadata", {})
    identity = meta.get("identity")

    service = get_service_cached(token, identity, run_date)

    locations = service.get("service", {}).get("locations", [])
    calling = []
    for loc in locations:
        name = loc.get("location", {}).get("description")
        if name:
            calling.append(name)

    leg = find_live_leg(service, now)
    if leg is None:
        return None

    a, b = leg
    track = get_route(a["crs"], b["crs"])
    if track is None:
        return None

    pos = estimate_position(track, a["departure"], b["arrival"], now)
    temporal = svc.get("temporalData", {})

    return {
        "uid": identity,
        "headcode": meta.get("trainReportingIdentity"),
        "operator": meta.get("operator", {}).get("name"),
        "runDate": run_date,
        "origin": _endpoint_name(svc, "origin"),
        "destination": _endpoint_name(svc, "destination"),
        "callingPoints": calling,
        "legFrom": a["name"],
        "legTo": b["name"],
        "legFromCrs": a["crs"],
        "legToCrs": b["crs"],
        "lat": round(pos.y, 6),
        "lon": round(pos.x, 6),
        "latenessMinutes": _lateness(temporal),
        "status": temporal.get("status"),
        "estimatedAt": now.isoformat(timespec="seconds"),
        "isEstimate": True,
    }


def compile_serviceboard(svc):
    """Flatten one board service into the shape the departures endpoint returns."""
    meta = svc.get("scheduleMetadata", {})
    temporal = svc.get("temporalData", {})
    arrival = temporal.get("arrival") or {}
    departure = temporal.get("departure") or {}

    return {
        "uid": meta.get("identity"),
        "headcode": meta.get("trainReportingIdentity"),
        "runDate": meta.get("departureDate"),
        "operator": meta.get("operator", {}).get("name"),
        "origin": _endpoint_name(svc, "origin"),
        "destination": _endpoint_name(svc, "destination"),
        "latenessMinutes": _lateness(temporal),
        "isCancelled": arrival.get("isCancelled", False) or departure.get("isCancelled", False),
        "status": temporal.get("status"),
    }


def journey_point(point):
    """
    One calling point carrying both scheduled and actual times.

    The passed flag is true when either actual time is present, meaning the
    train has reported there. That is an observation, unlike the positions
    elsewhere in this module, which are estimates.
    """
    location = point.get("location", {})
    crs = (location.get("shortCodes") or [None])[0]
    if not crs:
        return None

    temporal = point.get("temporalData", {})
    arr = temporal.get("arrival") or {}
    dep = temporal.get("departure") or {}

    def pick(block, *keys):
        for k in keys:
            if block.get(k):
                return block[k]
        return None

    real_arr = arr.get("realtimeActual")
    real_dep = dep.get("realtimeActual")
    platform = (point.get("locationMetadata", {}).get("platform", {}) or {}).get("actual")

    return {
        "crs": crs,
        "name": location.get("description", "?"),
        "schedArr": pick(arr, "scheduleAdvertised", "scheduleInternal"),
        "schedDep": pick(dep, "scheduleAdvertised", "scheduleInternal"),
        "actualArr": real_arr,
        "actualDep": real_dep,
        "passed": bool(real_arr or real_dep),
        "isCancelled": arr.get("isCancelled", False) or dep.get("isCancelled", False),
        "platform": platform,
    }


def build_journey(token, identity, run_date):
    """
    Full journey for one service: calling points plus routed geometry per leg.

    Legs that cannot be routed, or whose route fails the plausibility check,
    are omitted rather than drawn. A gap in the line is honest; a route that
    doubles back through a distant junction is not.
    """
    service = get_service_cached(token, identity, run_date)
    locations = service.get("service", {}).get("locations", [])

    stops = [journey_point(loc) for loc in locations]
    stops = [s for s in stops if s]

    legs = []
    for a, b in zip(stops, stops[1:]):
        track = get_route(a["crs"], b["crs"])
        if track is None:
            continue

        ratio = route_plausibility(track, a["crs"], b["crs"])
        if is_implausible(ratio):
            print(f"implausible route {a['crs']}->{b['crs']}: ratio {ratio:.1f}")
            continue

        legs.append({
            "from": a["crs"],
            "to": b["crs"],
            "passed": b["passed"],
            "ratio": round(ratio, 2) if ratio is not None else None,
            "coordinates": [[round(y, 6), round(x, 6)] for x, y in track.coords],
        })

    return {"uid": identity, "runDate": run_date, "stops": stops, "legs": legs}