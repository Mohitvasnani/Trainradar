from datetime import datetime
from shapely.geometry import LineString
from estimate import estimate_position


def test_halfway_in_time_is_halfway_along():
    track = LineString([(0, 0), (10, 0)])
    departed = datetime(2026, 1, 1, 12, 0)
    due = datetime(2026, 1, 1, 12, 10)
    now = datetime(2026, 1, 1, 12, 5)

    pos = estimate_position(track, departed, due, now)

    assert abs(pos.x - 5.0) < 0.001
    assert abs(pos.y - 0.0) < 0.001


def test_before_departure_clamps_to_start():
    track = LineString([(0, 0), (10, 0)])
    departed = datetime(2026, 1, 1, 12, 0)
    due = datetime(2026, 1, 1, 12, 10)
    now = datetime(2026, 1, 1, 11, 55)

    pos = estimate_position(track, departed, due, now)

    assert abs(pos.x - 0.0) < 0.001
    assert abs(pos.y - 0.0) < 0.001


def test_curved_track_follows_arc_length():
    track = LineString([(0, 0), (0, 10), (10, 10)])
    departed = datetime(2026, 1, 1, 12, 0)
    due = datetime(2026, 1, 1, 12, 10)
    now = datetime(2026, 1, 1, 12, 5)

    pos = estimate_position(track, departed, due, now)

    assert abs(pos.x - 0.0) < 0.001
    assert abs(pos.y - 10.0) < 0.001


def test_after_arrival_goes_to_end():
    track = LineString([(0, 0), (10, 0)])
    departed = datetime(2026, 1, 1, 12, 0)
    due = datetime(2026, 1, 1, 12, 10)
    now = datetime(2026, 1, 1, 12, 20)

    pos = estimate_position(track, departed, due, now)

    assert abs(pos.x - 10.0) < 0.001
    assert abs(pos.y - 0.0) < 0.001


def test_at_departure_is_at_start():
    track = LineString([(0, 0), (10, 0)])
    departed = datetime(2026, 1, 1, 12, 0)
    due = datetime(2026, 1, 1, 12, 10)
    now = datetime(2026, 1, 1, 12, 0)

    pos = estimate_position(track, departed, due, now)

    assert abs(pos.x - 0.0) < 0.001
    assert abs(pos.y - 0.0) < 0.001


def test_zero_duration_returns_end():
    track = LineString([(0, 0), (10, 0)])
    departed = datetime(2026, 1, 1, 12, 0)
    due = datetime(2026, 1, 1, 12, 0)
    now = datetime(2026, 1, 1, 12, 5)

    pos = estimate_position(track, departed, due, now)

    assert abs(pos.x - 10.0) < 0.001
    assert abs(pos.y - 0.0) < 0.001


def test_quarter_along_track():
    track = LineString([(0, 0), (10, 0)])
    departed = datetime(2026, 1, 1, 12, 0)
    due = datetime(2026, 1, 1, 12, 10)
    now = datetime(2026, 1, 1, 12, 2, 30)

    pos = estimate_position(track, departed, due, now)

    assert abs(pos.x - 2.5) < 0.001
    assert abs(pos.y - 0.0) < 0.001