import os

NORTH, SOUTH, EAST, WEST = 60.90, 49.90, 1.80, -8.20

RAIL_FILTER = (
    '["railway"~"rail"]'
    '["railway"!~"tram|light_rail|subway|miniature|monorail|funicular"]'
            '["service"!~"yard|siding|spur"]'
    '["usage"!~"industrial"]'
)

CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "rail_graph.graphml")

# Item 17: join dangling track ends that sit within tolerance of each other
# but belong to different components. Measured 7 Nov 2026 at 20 m: 105
# connectors, 45 component pairs joined, and zero additional routable legs
# (2451/6/93/18 identical with and without). Left off because synthetic
# edges that buy nothing can still invent a junction that isn't there.
STITCH_ENABLED = False
STITCH_TOLERANCE_M = 20


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
    import networkx as nx

    XML_PATH = os.path.join(
        os.path.dirname(__file__), "..", "..", "osm-data", "gb-rail.osm"
    )

    print("building rail graph from local OSM extract..")
    G = ox.graph_from_xml(XML_PATH, retain_all=True, simplify=False)

    # The two-pass osmium filter leaves behind nodes that belonged to the
    # dropped yard and siding ways. They have no edges, bloat the graph, and
    # pollute the KD-tree that route_leg snaps stations to.
    orphans = list(nx.isolates(G))
    G.remove_nodes_from(orphans)
    print(f"removed {len(orphans):,} orphan nodes, {len(G.nodes):,} remain")

    if STITCH_ENABLED:
        stitch_components(G, STITCH_TOLERANCE_M)

    ox.save_graphml(G, CACHE_PATH)
    print(f"graph built to {CACHE_PATH}")
    return G


def stitch_components(G, tolerance_m=20):
    # Only degree-1 nodes qualify, which is what prevents a bridge being
    # stitched to the line passing beneath it.
    import math
    import numpy as np
    import networkx as nx
    from scipy.spatial import cKDTree

    UG = nx.MultiGraph(G)

    comp_of = {}
    for i, comp in enumerate(nx.connected_components(UG)):
        for n in comp:
            comp_of[n] = i

    ends = [n for n in UG.nodes if len(set(UG.neighbors(n))) == 1]

    xs, ys = [], []
    for n in ends:
        lon, lat = UG.nodes[n]["x"], UG.nodes[n]["y"]
        xs.append(lon * 111320 * math.cos(math.radians(lat)))
        ys.append(lat * 111320)
    pts = np.column_stack([xs, ys])
    tree = cKDTree(pts)

    added = 0
    for i, j in tree.query_pairs(tolerance_m):
        a, b = ends[i], ends[j]
        if comp_of[a] == comp_of[b]:
            continue
        dist = float(np.hypot(*(pts[i] - pts[j])))
        G.add_edge(a, b, length=dist, stitched=1)
        G.add_edge(b, a, length=dist, stitched=1)
        added += 1

    print(f"stitched {added} gaps at {tolerance_m} m")
    return added
