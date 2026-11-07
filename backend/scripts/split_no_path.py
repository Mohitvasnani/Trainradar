"""One-off: split the no_path bucket into cutoff casualties vs real breaks."""
import sys
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR.parent))
sys.path.insert(0, str(SCRIPT_DIR.parent / "app"))

from osm_graph import load_rail_graph
from stations import load_station_coords
from route_leg import route_leg

with open(SCRIPT_DIR / "diagnostic_results.json") as f:
    pairs = json.load(f)["no_path"]

G = load_rail_graph()
coords = load_station_coords()

casualty, broken = [], []
for pair in pairs:
    track, _, _ = route_leg(G, coords, pair["crs_a"], pair["crs_b"], max_ratio=50)
    (casualty if track is not None else broken).append(pair)

print(f"{len(pairs)} no_path pairs")
print(f"  route once the cutoff is lifted: {len(casualty)}")
print(f"  genuinely disconnected:          {len(broken)}")

with open(SCRIPT_DIR / "no_path_split.json", "w") as f:
    json.dump({"cutoff_casualty": casualty, "component_break": broken}, f, indent=2)