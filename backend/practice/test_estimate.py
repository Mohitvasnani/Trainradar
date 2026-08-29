import webbrowser
from datetime import datetime
import osmnx as ox
import folium
from shapely.geometry import LineString

from osm_graph import load_rail_graph
from stations import load_station_coords
from estimate import estimate_position


if __name__ == "__main__":
    print("Loading rail graph...")
    G = load_rail_graph()
    coords = load_station_coords()

    start_crs, end_crs = "LIV", "EDG"
    start_lat, start_lon = coords[start_crs]
    end_lat, end_lon = coords[end_crs]

    start_node = ox.distance.nearest_nodes(G, start_lon, start_lat)
    end_node = ox.distance.nearest_nodes(G, end_lon, end_lat)
    route = ox.shortest_path(G, start_node, end_node, weight="length")

    route_coords = [(G.nodes[n]["x"], G.nodes[n]["y"]) for n in route]
    track = LineString(route_coords)

    # Test times
    departed = datetime(2026, 6, 30, 16, 50)
    due = datetime(2026, 6, 30, 16, 55)
    now = datetime(2026, 6, 30, 16, 51)

    pos = estimate_position(track, departed, due, now)
    print(f"Estimated position: {pos}")

    # Plot
    m = folium.Map(location=[start_lat, start_lon], zoom_start=14)

    track_latlon = [(lat, lon) for lon, lat in route_coords]
    folium.PolyLine(track_latlon, color="green", weight=4).add_to(m)

    folium.Marker([start_lat, start_lon], popup=start_crs).add_to(m)
    folium.Marker([end_lat, end_lon], popup=end_crs).add_to(m)

    folium.CircleMarker(
        [pos.y, pos.x], radius=8, color="red", fill=True, fill_opacity=1,
        popup="Estimated train position",
    ).add_to(m)

    out = "estimated_train.html"
    m.save(out)
    print(f"Saved {out}")
    webbrowser.open(out)