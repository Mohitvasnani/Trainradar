from osm_graph import load_rail_graph

G = load_rail_graph()

total = 0
with_geom = 0
max_points = 0

for u, v, data in G.edges(data=True):
    total += 1
    if "geometry" in data:
        with_geom += 1
        pts = len(data["geometry"].coords)
        if pts > max_points:
            max_points = pts

print(f"Total edges: {total}")
print(f"Edges WITH stored curve geometry: {with_geom}")
print(f"Edges that are just straight: {total - with_geom}")
print(f"Most points on a single curved edge: {max_points}")