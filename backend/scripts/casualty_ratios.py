"""How far off are the no_path pairs that route with the cutoff lifted."""
import sys
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR.parent))
sys.path.insert(0, str(SCRIPT_DIR.parent / "app"))

from osm_graph import load_rail_graph
from stations import load_station_coords
from route_leg import route_leg
from services.geometry import route_plausibility

with open(SCRIPT_DIR / "no_path_split.json") as f:
    pairs = json.load(f)["cutoff_casualty"]

G = load_rail_graph()
coords = load_station_coords()

rows = []
for pair in pairs:
    track, _, _ = route_leg(G, coords, pair["crs_a"], pair["crs_b"], max_ratio=50)
    if track is None:
        continue
    ratio = route_plausibility(track, pair["crs_a"], pair["crs_b"])
    if ratio is not None:
        rows.append((ratio, f"{pair['crs_a']}-{pair['crs_b']}"))

rows.sort()
bands = {"1.6-2": 0, "2-3": 0, "3-5": 0, "5-10": 0, "10+": 0}
for ratio, _ in rows:
    if ratio < 2:    bands["1.6-2"] += 1
    elif ratio < 3:  bands["2-3"] += 1
    elif ratio < 5:  bands["3-5"] += 1
    elif ratio < 10: bands["5-10"] += 1
    else:            bands["10+"] += 1

print(f"{len(rows)} pairs with a route")
for band, n in bands.items():
    print(f"  {band}x : {n}")
print()
print("closest to plausible:")
for ratio, name in rows[:10]:
    print(f"  {name} {ratio:.2f}x")