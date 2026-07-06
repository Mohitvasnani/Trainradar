from datetime import datetime

# This is the kind of string RTT gives us
time_text = "2026-06-30T16:50:00"
print(f"As text: {time_text}  (type: {type(time_text).__name__})")

# Convert the text into a real datetime object
time_obj = datetime.fromisoformat(time_text)
print(f"As datetime: {time_obj}  (type: {type(time_obj).__name__})")

# Now we can do maths with it, which we couldn't with text
print(f"The hour is: {time_obj.hour}")

# And "now" — the current real time
now = datetime.now()
print(f"Right now it is: {now}")