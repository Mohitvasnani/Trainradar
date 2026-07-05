from datetime import datetime
from shapely.geometry import LineString


def estimate_position(track, departed, due, now):
    """
    Estimate where a train is along a track.

    track    : a Shapely LineString (the routed path between two stations)
    departed : datetime the train left the first station
    due      : datetime the train is due at the next station
    now      : the current datetime

    Returns a Shapely Point at the estimated position.
    """
    # Step 2: fraction of the journey done, by time
    total_time = (due - departed).total_seconds()
    elapsed = (now - departed).total_seconds()
    fraction = elapsed / total_time

    # Guard rails: don't go before the start or past the end of the track
    if fraction < 0:
        fraction = 0.0
    if fraction > 1:
        fraction = 1.0

    # Step 3: fraction -> point on the track (follows the curve)
    position = track.interpolate(fraction, normalized=True)
    return position