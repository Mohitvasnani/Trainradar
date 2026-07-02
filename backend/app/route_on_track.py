import webbrowser
import osmnx as ox
import folium

from osm_graph import load_rail_graph
from stations import load_station_coords


if __name__ == "__main__":
    print("Loading rail graph...")
    G = load_rail_graph()
    print(f"Graph: {len(G.nodes)} nodes, {len(G.edges)} edges")

    coords = load_station_coords()

    # Two stations both inside the Liverpool bbox
    start_crs, end_crs = "LIV", "EDG"   # Lime Street -> Edge Hill
    start_lat, start_lon = coords[start_crs]
    end_lat, end_lon = coords[end_crs]

    # Snap each station to its nearest node on the rail graph
    # (osmnx nearest_nodes takes X=lon, Y=lat)
    start_node = ox.distance.nearest_nodes(G, start_lon, start_lat)
    end_node = ox.distance.nearest_nodes(G, end_lon, end_lat)
    print(f"{start_crs} -> node {start_node},  {end_crs} -> node {end_node}")

    # Shortest path along the track between the two nodes
    route = ox.shortest_path(G, start_node, end_node, weight="length")
    print(f"Route uses {len(route)} nodes along the track")

    # Get the (lat, lon) of each node on the routed path
    route_coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route]

    # Build a map
    m = folium.Map(location=[start_lat, start_lon], zoom_start=13)

    # The ACTUAL track path (green, following the rails)
    folium.PolyLine(route_coords, color="green", weight=4, opacity=0.8,
                    popup="Actual track path").add_to(m)

    # The NAIVE straight line between the two stations (red, for comparison)
    folium.PolyLine([(start_lat, start_lon), (end_lat, end_lon)],
                    color="red", weight=2, opacity=0.6, dash_array="5",
                    popup="Straight line").add_to(m)

    # Mark the two stations
    for crs, lat, lon in [(start_crs, start_lat, start_lon), (end_crs, end_lat, end_lon)]:
        folium.Marker([lat, lon], popup=crs).add_to(m)

    out = "routed_track.html"
    m.save(out)
    print(f"Saved {out} — opening")
    webbrowser.open(out)