import osmnx as ox

ox.settings.max_query_area_size = 50_000_000_000

# Tiny box tightly around Rainhill station (53.417, -2.759)
NORTH, SOUTH, EAST, WEST = 53.43, 53.40, -2.72, -2.80

RAIL_FILTER = '["railway"~"rail"]["railway"!~"tram|light_rail|subway|miniature|monorail|funicular"]'

print("Fetching just the Rainhill area...")
G = ox.graph_from_bbox(
    (WEST, SOUTH, EAST, NORTH),
    custom_filter=RAIL_FILTER,
    retain_all=True,
    simplify=False,          # <-- turn OFF simplify to test if that's the culprit
)
print(f"With simplify=False: {len(G.nodes)} nodes, {len(G.edges)} edges")

# How close is the nearest node to Rainhill now?
from geopy.distance import geodesic
node = ox.distance.nearest_nodes(G, -2.759, 53.417)
d = geodesic((53.417, -2.759), (G.nodes[node]["y"], G.nodes[node]["x"])).m
print(f"Nearest node to Rainhill: {d:.0f} m away")