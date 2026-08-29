from datetime import datetime
from services.estimation import format_stop, is_train_running


def test_format_stop_basic():
    # Basic station with scheduled and actual times
    point = {
        "location": {
            "description": "Liverpool Lime Street",
            "shortCodes": ["LIV"]
        },
        "temporalData": {
            "arrival": {
                "scheduleAdvertised": "2026-08-24T10:00:00",
                "realtimeActual": "2026-08-24T10:02:00"
            },
            "departure": {
                "scheduleAdvertised": "2026-08-24T10:05:00",
                "realtimeActual": "2026-08-24T10:07:00"
            }
        },
        "locationMetadata": {
            "platform": {
                "actual": "7"
            }
        }
    }
    
    result = format_stop(point)
    
    assert result["crs"] == "LIV"
    assert result["name"] == "Liverpool Lime Street"
    assert result["schedArr"] == "2026-08-24T10:00:00"
    assert result["actualArr"] == "2026-08-24T10:02:00"
    assert result["passed"] is True
    assert result["platform"] == "7"


def test_format_stop_not_passed_yet():
    # Station train hasn't reached yet
    point = {
        "location": {
            "description": "Manchester Piccadilly",
            "shortCodes": ["MAN"]
        },
        "temporalData": {
            "arrival": {
                "scheduleAdvertised": "2026-08-24T10:45:00"
            },
            "departure": {
                "scheduleAdvertised": "2026-08-24T10:50:00"
            }
        }
    }
    
    result = format_stop(point)
    
    assert result["crs"] == "MAN"
    assert result["passed"] is False
    assert result["actualArr"] is None
    assert result["actualDep"] is None


def test_format_stop_no_crs_returns_none():
    # Location without CRS code should be skipped
    point = {
        "location": {
            "description": "Some Junction"
        }
    }
    
    result = format_stop(point)
    
    assert result is None


def test_format_stop_cancelled():
    # Cancelled stop
    point = {
        "location": {
            "description": "Crewe",
            "shortCodes": ["CRE"]
        },
        "temporalData": {
            "arrival": {
                "isCancelled": True
            },
            "departure": {
                "isCancelled": True
            }
        }
    }
    
    result = format_stop(point)
    
    assert result["isCancelled"] is True


def test_is_train_running_midjourney():
    # Train that is currently running
    svc = {
        "origin": [
            {
                "temporalData": {
                    "scheduleAdvertised": "2026-08-24T10:00:00"
                }
            }
        ],
        "destination": [
            {
                "temporalData": {
                    "scheduleAdvertised": "2026-08-24T12:00:00"
                }
            }
        ],
        "temporalData": {
            "arrival": {"isCancelled": False},
            "departure": {"isCancelled": False}
        }
    }
    
    now = datetime(2026, 8, 24, 11, 0)  # Midway
    
    assert is_train_running(svc, now) is True


def test_is_train_running_before_start():
    # Train hasn't departed yet
    svc = {
        "origin": [
            {
                "temporalData": {
                    "scheduleAdvertised": "2026-08-24T10:00:00"
                }
            }
        ],
        "destination": [
            {
                "temporalData": {
                    "scheduleAdvertised": "2026-08-24T12:00:00"
                }
            }
        ],
        "temporalData": {
            "arrival": {"isCancelled": False},
            "departure": {"isCancelled": False}
        }
    }
    
    now = datetime(2026, 8, 24, 9, 0)  # Before departure
    
    assert is_train_running(svc, now) is False


def test_is_train_running_cancelled():
    # Cancelled train should not be running
    svc = {
        "origin": [
            {
                "temporalData": {
                    "scheduleAdvertised": "2026-08-24T10:00:00"
                }
            }
        ],
        "destination": [
            {
                "temporalData": {
                    "scheduleAdvertised": "2026-08-24T12:00:00"
                }
            }
        ],
        "temporalData": {
            "arrival": {"isCancelled": True},
            "departure": {"isCancelled": False}
        }
    }
    
    now = datetime(2026, 8, 24, 11, 0)
    
    assert is_train_running(svc, now) is False


def test_is_train_running_with_grace_period():
    # Late train within 30 min grace period
    svc = {
        "origin": [
            {
                "temporalData": {
                    "scheduleAdvertised": "2026-08-24T10:00:00"
                }
            }
        ],
        "destination": [
            {
                "temporalData": {
                    "scheduleAdvertised": "2026-08-24T12:00:00"
                }
            }
        ],
        "temporalData": {
            "arrival": {"isCancelled": False},
            "departure": {"isCancelled": False}
        }
    }
    
    now = datetime(2026, 8, 24, 12, 20)  # 20 min after arrival
    
    assert is_train_running(svc, now) is True


def test_is_train_running_after_grace_period():
    # Train too late, should be considered finished
    svc = {
        "origin": [
            {
                "temporalData": {
                    "scheduleAdvertised": "2026-08-24T10:00:00"
                }
            }
        ],
        "destination": [
            {
                "temporalData": {
                    "scheduleAdvertised": "2026-08-24T12:00:00"
                }
            }
        ],
        "temporalData": {
            "arrival": {"isCancelled": False},
            "departure": {"isCancelled": False}
        }
    }
    
    now = datetime(2026, 8, 24, 12, 45)  # 45 min after arrival
    
    assert is_train_running(svc, now) is False