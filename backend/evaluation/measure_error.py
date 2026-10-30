import argparse
import csv
import math
import sys
from datetime import datetime, date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "app"))
from rtt_client import get_access_token, get_location_board, get_service
from stations import load_station_coords
from osm_graph import load_rail_graph
from route_leg import route_leg
from estimate import estimate_position

SAMPLES_PER_LEG = 5
EARTH_RADIUS_M = 6371000


def haversine_m(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def parse_time(value):
    return datetime.fromisoformat(value) if value else None


def leg_endpoint(loc):
    location = loc.get("location", {})
    crs = (location.get("shortCodes") or [None])[0]
    if not crs:
        return None
    temporal= loc.get("temporalData", {})
    arr = temporal.get("arrival") or {}
    dep = temporal.get("departure") or {}

    return { "crs": crs,
        "name": location.get("description", "?"),
        "interpolated": temporal.get("isInterpolated", False),
        "sched_arr": parse_time(arr.get("scheduleAdvertised") or arr.get("scheduleInternal")),
        "sched_dep": parse_time(dep.get("scheduleAdvertised") or dep.get("scheduleInternal")),
        "actual_arr": parse_time(arr.get("realtimeActual")),
        "actual_dep": parse_time(dep.get("realtimeActual")) }


def evaluate_leg(track, a, b):
    sched_dep, sched_arr = a["sched_dep"], b["sched_arr"]
    actual_dep, actual_arr = a["actual_dep"], b["actual_arr"]

    sched_secs = (sched_arr - sched_dep).total_seconds()
    actual_secs = (actual_arr - actual_dep).total_seconds()

    for i in range(1, SAMPLES_PER_LEG + 1):
        fraction = i / (SAMPLES_PER_LEG + 1)
        sample_time = actual_dep + (actual_arr - actual_dep) * fraction

        p_sched = estimate_position(track, sched_dep, sched_arr, sample_time)
        p_actual = estimate_position(track, actual_dep, actual_arr, sample_time)

        yield {
            "leg_from": a["crs"],
            "leg_to": b["crs"],
            "leg_from_name": a["name"],
            "leg_to_name": b["name"],
            "sample_time": sample_time.isoformat(timespec="seconds"),
            "sample_fraction": round(fraction, 3),
            "sched_duration_s": int(sched_secs),
            "actual_duration_s": int(actual_secs),
            "duration_diff_s": int(actual_secs - sched_secs),
            "dep_lateness_s": int((actual_dep - sched_dep).total_seconds()),
            "sched_lat": round(p_sched.y, 6),
            "sched_lon": round(p_sched.x, 6),
            "actual_lat": round(p_actual.y, 6),
            "actual_lon": round(p_actual.x, 6),
            "error_m": round(haversine_m(p_sched.y, p_sched.x, p_actual.y, p_actual.x), 1),
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--station", default="MAN")
    ap.add_argument("--max-services", type=int, default=20)
    ap.add_argument("--out", default="error_results.csv")
    args = ap.parse_args()

    coords = load_station_coords()
    G = load_rail_graph()
    print(f"Graph ready: {len(G.nodes)} nodes")
    token, _ = get_access_token()
    run_date = date.today().isoformat()

    board = get_location_board(token, code=args.station)
    services = board.get("services", [])
    print(f"Found {len(services)} services at {args.station}, sampling up to {args.max_services}\n")

    route_cache = {}
    rows = []
    total_legs = used_legs = no_actual = interpolated = unroutable = bad_duration = 0

    for svc in services[:args.max_services]:
        identity = svc.get("scheduleMetadata", {}).get("identity")
        if not identity:
            continue

        try:
            service = get_service(token, identity=identity, departure_date=run_date)
        except Exception as e:
            print(f"{identity}: failed fetch({e})")
            continue

        locations = service.get( "service" , {}).get( "locations" , [])
        points=[leg_endpoint( loc ) for loc in locations]
        points= [p for p in points if p]

        for a, b in zip(points,points[ 1: ]):
            total_legs += 1

            if (a["actual_dep"] is None or b["actual_arr"] is None or
                a["sched_dep"] is None or b["sched_arr"] is None):
                no_actual +=1
                continue

            if a["interpolated"] or b["interpolated"]:
                interpolated += 1
                continue

            sched_secs  =  (b["sched_arr"]-a["sched_dep"]).total_seconds()
            actual_secs  =   (b["actual_arr"] - a["actual_dep"]).total_seconds()
            if sched_secs<= 0 or actual_secs <= 0:
                bad_duration+=1
                continue

            key=(a["crs"], b["crs"])
            if key not in route_cache:
                try:
                    track, _, _ =route_leg (G , coords , a["crs"], b["crs"])
                except Exception:
                    track = None
                route_cache[key] =track
            track= route_cache[key]

            if track is None:
                unroutable+=1
                continue

            for row in evaluate_leg (track, a, b):
                row["uid"] = identity
                row["run_date"] = run_date
                rows.append(row)
            used_legs += 1

    if not rows:
        print("No evaluable legs found.")
        return

    fieldnames = ["uid", "run_date", "leg_from", "leg_to", "leg_from_name",
                  "leg_to_name", "sample_time", "sample_fraction",
                  "sched_duration_s", "actual_duration_s", "duration_diff_s",
                  "dep_lateness_s", "sched_lat", "sched_lon",
                  "actual_lat", "actual_lon", "error_m"]

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    errors = sorted(r["error_m"] for r in rows)
    n = len(errors)
    mean = sum(errors) / n
    median = errors[n // 2]
    p90 = errors[int(n * 0.9)]

    print(f"\nWrote {n} observations from {used_legs} legs to {args.out}")
    print(f"Legs: total={total_legs}, used={used_legs}, no actual={no_actual}, "
          f"interpolated={interpolated}, unroutable={unroutable}, bad duration={bad_duration}")
    print(f"Error (m): mean={mean:.1f}, median={median:.1f}, p90={p90:.1f}, max={errors[-1]:.1f}")


if __name__ == "__main__":
    main()