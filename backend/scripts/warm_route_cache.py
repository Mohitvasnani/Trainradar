"""
Stage 1, item 20: the warming job.

Routes every resolved adjacency pair deliberately, simplifies the geometry,
and writes backend/data/route_cache.json in the format load_route_cache reads.

    python warm_route_cache.py        # all pairs
    python warm_route_cache.py 50     # first 50, for a quick check
"""

import sys
import json
import time
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = SCRIPT_DIR.parent

sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "app"))

from osm_graph import load_rail_graph
from stations import load_station_coords
from route_leg import route_leg
from services.geometry import route_plausibility, is_implausible

OUT_PATH = BACKEND_DIR / "data" / "route_cache.json"

# Douglas-Peucker tolerance. Geometry is in lon/lat degrees, so 5 m is
# converted using 111,320 m per degree of latitude.
SIMPLIFY_TOLERANCE_DEG = 5 / 111320


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None

    with open(SCRIPT_DIR / "adjacency_resolved.json") as f:
        pairs = json.load(f)
    if limit:
        pairs = pairs[:limit]
        print(f"TEST RUN: first {len(pairs)} pairs, will still overwrite the cache")

    G = load_rail_graph()
    if G is None:
        sys.exit("no graph - build it first")
    coords = load_station_coords()
    print(f"{len(pairs)} pairs, graph {len(G.nodes):,} nodes")

    out = {}
    raw_points = 0
    kept_points = 0
    counts = {"written": 0, "implausible": 0, "no_route": 0, "not_linestring": 0}

    t_start = time.time()

    for i, pair in enumerate(pairs):
        crs_a, crs_b = pair["crs_a"], pair["crs_b"]
        track, _, _ = route_leg(G, coords, crs_a, crs_b)

        if (i + 1) % 250 == 0:
            print(f"  {i + 1}/{len(pairs)}  {time.time() - t_start:.0f}s")

        if track is None:
            counts["no_route"] += 1
            continue
        if track.geom_type != "LineString":
            counts["not_linestring"] += 1
            continue
        if is_implausible(route_plausibility(track, crs_a, crs_b)):
            counts["implausible"] += 1
            continue

        simplified = track.simplify(SIMPLIFY_TOLERANCE_DEG, preserve_topology=False)
        raw_points += len(track.coords)
        kept_points += len(simplified.coords)

        out[f"{crs_a}-{crs_b}"] = [
            [round(x, 6), round(y, 6)] for x, y in simplified.coords
        ]
        counts["written"] += 1

    backup = OUT_PATH.with_name("route_cache_33leg_backup.json")
    if OUT_PATH.exists() and not backup.exists():
        shutil.copy2(OUT_PATH, backup)
        print(f"previous cache backed up to {backup.name}")

    tmp = OUT_PATH.with_name(OUT_PATH.name + ".tmp")
    with open(tmp, "w") as f:
        json.dump(out, f)
    tmp.replace(OUT_PATH)

    size_mb = OUT_PATH.stat().st_size / 1_000_000
    print()
    print(f"written {counts['written']} legs, {size_mb:.2f} MB")
    for key in ("implausible", "no_route", "not_linestring"):
        print(f"  skipped {key}: {counts[key]}")
    if raw_points:
        pct = 100 * kept_points / raw_points
        print(f"  coordinates {raw_points:,} -> {kept_points:,} ({pct:.0f}% kept)")
    print(f"  {time.time() - t_start:.0f}s total")

if __name__ == "__main__":
    main()