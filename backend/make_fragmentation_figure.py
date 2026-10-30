"""

"""
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox

print("osmnx version:", ox.__version__)

HERE = os.path.dirname(os.path.abspath(__file__))
GRAPHML = os.path.join(HERE, "data", "rail_graph.graphml")
OUT_DIR = os.path.join(HERE, "outputs")
OUT = os.path.join(OUT_DIR, "fragmentation.png")

# Crop box: west, south, east, north
WEST, SOUTH, EAST, NORTH = -2.98, 53.36, -2.18, 53.54

if not os.path.exists(GRAPHML):
    sys.exit(f"Graph not found at {GRAPHML}")
os.makedirs(OUT_DIR, exist_ok=True)

G = ox.load_graphml(GRAPHML)
print(f"  full graph: {len(G.nodes):,} nodes")


def crop(G):
    # Crop to bounding box
    try:
        return ox.truncate.truncate_graph_bbox(G, (WEST, SOUTH, EAST, NORTH))
    except TypeError:
        return ox.truncate.truncate_graph_bbox(G, NORTH, SOUTH, EAST, WEST)


def simplify(G):

    H = G.copy()
    H.graph["simplified"] = False
    try:
        return ox.simplify_graph(H)
    except AttributeError:
        return ox.simplification.simplify_graph(H)


sub = crop(G)
print(f"  cropped: {len(sub.nodes):,} nodes")

sub_simplified = simplify(sub)
print(f"  simplified: {len(sub_simplified.nodes):,} nodes")


def components(G):
    return list(nx.connected_components(G.to_undirected()))


panels = [
    (sub_simplified, "Simplification enabled"),
    (sub, "Simplification disabled"),
]

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, (Gp, label) in zip(axes, panels):
    comps = components(Gp)
    print(f"{label}: {len(Gp.nodes):,} nodes, {len(comps)} components")

    idx = {n: i for i, c in enumerate(comps) for n in c}
    edge_colours = [plt.cm.tab20(idx[u] % 20) for u, v, k in Gp.edges(keys=True)]

    ox.plot_graph(
        Gp, ax=ax, node_size=0, edge_color=edge_colours, edge_linewidth=0.9,
        bgcolor="white", show=False, close=False,
    )
    ax.set_title(
        f"{label}\n{len(Gp.nodes):,} nodes, {len(comps)} components",
        fontsize=12,
    )

plt.tight_layout()
plt.savefig(OUT, dpi=200, bbox_inches="tight", facecolor="white")
print("\nwritten:", OUT)