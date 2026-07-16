####
import osmnx as ox
from track_builder import build_route_track
from geopy.distance import geodesic

def route_leg(G, coords, crs_a, crs_b, max_snap_m=300):
    """ 
    route the track from one station to next A -> B
    returns a curved string else none


    Returns (track, snap_a_m, snap_b_m) where the snap distances tell you
    how far each station had to reach to find a node on the graph.
    Returns (None, snap_a, snap_b) if it can't route or the snap is too far.
    """

    # station coordinates
    if crs_a not in coords or crs_b not in coords:
        return None, None, None
    
    a_lat, a_lon = coords[crs_a]
    b_lat, b_lon = coords[crs_b]

    # place each station to the nearest nodes in the graph

    a_node = ox.distance.nearest_nodes(G, a_lon, a_lat)
    b_node = ox.distance.nearest_nodes(G, b_lon, b_lat)

    # How far away did each station actually snap?

    a_snap = geodesic((a_lat, a_lon),
                      (G.nodes[a_node]["y"], G.nodes[a_node]["x"] )).m
    b_snap = geodesic((b_lat, b_lon),
                      (G.nodes[b_node]["y"], G.nodes[b_node]["x"] )).m
# If either station snapped too far, the route can't be trusted
    if a_snap>max_snap_m or b_snap>max_snap_m:
        return None, a_snap, b_snap
    route = ox.shortest_path(G, a_node, b_node, weight="length")
    if not route or len(route)<2:
        return None, a_snap, b_snap
    track = build_route_track(G, route)
    return track, a_snap, b_snap
    

if  __name__ == "__main__":
    from osm_graph import load_rail_graph
    from stations import load_station_coords

    G = load_rail_graph()
    coords = load_station_coords()

    #quick testing  routing one leg
    for crs_a, crs_b in [("MAN", "SPT"), ("BDY", "BNT")]:
        track, snap_a, snap_b = route_leg(G, coords, crs_a, crs_b)
        if track:
            print(f"{crs_a}->{crs_b}: OK  "
                  f"(snaps: {snap_a:.0f} m, {snap_b:.0f} m)")
        else:
            print(f"{crs_a}->{crs_b}: REJECTED  "
                  f"(snaps: {snap_a:.0f} m, {snap_b:.0f} m)")