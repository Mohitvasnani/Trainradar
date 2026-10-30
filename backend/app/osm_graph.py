import os

NORTH, SOUTH, EAST, WEST = 55.00, 52.90, -1.90, -3.95

RAIL_FILTER = '["railway"~"rail"]["railway"!~"tram|light_rail|subway|miniature|monorail|funicular"]'

CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "rail_graph.graphml")


def load_rail_graph(allow_download=False):
    if not os.path.exists(CACHE_PATH):
        if not allow_download:
            print(f"no rail graph at {CACHE_PATH}")
            return None
        return _download_graph()

    try:
        import osmnx as ox
    except ImportError:
        print("osmnx not installed, running without the graph")
        return None

    print("loading rail graph from cache")
    return ox.load_graphml(CACHE_PATH)


def _download_graph():
    import osmnx as ox
    ox.settings.max_query_area_size = 50_000_000_000

    print("downloading rail graph from OSM..")
    bbox = (WEST, SOUTH, EAST, NORTH)
    G = ox.graph_from_bbox(
        bbox,
        custom_filter=RAIL_FILTER,
        retain_all=True,
        simplify=False)
    ox.save_graphml(G, CACHE_PATH)
    print(f"graph downloaded to {CACHE_PATH}")
    return G