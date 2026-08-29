from datetime import datetime
from find_current_leg import find_live_leg


def make_service(locations):
    # Helper to build service dict
    return {"service": {"locations": locations}}


def make_location(name, crs, dep=None, arr=None):
    # Helper to build location dict
    temporal = {}
    if dep:
        temporal["departure"] = {"scheduleAdvertised": dep}
    if arr:
        temporal["arrival"] = {"scheduleAdvertised": arr}
    
    return {
        "location": {
            "description": name,
            "shortCodes": [crs]
        },
        "temporalData": temporal
    }


def test_midjourney_returns_correct_pair():
    # Train between station B and C
    locations = [
        make_location("Liverpool", "LIV", dep="2026-08-24T10:00:00"),
        make_location("Manchester", "MAN", arr="2026-08-24T10:45:00", dep="2026-08-24T10:50:00"),
        make_location("London", "EUS", arr="2026-08-24T12:30:00"),
    ]
    
    service = make_service(locations)
    now = datetime(2026, 8, 24, 11, 0)  # Between Manchester dep and London arr
    
    leg = find_live_leg(service, now)
    
    assert leg is not None
    assert leg[0]["crs"] == "MAN"
    assert leg[1]["crs"] == "EUS"


def test_not_departed_returns_none():
    # Train hasn't left yet
    locations = [
        make_location("Liverpool", "LIV", dep="2026-08-24T10:00:00"),
        make_location("Manchester", "MAN", arr="2026-08-24T10:45:00", dep="2026-08-24T10:50:00"),
        make_location("London", "EUS", arr="2026-08-24T12:30:00"),
    ]
    
    service = make_service(locations)
    now = datetime(2026, 8, 24, 9, 0)  # Before first departure
    
    leg = find_live_leg(service, now)
    
    assert leg is None


def test_arrived_returns_none():
    # Train has finished journey
    locations = [
        make_location("Liverpool", "LIV", dep="2026-08-24T10:00:00"),
        make_location("Manchester", "MAN", arr="2026-08-24T10:45:00", dep="2026-08-24T10:50:00"),
        make_location("London", "EUS", arr="2026-08-24T12:30:00"),
    ]
    
    service = make_service(locations)
    now = datetime(2026, 8, 24, 13, 0)  # After final arrival
    
    leg = find_live_leg(service, now)
    
    assert leg is None


def test_exactly_at_departure_time():
    # Now exactly equals departure from station B
    locations = [
        make_location("Liverpool", "LIV", dep="2026-08-24T10:00:00"),
        make_location("Manchester", "MAN", arr="2026-08-24T10:45:00", dep="2026-08-24T10:50:00"),
        make_location("London", "EUS", arr="2026-08-24T12:30:00"),
    ]
    
    service = make_service(locations)
    now = datetime(2026, 8, 24, 10, 50)  # Exactly at Manchester departure
    
    leg = find_live_leg(service, now)
    
    assert leg is not None
    assert leg[0]["crs"] == "MAN"
    assert leg[1]["crs"] == "EUS"


def test_exactly_at_arrival_time():
    # Now exactly equals arrival at station B
    locations = [
        make_location("Liverpool", "LIV", dep="2026-08-24T10:00:00"),
        make_location("Manchester", "MAN", arr="2026-08-24T10:45:00", dep="2026-08-24T10:50:00"),
        make_location("London", "EUS", arr="2026-08-24T12:30:00"),
    ]
    
    service = make_service(locations)
    now = datetime(2026, 8, 24, 10, 45)  # Exactly at Manchester arrival
    
    leg = find_live_leg(service, now)
    
    # At arrival, still on previous leg (LIV->MAN)
    assert leg is not None
    assert leg[0]["crs"] == "LIV"
    assert leg[1]["crs"] == "MAN"


def test_at_station_between_legs():
    # Train arrived at B but hasn't departed yet (10:46-10:49)
    locations = [
        make_location("Liverpool", "LIV", dep="2026-08-24T10:00:00"),
        make_location("Manchester", "MAN", arr="2026-08-24T10:45:00", dep="2026-08-24T10:50:00"),
        make_location("London", "EUS", arr="2026-08-24T12:30:00"),
    ]
    
    service = make_service(locations)
    now = datetime(2026, 8, 24, 10, 47)  # Between arrival and departure at Manchester
    
    leg = find_live_leg(service, now)
    
    assert leg is None


def test_single_station_returns_none():
    # Only one station, no legs possible
    locations = [
        make_location("Liverpool", "LIV", dep="2026-08-24T10:00:00"),
    ]
    
    service = make_service(locations)
    now = datetime(2026, 8, 24, 10, 30)
    
    leg = find_live_leg(service, now)
    
    assert leg is None