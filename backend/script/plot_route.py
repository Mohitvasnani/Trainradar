import webbrowser
from datetime import date

import folium

from rtt_client import get_access_token, get_location_board, get_service
from stations import load_station_coords


def build_route_points(service, coords):
    """Turn a service's timing points into a list of (name, lat, lon, time)."""
    points = []
    locations = service.get("service", {}).get("locations", [])
    for loc in locations:
        location = loc.get("location", {})
        name = location.get("description", "?")
        short_codes = location.get("shortCodes") or []
        crs = short_codes[0] if short_codes else None

        temporal = loc.get("temporalData", {})

        def pick(kind):
            block = temporal.get(kind) or {}
            return block.get("scheduleAdvertised") or block.get("scheduleInternal")

        time = pick("departure") or pick("arrival") or pick("pass") or "?"

        if crs and crs in coords:
            lat, lon = coords[crs]
            points.append((name, lat, lon, time))
    return points


if __name__ == "__main__":
    coords = load_station_coords()
    token, _ = get_access_token()

    # Find a live service at Liverpool Lime Street
    board = get_location_board(token, code="LIV")
    services = board.get("services", [])
    identity = services[0]["scheduleMetadata"]["identity"]
    today = date.today().isoformat()
    service = get_service(token, identity=identity, departure_date=today)

    points = build_route_points(service, coords)
    print(f"Service {identity}: plotted {len(points)} of its timing points")

    if not points:
        print("No mappable points found.")
        raise SystemExit

    # Centre the map on the first point
    start_lat, start_lon = points[0][1], points[0][2]
    m = folium.Map(location=[start_lat, start_lon], zoom_start=10)

    # Draw the route line
    line = [(lat, lon) for _, lat, lon, _ in points]
    folium.PolyLine(line, color="blue", weight=3, opacity=0.7).add_to(m)

    # Add a marker at each station
    for name, lat, lon, time in points:
        folium.CircleMarker(
            location=[lat, lon],
            radius=5,
            color="red",
            fill=True,
            popup=f"{name}<br>{time}",
        ).add_to(m)

    out = "route_map.html"
    m.save(out)
    print(f"Map saved to {out} — opening in browser")
    webbrowser.open(out)