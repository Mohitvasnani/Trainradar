from shapely.geometry import LineString
from shapely.ops import linemerge


def build_route_track(G, route):
    """
    Turn a route (list of node IDs) into a properly curved LineString,
    following each edge's real geometry where it exists.
    """
    segments = []

    # Walk consecutive node pairs along the route
    for u, v in zip(route[:-1], route[1:]):
        # Get the edge data between u and v.
        # (There can be multiple edges between two nodes; take the first.)
        edge_data = G.get_edge_data(u, v)
        first_key = list(edge_data.keys())[0]
        data = edge_data[first_key]

        if "geometry" in data:
            # This edge stored its real curved shape — use it
            segments.append(data["geometry"])
        else:
            # No stored curve — fall back to a straight line node->node
            point_u = (G.nodes[u]["x"], G.nodes[u]["y"])
            point_v = (G.nodes[v]["x"], G.nodes[v]["y"])
            segments.append(LineString([point_u, point_v]))

    # Stitch all the little segments into one continuous line
    merged = linemerge(segments)
    return merged


if __name__ == "__main__":
    import osmnx as ox
    from osm_graph import load_rail_graph
    from stations import load_station_coords

    G = load_rail_graph()
    coords = load_station_coords()

    a_lat, a_lon = coords["LIV"]
    b_lat, b_lon = coords["EDG"]

    a_node = ox.distance.nearest_nodes(G, a_lon, a_lat)
    b_node = ox.distance.nearest_nodes(G, b_lon, b_lat)
    route = ox.shortest_path(G, a_node, b_node, weight="length")

    track = build_route_track(G, route)
    print(f"Built track with {len(track.coords)} points")
    print(f"(Straight node-to-node would have been only {len(route)} points)")
    # --- Plot curvy vs straight to compare ---
    import folium
    import webbrowser

    m = folium.Map(location=[a_lat, a_lon], zoom_start=14)

    # NEW curvy track (green) — follows the real rails
    curvy = [(lat, lon) for lon, lat in track.coords]
    folium.PolyLine(curvy, color="green", weight=4, opacity=0.9,
                    popup="Curvy (real track)").add_to(m)

    # OLD straight version (red dashed) — node-to-node only
    straight = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route]
    folium.PolyLine(straight, color="red", weight=2, opacity=0.7,
                    dash_array="5", popup="Straight (node-to-node)").add_to(m)

    folium.Marker([a_lat, a_lon], popup="LIV").add_to(m)
    folium.Marker([b_lat, b_lon], popup="EDG").add_to(m)

    m.save("curvy_vs_straight.html")
    print("Saved curvy_vs_straight.html — opening")
    webbrowser.open("curvy_vs_straight.html")