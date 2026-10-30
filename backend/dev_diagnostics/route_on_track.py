import webbrowser
import osmnx as ox
import folium
from osm_graph import load_rail_graph
from stations import load_station_coords

if __name__ == "__main__":
    G = load_rail_graph()
    print(f"Graph: {len(G.nodes)} nodes, {len(G.edges)} edges")
    coords = load_station_coords()

    start_lat, start_lon = coords["LIV"]
    end_lat, end_lon = coords["EDG"]

    start_node =ox.distance.nearest_nodes(G, start_lon, start_lat)
    end_node =ox.distance.nearest_nodes(G, end_lon, end_lat)
    print(f"LIV -> {start_node}, EDG -> {end_node}")

    route=ox.shortest_path(G, start_node, end_node, weight="length")
    print(f"Route uses {len(route)} nodes")

    route_coords = [(G.nodes[n]["y"],G.nodes[n]["x"]) for n in route]

    m = folium.Map(location=[start_lat, start_lon],zoom_start=13)
    folium.PolyLine(route_coords, 
                    color="green", 
                    weight=4, 
                    opacity=0.8).add_to(m)
    folium.PolyLine([(start_lat, start_lon), 
                     (end_lat, end_lon)],color="red", 
                     weight=2, 
                     opacity=0.6, 
                     dash_array="5").add_to(m)
    folium.Marker([start_lat, start_lon],
                  popup="LIV").add_to(m)
    folium.Marker([end_lat, end_lon], 
                  popup="EDG").add_to(m)

    out = "routed_track.html"
    m.save(out)
    print(f"Saved {out}")
    webbrowser.open(out)