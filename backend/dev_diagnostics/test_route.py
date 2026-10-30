from osm_graph import load_rail_graph
from stations import load_station_coords
from route_leg import route_leg

ROUTE = [("MAN", "Manchester Piccadilly"),
    ("MCO", "Manchester Oxford Road"),
    ("MCV", "Manchester Victoria"),
    ("NLW", "Newton-le-Willows"),
    ("ERL", "Earlestown"),
    ("SNJ", "St Helens Junction"),
    ("LEG", "Lea Green"),
    ("RNH", "Rainhill"),
    ("WHN", "Whiston"),
    ("HUY", "Huyton"),
    ("ROB", "Roby"),
    ("BGE", "Broad Green"),
    ("WAV", "Wavertree Technology Park"),
    ("EDG", "Edge Hill"),
    ("LIV", "Liverpool Lime Street")]

G = load_rail_graph()
coords = load_station_coords()

print("Testing each leg of Manchester -> Liverpool:\n")
good = 0
bad = 0

for i in range(len(ROUTE) - 1):
    crs_a,name_a   = ROUTE[i]
    crs_b,name_b= ROUTE[i + 1]

    track,   snap_a,    snap_b = route_leg(G, coords, crs_a, crs_b)
    if track is not None:
        print(f"  OK{name_a} -> {name_b}  (snaps {snap_a:.0f}/{snap_b:.0f} m)")
        good += 1
    else:
        reason = "no route"
        if snap_a and snap_a > 300:
            reason = f"{name_a} snapped {snap_a:.0f}m"
        elif snap_b and snap_b > 300:
            reason = f"{name_b} snapped {snap_b:.0f}m"
        print(f"  SKIPPED  {name_a} -> {name_b}  ({reason})")
        bad +=1

print(f"\n{good} legs OK, {bad} skipped")