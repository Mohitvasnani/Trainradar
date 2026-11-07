import networkx as nx
import numpy as np
from scipy.spatial import cKDTree
from geopy.distance import geodesic

from track_builder import build_route_track
from services.geometry import track_length_m, haversine_m

_undirected_cache = {}
_kdtree_cache = {}
_component_cache = {}


def _get_undirected(G):
    # MultiGraph, not Graph: build_route_track reads edge keys.
    # nx.MultiGraph(G) shallow-references the existing attribute dicts,
    # so this is seconds, unlike G.to_undirected() which deepcopies.
    key = id(G)
    if key not in _undirected_cache:
        _undirected_cache[key] = nx.MultiGraph(G)
    return _undirected_cache[key]


def _get_components(G_u):
    key = id(G_u)
    if key not in _component_cache:
        comp_of = {}
        for i, comp in enumerate(nx.connected_components(G_u)):
            for n in comp:
                comp_of[n] = i
        _component_cache[key] = comp_of
    return _component_cache[key]


def _get_kdtree(G):
    key = id(G)
    if key not in _kdtree_cache:
        node_ids = list(G.nodes)
        xs = [G.nodes[n]["x"] for n in node_ids]
        ys = [G.nodes[n]["y"] for n in node_ids]
        tree = cKDTree(np.column_stack([xs, ys]))
        _kdtree_cache[key] = (node_ids, tree)
    return _kdtree_cache[key]


def _k_nearest_nodes(G, lon, lat, k=3):
    node_ids, tree = _get_kdtree(G)
    k = min(k, len(node_ids))
    _, idxs = tree.query([lon, lat], k=k)
    if np.isscalar(idxs):
        idxs = [idxs]
    return [node_ids[i] for i in idxs]


def route_leg(G, coords, crs_a, crs_b, max_snap_m=300, k_candidates=3,
              max_ratio=1.6):

    if crs_a not in coords or crs_b not in coords:
        return None, None, None

    a_lat, a_lon = coords[crs_a]
    b_lat, b_lon = coords[crs_b]

    G_u = _get_undirected(G)
    comp_of = _get_components(G_u)

    a_candidates = _k_nearest_nodes(G_u, a_lon, a_lat, k=k_candidates)
    b_candidates = _k_nearest_nodes(G_u, b_lon, b_lat, k=k_candidates)

    # Compute every candidate's snap distance upfront, independent of the
    # route-search loop below - this is what was missing before, and why
    # closest_b_snap could end up None when every a-candidate was too far.
    a_snaps = {n: geodesic((a_lat, a_lon), (G_u.nodes[n]["y"], G_u.nodes[n]["x"])).m for n in a_candidates}
    b_snaps = {n: geodesic((b_lat, b_lon), (G_u.nodes[n]["y"], G_u.nodes[n]["x"])).m for n in b_candidates}

    closest_a_snap = min(a_snaps.values()) if a_snaps else None
    closest_b_snap = min(b_snaps.values()) if b_snaps else None

    straight = haversine_m(a_lat, a_lon, b_lat, b_lon)

    # Anything longer than MAX_ROUTE_RATIO is discarded as implausible
    # anyway, so there is no reason to let Dijkstra search past it.
    cutoff = straight * max_ratio if straight > 0 else None

    best_track = None
    best_ratio = None
    best_a_snap = None
    best_b_snap = None

    for a_node, a_snap in a_snaps.items():
        if a_snap > max_snap_m:
            continue
        for b_node, b_snap in b_snaps.items():
            if b_snap > max_snap_m:
                continue
            if comp_of.get(a_node) != comp_of.get(b_node):
                continue

            try:
                _, route = nx.single_source_dijkstra(
                    G_u, a_node, target=b_node, cutoff=cutoff, weight="length"
                )
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue

            if not route or len(route) < 2:
                continue

            track = build_route_track(G_u, route)
            length = track_length_m(track)
            ratio = (length / straight) if straight > 0 else None

            if best_ratio is None or (ratio is not None and ratio < best_ratio):
                best_track = track
                best_ratio = ratio
                best_a_snap = a_snap
                best_b_snap = b_snap

    if best_track is None:
        return None, closest_a_snap, closest_b_snap

    return best_track, best_a_snap, best_b_snap
