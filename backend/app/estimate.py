def estimate_position(track, departed, due, now):
   
    total_time=(due-departed).total_seconds()

    if total_time <= 0:
        return track.interpolate(1.0, normalized=True)

    elapsed =(now - departed).total_seconds()
    fraction =elapsed/total_time

    if fraction < 0:
        fraction = 0.0
    if fraction > 1:
        fraction = 1.0

    return track.interpolate(fraction, normalized=True)