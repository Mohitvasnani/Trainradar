"""
Distance and route plausibility.

Distances use the haversine formula on a spherical Earth. That is roughly
0.3% out against a true ellipsoidal calculation, which does not matter here
because these values are only ever compared as a ratio. The snap distance
check in route_leg uses geopy's geodesic instead, because there an absolute
threshold in metres is being applied.
"""

import math

from services.state import coords


EARTH_RADIUS_M = 6371000

# Routed length divided by straight-line station distance. Calibrated from
# observed values: valid legs clustered between 0.98 and 1.20, while routes
# that doubled back measured 1.74, 3.3 and 5.6. A threshold of 1.5 separates
# the two clusters with margin on both sides.
MAX_ROUTE_RATIO = 1.5


def haversine_m(lat1, lon1, lat2, lon2):
    """Great-circle distance in metres between two lat/lon points."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def track_length_m(track):
    """Total length of a LineString whose coordinates are (lon, lat)."""
    total = 0.0
    pts = list(track.coords)
    for (lon1, lat1), (lon2, lat2) in zip(pts, pts[1:]):
        total += haversine_m(lat1, lon1, lat2, lon2)
    return total


def route_plausibility(track, crs_a, crs_b):
    """
    Ratio of routed track length to straight-line station distance.

    A route that doubles back or detours via a distant junction shows up as
    a high ratio. Returns None when either station has no coordinates, or
    when the two stations sit at the same point.
    """
    if crs_a not in coords or crs_b not in coords:
        return None

    lat_a, lon_a = coords[crs_a]
    lat_b, lon_b = coords[crs_b]
    straight = haversine_m(lat_a, lon_a, lat_b, lon_b)
    if straight <= 0:
        return None

    return track_length_m(track) / straight


def is_implausible(ratio):
    """True when a ratio is known and exceeds the calibrated threshold."""
    return ratio is not None and ratio > MAX_ROUTE_RATIO