import networkx as nx
import osmnx as ox
from geopy.distance import geodesic
from osm_graph import load_rail_graph

G = load_rail_graph()
print(f"Total: {len(G.nodes)} nodes,{len(G.edges)} edges")

UG = G.to_undirected()
components =list(nx.connected_components(UG))
print(f"Graph is in {len(components)} disconnected components")

sizes = sorted((len(c) for c in components), reverse=True)
print(f"Largest components: {sizes[:10]}")

node =ox.distance.nearest_nodes(G, -2.759, 53.417)
d= geodesic((53.417, -2.759), (G.nodes[node]["y"],G.nodes[node]["x"])).m
print(f"Nearest node to Rainhill is {d:.0f}m away")