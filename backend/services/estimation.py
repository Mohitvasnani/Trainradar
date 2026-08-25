"""
Position estimation and selecting response format
"""

from datetime import datetime, timedelta

  

from app.estimate import estimate_position
from app.find_current_leg import find_live_leg
from services.cache import get_service_cached, get_route
from services.geometry import route_plausibility, is_implausible



GraceTime = timedelta( minutes=30 )


def is_train_running (svc,now):
   
    temp =svc.get("temporalData",{})
    arr = temp.get("arrival") or{}


    departure = temp.get("departure") or {}
    if arr.get("isCancelled") or departure.get("isCancelled"):  return False

    origin = (svc.get("origin") or [{}])[0]
    dest = (svc.get("destination") or [{}])[0]
    origin_dep= (origin.get("temporalData") or{}).get("scheduleAdvertised")
    dest_arr = (dest.get("temporalData") or {}).get("scheduleAdvertised")
    if not origin_dep or not dest_arr:
        return False

    start = datetime.fromisoformat(origin_dep)
    end = datetime.fromisoformat(dest_arr)+GraceTime
    return start <= now <=end


def get_lateness(temporal):    
    arr = temporal.get("arrival") or {}
    departure =temporal.get("departure") or {}
    late = departure.get("realtimeAdvertisedLateness")
    if late is None:
        late = arr.get("realtimeAdvertisedLateness")
    return late


def get_station_name(svc, key):
    entries = svc.get(key) or [{}]
    return entries[0].get("location",{}).get("description")


def estimate_trainPosition(svc, token, run_date,now):
  
    meta = svc.get("scheduleMetadata", {})
    identity = meta.get("identity")

    service=get_service_cached(token, identity, run_date)

    locations =service.get("service", {}).get("locations", [])
    calling = []
    for loc in locations:
        name = loc.get("location", {}).get("description")
        if name:
            calling.append(name)

    leg = find_live_leg(service, now)
    if leg is None: return None
    a,b = leg
    track = get_route(a["crs"], b["crs"])
    if track is None:
        return None


    pos = estimate_position(track, a["departure"], b["arrival"], now)
    temporal = svc.get("temporalData", {})

    return{
        "uid": identity,
        "headcode": meta.get("trainReportingIdentity"),
        "operator": meta.get("operator", {}).get("name"),
        "runDate": run_date,
        "origin": get_station_name(svc, "origin"),
        "destination": get_station_name(svc, "destination"),
        "callingPoints": calling,
        "legFrom": a["name"], "legTo": b["name"],
        "legFromCrs": a["crs"],
        "legToCrs": b["crs"],
        "lat":round(pos.y, 6),
        "lon":round(pos.x, 6),
        "latenessMinutes":get_lateness(temporal),
        "status": temporal.get("status"),
        "estimatedAt": now.isoformat(timespec="seconds"),
        "isEstimate": True}


def full_depboard(svc):
   
    meta = svc.get("scheduleMetadata", {})
    temp = svc.get("temporalData", {})
    arrival = temp.get("arrival") or {}
    departure = temp.get("departure") or {}

    return{"uid": meta.get("identity"),
        "headcode": meta.get("trainReportingIdentity"),
        "runDate": meta.get("departureDate"),

        "operator": meta.get("operator", {}).get("name"),
        "origin": get_station_name(svc, "origin"),
        "destination": get_station_name(svc,"destination"),
        "latenessMinutes": get_lateness(temp),
        "isCancelled": arrival.get("isCancelled", False)or departure.get("isCancelled", False),
        "status": temp.get("status")}


def format_stop(point):
  
    location = point.get("location", {})
    crs = (location.get("shortCodes") or [None])[0]
    if not crs:
        return None

    temp= point.get("temporalData", {})
    arr =temp.get("arrival") or {}
    dep =temp.get("departure") or {}

    real_arr = arr.get("realtimeActual")
    real_dep= dep.get("realtimeActual")
    platform = (point.get("locationMetadata",{}).get("platform",{})or{}).get("actual")

    return{
        "crs": crs,
        "name": location.get("description", "?"),
        "schedArr": arr.get("scheduleAdvertised") or arr.get("scheduleInternal"),
        "schedDep": dep.get("scheduleAdvertised") or dep.get("scheduleInternal"),
        "actualArr": real_arr,
        "actualDep": real_dep,
        "passed": bool(real_arr or real_dep),
        "isCancelled": arr.get("isCancelled", False) or dep.get("isCancelled", False),
        "platform": platform}


def journey_building(token,identity,run_date):
    ser = get_service_cached(token, identity,run_date)
    locations =ser.get("service", {}).get("locations", [])
    stops=[format_stop(loc) for loc in locations]
    stops =[s for s in stops if s]

    legs=[]
    for a, b in zip(stops, stops[1:]):
        track = get_route(a["crs"], b["crs"])
        if track is None: continue

        ratio = route_plausibility(track, a["crs"], b["crs"])
        if is_implausible(ratio): continue

        legs.append({"from": a["crs"],
            "to": b["crs"],

            "passed": b["passed"],
            "ratio": round(ratio, 2) if ratio is not None else None,
            "coordinates": [[round(y, 6), round(x, 6)] for x, y in track.coords]})

    return {"uid": identity, "runDate":run_date, "stops":stops, "legs":legs}