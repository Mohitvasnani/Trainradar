import webbrowser
from datetime import datetime, date

import folium
from shapely.geometry import LineString
from shapely.ops import linemerge

from rtt_client import get_access_token, get_location_board, get_service
from stations import load_station_coords
from osm_graph import load_rail_graph
from estimate import estimate_position
from find_current_leg import get_leg_times
from route_leg import route_leg
from live_train import find_live_leg  

def build_full_journey(G, coords, legs):
    """
    Route every consecutive station pair and stitch into one track.
    Returns (full_track, routed_count, skipped_count).
    """
    segments = []
    routed = 0
    skipped = 0

    for i in range(len(legs) - 1):
        crs_a = legs[i]["crs"]
        crs_b = legs[i + 1]["crs"]

        leg_track = route_leg(G, coords, crs_a, crs_b)
        if leg_track is not None:
            segments.append(leg_track)
            routed += 1
        else:
            skipped += 1

    if not segments:
        return None, routed, skipped

    # Stitch all leg-tracks into one line
    full_track = linemerge(segments)
    return full_track, routed, skipped


if __name__ == "__main__":
    token, _ = get_access_token()
    coords = load_station_coords()

    # Find a live service at Manchester
    board = get_location_board(token, code="MAN")
    services = board.get("services", [])
    today = date.today().isoformat()
    now = datetime.now()

    print(f"Scanning {len(services)} services...")
    live_services = []
    for s in services:
        identity = s["scheduleMetadata"]["identity"]
        try:
            service = get_service(token, identity=identity, departure_date=today)
        except Exception:
            continue
        leg = find_live_leg(service, now)
        if leg:
            a, b = leg
            live_services.append((identity, service, a, b))

        

    if not live_services:
        print("No live service found right now — run again.")
        raise SystemExit
    print(f"\nFound {len(live_services)} live services:\n")
    for i, (ident, svc, a, b) in enumerate(live_services):
        print(f"  [{i}]  {ident}:  {a['name']} -> {b['name']}")
    print()

    identity, service = live_services
    locations = service.get("service", {}).get("locations", [])
    legs = [get_leg_times(loc) for loc in locations]
    
    
    print(f"Service {identity}: {len(legs)} stations\n")
    for leg in legs:
        t = leg["departure"] or leg["arrival"]
        time_str = t.strftime("%H:%M") if t else "  ?  "
        print(f"  {time_str}  {leg['name']}")
    print()

    print("Loading rail graph...")
    G = load_rail_graph()

    # Build the whole-journey track
    full_track, routed, skipped = build_full_journey(G, coords, legs)
    print(f"Routed {routed} legs, skipped {skipped}")

    if full_track is None:
        print("Could not build a journey track.")
        raise SystemExit

    # Find the current leg and estimate the train's position on it
    current = find_live_leg(service, now)
    a, b = current
    leg_track = route_leg(G, coords, a["crs"], b["crs"])
    pos = estimate_position(leg_track, a["departure"], b["arrival"], now)

    # --- Plot ---
    # Centre on the train
    m = folium.Map(location=[pos.y, pos.x], zoom_start=11)

    # The whole journey (blue, faint) — handle both Line and MultiLine
    def draw_line(geom, **kwargs):
        latlon = [(lat, lon) for lon, lat in geom.coords]
        folium.PolyLine(latlon, **kwargs).add_to(m)

    if full_track.geom_type == "LineString":
        draw_line(full_track, color="blue", weight=3, opacity=0.5)
    else:  # MultiLineString — draw each piece
        for part in full_track.geoms:
            draw_line(part, color="blue", weight=3, opacity=0.5)

    # Station markers
    for leg in legs:
        if leg["crs"] in coords:
            lat, lon = coords[leg["crs"]]
            folium.CircleMarker([lat, lon], radius=3, color="gray",
                                fill=True, popup=leg["name"]).add_to(m)

    # The train (red)
    folium.CircleMarker([pos.y, pos.x], radius=8, color="red", fill=True,
                        fill_opacity=1, popup=f"{identity} (live)").add_to(m)

    out = "whole_journey.html"
    m.save(out)
    print(f"Saved {out} — opening")
    webbrowser.open(out)