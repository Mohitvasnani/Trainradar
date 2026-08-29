import os
import osmnx as ox

ox.settings.max_query_area_size = 50_000_000_000

NORTH, SOUTH, EAST, WEST = 55.00, 52.90, -1.90, -3.95


RAIL_FILTER='["railway"~"rail"]["railway"!~"tram|light_rail|subway|miniature|monorail|funicular"]'

CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "rail_graph.graphml")


def load_rail_graph():  
    if os.path.exists(CACHE_PATH):
        print("loading rail graph from cache")
        return ox.load_graphml(CACHE_PATH)
    

    print("downloadingrail graph from OSM..")
    bbox = (WEST, SOUTH, EAST, NORTH)
    G = ox.graph_from_bbox(
        bbox,
        custom_filter=RAIL_FILTER,
        retain_all=True, simplify=False)

    ox.save_graphml(G, CACHE_PATH)
    print(f"Graph downloaded in {CACHE_PATH}")
    return G


# if __name__ == "__main__":
#     G = load_rail_graph()
#     print(f"Graph loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")