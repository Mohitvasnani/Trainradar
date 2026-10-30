import webbrowser
from datetime import datetime, date
import osmnx as ox
import folium
from track_builder import build_route_track
from rtt_client import get_access_token, get_location_board, get_service
from stations import load_station_coords
from osm_graph import load_rail_graph
from estimate import estimate_position
from find_current_leg import find_live_leg

if __name__ == "__main__":
    token, _  = get_access_token()
    board =   get_location_board(token, code="MAN")
    services =   board.get("services", [])
    today =  date.today( ).isoformat()
    now= datetime.now()

    print(f"Scanning {len(services)} services\n")

    live=None
    for s in services:
        identity = s["scheduleMetadata"]["identity"]
        try:
            service = get_service(token, 
                                  identity=identity, 
                                  departure_date=today)
        except Exception:  continue
        leg =find_live_leg(service, now)
        if leg:
            live = (identity, leg)
            print(f"Found live service {identity}:{leg[0]['name']} -> {leg[1]['name']}")
            break

    if not live:
        print("No services mid-journey right now.")
        raise SystemExit

    identity, (a, b) = live

    coords = load_station_coords()
    if a["crs"] not in coords or b["crs"] not in coords:
        print("Station has no coordinate, skipping plot.")
        raise SystemExit

    a_lat, a_lon = coords[a["crs"]]
    b_lat, b_lon = coords[b["crs"]]

    G = load_rail_graph()
    a_node = ox.distance.nearest_nodes(G, a_lon, a_lat)
    b_node = ox.distance.nearest_nodes(G, b_lon, b_lat)
    route = ox.shortest_path(G, a_node, b_node, weight="length")

    if not route:
        print("No track route found.")
        raise SystemExit

    track = build_route_track(G, route)

    pos = estimate_position(track, a["departure"], b["arrival"], now)
    print(f"Estimated live position: lat {pos.y}, lon {pos.x}")

    m = folium.Map(location=[a_lat, a_lon], zoom_start=13)
    folium.PolyLine([(lat, lon) for lon, lat in track.coords],
                    color="green", weight=4).add_to(m)
    folium.Marker([a_lat, a_lon], popup=a["name"]).add_to(m)
    folium.Marker([b_lat, b_lon], popup=b["name"]).add_to(m)
    folium.CircleMarker([pos.y, pos.x], radius=8, color="red", fill=True,
                        fill_opacity=1, popup=f"{identity} (live)").add_to(m)

    out = "live_train.html"
    m.save(out)
    print(f"Saved {out}")
    webbrowser.open(out)