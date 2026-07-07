import os
import osmnx as ox

# Bounding box around Liverpool (north, south, east, west)
NORTH, SOUTH, EAST, WEST = 53.55, 53.05, -2.15, -3.90

# we just fetch the railway instaed of roads
RAIL_FILTER = '["railway"~"rail"]'


CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "rail_graph.graphml")


def load_rail_graph():
    """Load the rail network. Use the cached file if it exists, else download and cache it."""
    if os.path.exists(CACHE_PATH):
        print("Loading rail graph from cache...")
        return ox.load_graphml(CACHE_PATH)

    print("No cache found — downloading rail graph from OpenStreetMap...")
    bbox = (WEST, SOUTH, EAST, NORTH)   # (left, bottom, right, top)
    G = ox.graph_from_bbox(
        bbox,
        custom_filter=RAIL_FILTER,
        retain_all=True,
        simplify=True,
    )

    # Save it so next time is instant
    ox.save_graphml(G, CACHE_PATH)
    print(f"Graph downloaded and cached to {CACHE_PATH}")
    return G


if __name__ == "__main__":
    G = load_rail_graph()
    print(f"Graph loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")