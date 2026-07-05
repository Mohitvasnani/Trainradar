from datetime import datetime
from shapely.geometry import LineString

# --- The track for this leg (our L-shaped mini-track again) ---
track = LineString([(0, 0), (10, 0), (10, 10)])

# --- The times for this leg ---
departed = datetime(2026, 6, 30, 16, 50)
due      = datetime(2026, 6, 30, 16, 55)
now      = datetime(2026, 6, 30, 16, 53)

# --- Step 2: work out the fraction of the journey done ---
total_time = due - departed
elapsed = now - departed
fraction = elapsed.total_seconds() / total_time.total_seconds()
print(f"Fraction of journey done: {fraction}")

# --- Step 3: turn that fraction into a position on the track ---

# Method A: fraction -> distance -> point (shows the maths explicitly)
distance = fraction * track.length
position_a = track.interpolate(distance)
print(f"Distance along track: {distance}")
print(f"Estimated position (method A): {position_a}")

# Method B: pass the fraction straight in with normalized=True (cleaner)
position_b = track.interpolate(fraction, normalized=True)
print(f"Estimated position (method B): {position_b}")