"""
Stage 1, items 12-13: runs route_leg over every resolved adjacency pair
and buckets the results into four categories: plausible, implausible,
no path found, snap too far.

Run from anywhere - it sets up sys.path itself. Expects
adjacency_resolved.json in the same folder as this script (backend/scripts/).

Optional first argument limits how many pairs to route, for timing runs:
    python diagnose_routing.py 100
"""

import sys
import json
import time
from pathlib import Path

# Same pattern as testing_suite/conftest.py, so the mixed flat-import /
# package-import style in the existing code works unmodified.
SCRIPT_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = SCRIPT_DIR.parent
APP_DIR = BACKEND_DIR / "app"

sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(APP_DIR))

from osm_graph import load_rail_graph
from stations import load_station_coords
from route_leg import route_leg
from services.geometry import route_plausibility, is_implausible


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None

    adjacency_path = SCRIPT_DIR / "adjacency_resolved.json"
    with open(adjacency_path) as f:
        pairs = json.load(f)

    if limit:
        pairs = pairs[:limit]
        print(f"TIMING RUN: first {len(pairs)} pairs only")

    print(f"{len(pairs)} pairs to route")
    print("Loading rail graph (cached, should be fast)...")
    G = load_rail_graph()
    if G is None:
        print("No graph found - check backend/data/rail_graph.graphml exists.")
        sys.exit(1)
    print(f"Graph loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")

    coords = load_station_coords()
    print(f"{len(coords)} station coordinates loaded")
    print()

    buckets = {
        "plausible": [],
        "implausible": [],
        "no_path": [],
        "snap_too_far": [],
        "missing_coords": [],
    }

    timings = []
    t_start = time.time()

    for i, pair in enumerate(pairs):
        crs_a, crs_b = pair["crs_a"], pair["crs_b"]

        t0 = time.time()
        track, snap_a, snap_b = route_leg(G, coords, crs_a, crs_b)
        dt = time.time() - t0
        timings.append((dt, f"{crs_a}-{crs_b}"))

        if (i + 1) % 25 == 0:
            done = i + 1
            elapsed = time.time() - t_start
            rate = elapsed / done
            left = (len(pairs) - done) * rate
            print(f"  {done}/{len(pairs)}  {elapsed/60:.1f} min in, "
                  f"{rate:.2f} s/pair, ~{left/60:.0f} min left")

        if track is None:
            if snap_a is None or snap_b is None:
                buckets["missing_coords"].append(pair)
            elif snap_a > 300 or snap_b > 300:
                buckets["snap_too_far"].append({**pair, "snap_a": snap_a, "snap_b": snap_b})
            else:
                buckets["no_path"].append(pair)
            continue

        ratio = route_plausibility(track, crs_a, crs_b)
        entry = {**pair, "ratio": ratio}
        if is_implausible(ratio):
            buckets["implausible"].append(entry)
        else:
            buckets["plausible"].append(entry)

    print()
    print("=== Results ===")
    total = len(pairs)
    for name, items in buckets.items():
        pct = 100 * len(items) / total if total else 0
        print(f"  {name}: {len(items)} ({pct:.1f}%)")

    print()
    print(f"total {(time.time() - t_start)/60:.1f} min")
    for dt, name in sorted(timings, reverse=True)[:5]:
        print(f"  slowest: {name} {dt:.1f}s")

    name = "diagnostic_results_sample.json" if limit else "diagnostic_results.json"
    out_path = SCRIPT_DIR / name
    with open(out_path, "w") as f:
        json.dump(buckets, f, indent=2)
    print()
    print(f"Full breakdown written to {out_path}")


if __name__ == "__main__":
    main()