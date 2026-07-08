####
import osmnx as ox
from track_builder import build_route_track

def route_leg(G, coords, crs_a, crs_b):
    """ 
    route the track from one station to next A -> B
    returns a curved string else none
    """

    # station coordinates
    if crs_a not in coords or crs_b not in coords:
        return None
    
    a_lat, a_lon = coords[crs_a]
    b_lat, b_lon = coords[crs_b]

    # place each station to the nearest nodes in the graph

    a_node = ox.distance.nearest_nodes(G, a_lon, a_lat)
    b_node = ox.distance.nearest_nodes(G, b_lon, b_lat)

    #find shortest path

    route = ox.shortest_path(G, a_node, b_node, weight="length")
    if not route or len(route)<2:
        return None
    
    #build the track
    return build_route_track(G, route)

if  __name__ == "__main__":
    from osm_graph import load_rail_graph
    from stations import load_station_coords

    G = load_rail_graph()
    coords = load_station_coords()

    #quick testing  routing one leg
    track = route_leg(G, coords, "MAN", "SPT")
    if track:
        print(f"Routed leg with {len(track.coords)} points")
    else:
        print("Could not route that leg")
