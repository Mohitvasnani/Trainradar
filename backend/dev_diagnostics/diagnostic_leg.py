import osmnx as ox
import folium
import webbrowser
from geopy.distance import geodesic
from osm_graph import load_rail_graph
from stations import load_station_coords
from route_leg import route_leg
from distances import track_length_km, straight_line_km

G=load_rail_graph()
coords = load_station_coords()

CRS_A,CRS_B = "BDY", "BNT"

a_lat, a_lon =coords[CRS_A]
b_lat, b_lon = coords[CRS_B]

a_node = ox.distance.nearest_nodes(G, a_lon, a_lat)
b_node = ox.distance.nearest_nodes(G, b_lon, b_lat)

a_node_lat, a_node_lon = G.nodes[a_node]["y"], G.nodes[a_node]["x"]
b_node_lat, b_node_lon = G.nodes[b_node]["y"], G.nodes[b_node]["x"]

a_snap_dist = geodesic((a_lat, a_lon), (a_node_lat, a_node_lon)).m
b_snap_dist = geodesic((b_lat, b_lon), (b_node_lat, b_node_lon)).m

print(f"{CRS_A} snapped to node {a_node}, {a_snap_dist:.0f} m from the station")
print(f"{CRS_B} snapped to node {b_node}, {b_snap_dist:.0f} m from the station")
print()

route = ox.shortest_path(G, a_node, b_node, weight="length")
print(f"Route uses {len(route)} nodes")

track, _, _ = route_leg(G, coords, CRS_A, CRS_B)
routed_km = track_length_km(track)
straight_km = straight_line_km((a_lat, a_lon), (b_lat, b_lon))
print(f"Routed {routed_km:.2f} km vs straight {straight_km:.2f} km "
      f"(ratio {routed_km/straight_km:.1f}x)")
print()

if G.has_edge(a_node, b_node):
    print("The two  nodes are connected by  edge")
else:
    print("The two snapped nodes are NOT connected")
    print(f"Shortest path {len(route)} nodes no.")

m = folium.Map(location=[(a_lat + b_lat)/2, (a_lon + b_lon) / 2], zoom_start=14)

folium.PolyLine([(lat, lon) for lon, lat in track.coords],
                color="red", weight=4, opacity=0.8,
                popup=f"Routed:{routed_km:.1f} km").add_to(m)

folium.PolyLine([(a_lat, a_lon), (b_lat, b_lon)],
                color="black", weight=2, dash_array="5",
                popup=f"Straight: {straight_km:.1f} km").add_to(m)

folium.Marker([a_lat, a_lon], popup=f"{CRS_A} station").add_to(m)
folium.Marker([b_lat, b_lon], popup=f"{CRS_B} station").add_to(m)

folium.CircleMarker([a_node_lat, a_node_lon], radius=6, color="orange",
                    fill=True, popup=f"{CRS_A} snapped here ({a_snap_dist:.0f} m away)").add_to(m)
folium.CircleMarker([b_node_lat, b_node_lon], radius=6, color="orange",
                    fill=True, popup=f"{CRS_B} snapped here ({b_snap_dist:.0f} m away)").add_to(m)

m.save("diagnose_leg.html")
print("Saved diagnose_leg.html")
webbrowser.open("diagnose_leg.html")