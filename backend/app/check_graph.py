import networkx as nx
from osm_graph import load_rail_graph
import osmnx as ox

G = load_rail_graph()
print(f"Total: {len(G.nodes)} nodes, {len(G.edges)} edges")

# How many separate disconnected pieces is the graph in?
UG = G.to_undirected()
components = list(nx.connected_components(UG))
print(f"Graph is in {len(components)} disconnected components")

# Sizes of the biggest few
sizes = sorted((len(c) for c in components), reverse=True)
print(f"Largest components: {sizes[:10]}")

# Is there ANY node near Rainhill (53.417, -2.759)?
node = ox.distance.nearest_nodes(G, -2.759, 53.417)
from geopy.distance import geodesic
d = geodesic((53.417, -2.759), (G.nodes[node]["y"], G.nodes[node]["x"])).m
print(f"Nearest node to Rainhill is {d:.0f} m away")