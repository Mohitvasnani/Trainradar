import math

from services.state import coords


EARTH_RADIUS_M = 6371000
MAX_ROUTE_RATIO = 1.5


def haversine_m(lat1, lon1, lat2, lon2):
    # Calculate distance between two lat/lon points in meters
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def track_length_m(track):
    # Calculate total length of a LineString
    total = 0.0
    pts = list(track.coords)
    for (lon1, lat1), (lon2, lat2) in zip(pts, pts[1:]):
        total += haversine_m(lat1, lon1, lat2, lon2)
    return total


def route_plausibility(track, crs_a, crs_b):
    # Compare actual track length vs straight-line distance
    if crs_a not in coords or crs_b not in coords:
        return None

    lat_a, lon_a = coords[crs_a]
    lat_b, lon_b = coords[crs_b]
    straight = haversine_m(lat_a, lon_a, lat_b, lon_b)
    if straight <= 0:
        return None

    return track_length_m(track) / straight


def is_implausible(ratio):
    # Check if ratio is too high
    return ratio is not None and ratio > MAX_ROUTE_RATIO