from datetime import datetime, date

from rtt_client import get_access_token, get_location_board, get_service


def get_leg_times(loc):
    """Pull the useful times from one location as datetimes (or None)."""
    temporal = loc.get("temporalData", {})

    def pick(kind):
        block = temporal.get(kind) or {}
        t = block.get("scheduleAdvertised") or block.get("scheduleInternal")
        return datetime.fromisoformat(t) if t else None

    return {
        "name": loc.get("location", {}).get("description", "?"),
        "crs": (loc.get("location", {}).get("shortCodes") or [None])[0],
        "arrival": pick("arrival"),
        "departure": pick("departure"),
    }

def find_live_leg(service, now):
    """Return (a, b) for the leg this service is on now, or None."""
    locations = service.get("service", {}).get("locations", [])
    legs = [get_leg_times(loc) for loc in locations]
    for i in range(len(legs) - 1):
        a, b = legs[i], legs[i + 1]
        if a["departure"] and b["arrival"] and a["departure"] <= now <= b["arrival"]:
            return a, b
    return None


if __name__ == "__main__":
    token, _ = get_access_token()

    # Grab a live service at Lime Street
    board = get_location_board(token, code="LIV")
    services = board.get("services", [])
    identity = services[0]["scheduleMetadata"]["identity"]
    today = date.today().isoformat()
    service = get_service(token, identity=identity, departure_date=today)

    locations = service.get("service", {}).get("locations", [])
    legs = [get_leg_times(loc) for loc in locations]

    now = datetime.now()
    print(f"Service {identity}, now = {now}\n")

    # Walk consecutive station pairs and find the current leg
    found = False
    for i in range(len(legs) - 1):
        a = legs[i]
        b = legs[i + 1]

        # A train departs station A, arrives station B.
        departed = a["departure"]
        due = b["arrival"]

        if departed and due and departed <= now <= due:
            print(f"CURRENTLY ON LEG: {a['name']} -> {b['name']}")
            print(f"  departed {departed}, due {due}")
            found = True
            break

    if not found:
        print("This service is not mid-journey right now.")
        print("First leg:", legs[0]["name"], "->", legs[1]["name"],
              "departs", legs[0]["departure"])