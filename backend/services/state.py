from app.stations import load_station_coords

CORRIDOR_STATIONS = ["MAN"]

print("Loading station coordinates")
coords = load_station_coords()

_G = None
_graph_tried = False


def get_graph():
    global _G, _graph_tried
    if _G is None and not _graph_tried:
        _graph_tried = True
        from app.osm_graph import load_rail_graph
        print("cache miss, loading rail graph")
        _G = load_rail_graph()
        if _G is not None:
            print(f"graph is ready: {len(_G.nodes)} nodes")
    return _G

def graph_loaded():
    return _G is not None


last_good = []


def save_last_good(results):
    global last_good
    last_good = results


def get_last_good():
    return last_good