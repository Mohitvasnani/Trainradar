import osmnx as ox

# Bounding box around Liverpool (north, south, east, west)
NORTH, SOUTH, EAST, WEST = 53.48, 53.35, -2.85, -3.05

# Custom filter: fetch railway=rail ways instead of roads
RAIL_FILTER = '["railway"~"rail"]'


def load_rail_graph():
    """Load the rail network within the bounding box as a connected graph."""
    # Newer OSMnx expects bbox as (west, south, east, north)
    bbox = (WEST, SOUTH, EAST, NORTH)   # (-3.05, 53.35, -2.85, 53.48)
    G = ox.graph_from_bbox(
        bbox,
        custom_filter=RAIL_FILTER,
        retain_all=True,
        simplify=True,
    )
    return G


if __name__ == "__main__":
    print("Loading rail network from OpenStreetMap...")
    G = load_rail_graph()
    print(f"Graph loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")

    # Plot it to confirm it loaded as a connected network
    ox.plot_graph(
        G,
        node_size=5,
        node_color="red",
        edge_color="black",
        edge_linewidth=0.8,
        bgcolor="white",
    )