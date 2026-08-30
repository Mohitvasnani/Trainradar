from geopy.distance import geodesic


def track_length_km(track):
    """
    Real-world length of a track (LineString in lon/lat) in kilometres.
    Walks the line's points and sums the geodesic distance between each pair.
    """
    total = 0.0
    coords = list(track.coords)   # list of (lon, lat) points

    for i in range(len(coords) - 1):
        lon1, lat1 = coords[i]
        lon2, lat2 = coords[i + 1]
        # geodesic wants (lat, lon) — note the flip
        total += geodesic((lat1, lon1), (lat2, lon2)).km

    return total


def straight_line_km(coord_a, coord_b):
    """Straight-line (as-the-crow-flies) distance between two (lat, lon) points, in km."""
    return geodesic(coord_a, coord_b).km


def plausibility_ratio(track, coord_a, coord_b):
    """
    How much longer is the routed track than the straight line?
    A ratio near 1 means direct. A big ratio means a suspicious detour.
    """
    routed = track_length_km(track)
    straight = straight_line_km(coord_a, coord_b)
    if straight == 0:
        return None
    return routed / straight


if __name__ == "__main__":
    from osm_graph import load_rail_graph
    from stations import load_station_coords
    from route_leg import route_leg

    G = load_rail_graph()
    coords = load_station_coords()

    # Test a few legs: a normal one, and the suspicious Bredbury -> Brinnington one
    test_legs = [
        ("MAN", "SPT"),   # Manchester Piccadilly -> Stockport (should be sensible)
        ("BDY", "BNT"),   # Bredbury -> Brinnington (suspected detour)
    ]

    for crs_a, crs_b in test_legs:
        track = route_leg(G, coords, crs_a, crs_b)
        if track is None:
            print(f"{crs_a} -> {crs_b}: could not route")
            continue

        routed = track_length_km(track)
        straight = straight_line_km(coords[crs_a], coords[crs_b])
        ratio = routed / straight if straight else 0

        flag = "  <-- SUSPICIOUS" if ratio > 3 else ""
        print(f"{crs_a} -> {crs_b}:  routed {routed:.2f} km, "
              f"straight {straight:.2f} km, ratio {ratio:.1f}x{flag}")