from shapely.geometry import LineString
from services.geometry import route_plausibility


def test_route_plausibility_straight_track():
    # Straight track should have ratio close to 1.0
    track = LineString([(-2.9780, 53.4078), (-2.2309, 53.4774)])
    
    # Mock coords matching the track endpoints
    import services.geometry as geometry
    original_coords = geometry.coords
    geometry.coords = {
        "LIV": (53.4078, -2.9780),
        "MAN": (53.4774, -2.2309),
    }
    
    try:
        ratio = route_plausibility(track, "LIV", "MAN")
        assert ratio is not None
        assert ratio > 0.9
        assert ratio < 1.1
    finally:
        geometry.coords = original_coords


def test_route_plausibility_curved_track():
    # Curved track should have ratio > 1.0
    track = LineString([
        (-2.9780, 53.4078),
        (-2.6000, 53.4400),  # Detour point
        (-2.2309, 53.4774),
    ])
    
    import services.geometry as geometry
    original_coords = geometry.coords
    geometry.coords = {
        "LIV": (53.4078, -2.9780),
        "MAN": (53.4774, -2.2309),
    }
    
    try:
        ratio = route_plausibility(track, "LIV", "MAN")
        assert ratio is not None
        assert ratio > 1.0
    finally:
        geometry.coords = original_coords


def test_route_plausibility_missing_station():
    # Station not in coords should return None
    track = LineString([(0, 0), (10, 10)])
    
    import services.geometry as geometry
    original_coords = geometry.coords
    geometry.coords = {}
    
    try:
        ratio = route_plausibility(track, "XXX", "YYY")
        assert ratio is None
    finally:
        geometry.coords = original_coords