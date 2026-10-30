import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

G_full = ox.load_graphml("../data/rail_graph.graphml")

sub = ox.truncate.truncate_graph_bbox(G_full, (-2.98, 53.36, -2.18, 53.54))

G_simp = sub.copy()
G_simp.graph["simplified"] = False
G_simp = ox.simplify_graph(G_simp)


def components(G):
    return list(nx.connected_components(G.to_undirected()))

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, G, label in zip(axes, [G_simp, sub],
                        ["Simplification enabled", "Simplification disabled"]):
    comps = components(G)
    idx = {n: i for i, c in enumerate(comps) for n in c}
    ec = [plt.cm.tab20(idx[u] % 20) for u, v, k in G.edges(keys=True)]
    ox.plot_graph(G, ax=ax, node_size=0, edge_color=ec, edge_linewidth=0.9,
                  bgcolor="white", show=False, close=False)
    ax.set_title(f"{label}\n{len(G.nodes):,} nodes, {len(comps)} components")

plt.savefig("fragmentation.png", dpi=200, bbox_inches="tight")