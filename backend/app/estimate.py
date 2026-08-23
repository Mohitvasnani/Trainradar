def estimate_position(track, departed, due, now):
    """
    Estimate where a train is along a track.

    track    : a Shapely LineString (the routed path between two stations)
    departed : datetime the train left the first station
    due      : datetime the train is due at the next station
    now      : the current datetime

    Returns a Shapely Point at the estimated position.
    """
    total_time = (due-departed).total_seconds()

    if total_time <= 0:
        return track.interpolate(1.0, normalized=True)

    elapsed =(now - departed).total_seconds()
    fraction =elapsed/total_time

    if fraction < 0:
        fraction = 0.0
    if fraction > 1:
        fraction = 1.0

    return track.interpolate(fraction, normalized=True)