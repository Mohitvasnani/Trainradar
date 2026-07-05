from datetime import datetime

# Pretend times for one leg of a journey.
departed = datetime(2026, 6, 30, 16, 50)   # left first station at 16:50
due      = datetime(2026, 6, 30, 16, 55)   # due at next station at 16:55
now      = datetime(2026, 6, 30, 16, 53)   # current time is 16:53

# How long is the whole leg? Subtracting two datetimes gives a "timedelta".
total_time = due - departed
print(f"Total leg time: {total_time}  ({total_time.total_seconds()} seconds)")

# How much time has passed since departure?
elapsed = now - departed
print(f"Elapsed so far: {elapsed}  ({elapsed.total_seconds()} seconds)")

# The fraction of the journey completed = elapsed / total.
# We use .total_seconds() so we're dividing plain numbers.
fraction = elapsed.total_seconds() / total_time.total_seconds()
print(f"Fraction of journey done: {fraction}")