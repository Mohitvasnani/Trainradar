import json, csv

with open("../data/stations.csv") as f:
    real_crs = set(row["crsCode"].strip() for row in csv.DictReader(f) if row["crsCode"].strip())

with open("adjacency.json") as f:
    pairs = json.load(f)

# Drop junction/reporting-point codes outright - no station, no board, nothing to route to meaningfully.
pairs = [p for p in pairs if not p["crs_a"].startswith("X") and not p["crs_b"].startswith("X")]

resolved = [p for p in pairs if p["crs_a"] in real_crs and p["crs_b"] in real_crs]
unresolved = [p for p in pairs if p["crs_a"] not in real_crs or p["crs_b"] not in real_crs]

print(f"After dropping X-junctions: {len(pairs)} pairs")
print(f"  resolved against stations.csv: {len(resolved)}")
print(f"  still unresolved (code missing from stations.csv): {len(unresolved)}")

with open("adjacency_resolved.json", "w") as f:
    json.dump(resolved, f, indent=2)

with open("adjacency_unresolved.json", "w") as f:
    json.dump(unresolved, f, indent=2)