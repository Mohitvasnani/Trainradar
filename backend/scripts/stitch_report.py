"""
Item 17 reconnaissance: how many disconnected track ends sit close enough
to stitch, across a range of tolerances. Reports only, changes nothing.
"""

import sys
import math
from pathlib import Path

import numpy as np
import networkx as nx
from scipy.spatial import cKDTree

SCRIPT_DIR = Path(__file__).parent.absolute()
BACKEND_DIR = SCRIPT_DIR.parent

sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "app"))

from osm_graph import load_rail_graph

TOLERANCES_M = [5, 10, 20, 50, 100]


def main():
    G = load_rail_graph()
    if G is None:
        sys.exit("no graph")

    UG = nx.MultiGraph(G)
    print(f"graph: {UG.number_of_nodes():,} nodes, {UG.number_of_edges():,} edges")

    comp_of = {}
    sizes = []
    for i, comp in enumerate(nx.connected_components(UG)):
        sizes.append(len(comp))
        for n in comp:
            comp_of[n] = i
    sizes.sort(reverse=True)
    singletons = sum(1 for s in sizes if s == 1)
    print(f"components: {len(sizes):,}   largest: {sizes[0]:,}   "
          f"next four: {sizes[1:5]}   singletons: {singletons:,}")

    # A dangling track end has exactly one distinct neighbour. Mid-track
    # nodes have two. Restricting to ends is what stops a bridge being
    # stitched to the line passing underneath it.
    ends = [n for n in UG.nodes if len(set(UG.neighbors(n))) == 1]
    print(f"dangling ends: {len(ends):,}")

    # Project lon/lat to approximate metres, per node, so the KD-tree can
    # work in metres directly rather than in degrees.
    xs, ys = [], []
    for n in ends:
        lon = UG.nodes[n]["x"]
        lat = UG.nodes[n]["y"]
        xs.append(lon * 111320 * math.cos(math.radians(lat)))
        ys.append(lat * 111320)
    tree = cKDTree(np.column_stack([xs, ys]))

    print()
    print(" tolerance   cross-component pairs   components joined")
    for tol in TOLERANCES_M:
        pairs = tree.query_pairs(tol)
        cross = [(i, j) for i, j in pairs
                 if comp_of[ends[i]] != comp_of[ends[j]]]
        joined = {tuple(sorted((comp_of[ends[i]], comp_of[ends[j]])))
                  for i, j in cross}
        print(f"{tol:>7} m   {len(cross):>21,}   {len(joined):>17,}")


if __name__ == "__main__":
    main()