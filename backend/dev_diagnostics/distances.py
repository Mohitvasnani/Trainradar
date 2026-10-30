from geopy.distance import geodesic


def track_length_km(track):
    total = 0.0
    coords = list(track.coords)

    for i in range(len(coords) - 1):
        lon1, lat1 = coords[i]
        lon2, lat2 = coords[i + 1]
        total += geodesic((lat1, lon1), (lat2, lon2)).km

    return total


def straight_line_km(coord_a, coord_b):
    return geodesic(coord_a, coord_b).km


def plausibility_ratio(track, coord_a, coord_b):
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

    test_legs = [
        ("MAN", "SPT"),
        ("BDY", "BNT"),
    ]

    for crs_a, crs_b in test_legs:
        track, _, _ = route_leg(G, coords, crs_a, crs_b)
        if track is None:
            print(f"{crs_a} -> {crs_b}: could not route")
            continue

        routed = track_length_km(track)
        straight = straight_line_km(coords[crs_a], coords[crs_b])
        ratio = routed / straight if straight else 0

        flag = "  <-- SUSPICIOUS" if ratio > 3 else ""
        print(f"{crs_a} -> {crs_b}:  routed {routed:.2f} km, "
              f"straight {straight:.2f} km, ratio {ratio:.1f}x{flag}")