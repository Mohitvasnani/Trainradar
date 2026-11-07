import os

NORTH, SOUTH, EAST, WEST = 60.90, 49.90, 1.80, -8.20

RAIL_FILTER = (
    '["railway"~"rail"]'
    '["railway"!~"tram|light_rail|subway|miniature|monorail|funicular"]'
    '["service"!~"yard|siding|spur|crossover"]'
    '["usage"!~"industrial"]'
)

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

    XML_PATH = os.path.join(
        os.path.dirname(__file__), "..", "..", "osm-data", "gb-rail.osm"
    )

    print("building rail graph from local OSM extract..")
    G = ox.graph_from_xml(XML_PATH, retain_all=True, simplify=False)
    ox.save_graphml(G, CACHE_PATH)
    print(f"graph built to {CACHE_PATH}")
    return G