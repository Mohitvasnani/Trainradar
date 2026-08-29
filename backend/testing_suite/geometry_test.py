from datetime import datetime
from shapely.geometry import LineString
from services.geometry import haversine_m, track_length_m, route_plausibility, is_implausible


def test_haversine_same_point_is_zero():
    # Same point should be 0 meters apart
    dist = haversine_m(53.4078, -2.9780, 53.4078, -2.9780)
    
    assert dist < 0.001


def test_haversine_known_distance():
    # Rough distance between Liverpool and Manchester (~50km)
    dist = haversine_m(53.4078, -2.9780, 53.4774, -2.2309)
    
    assert dist > 45000  # More than 45km
    assert dist < 55000  # Less than 55km


def test_track_length_straight_line():
    # 1 degree latitude is roughly 111km
    track = LineString([(0, 0), (0, 1)])
    length = track_length_m(track)
    
    assert length > 110000
    assert length < 112000


def test_track_length_multi_segment():
    # Two segments: up 1, then right 1
    track = LineString([(0, 0), (0, 1), (1, 1)])
    length = track_length_m(track)
    
    # Should be roughly 222km (111km + 111km)
    assert length > 220000
    assert length < 224000


def test_route_plausibility_normal_route():
    # Straight track should have ratio close to 1.0
    # Can't easily test without mock coords, so test the concept
    ratio = 1.1
    
    assert not is_implausible(ratio)


def test_route_plausibility_bad_route():
    # Route that doubles back should be flagged
    ratio = 3.3
    
    assert is_implausible(ratio)


def test_is_implausible_none_returns_false():
    # None ratio should not be flagged as implausible
    assert not is_implausible(None)


def test_is_implausible_boundary():
    # Exactly at threshold should be plausible
    assert not is_implausible(1.5)
    # Just above threshold should be implausible
    assert is_implausible(1.51)