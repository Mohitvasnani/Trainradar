import os
import requests
from dotenv import load_dotenv

# Load variables from backend/.env
load_dotenv()

REFRESH_TOKEN = os.getenv("RTT_REFRESH_TOKEN")
BASE_URL = os.getenv("RTT_BASE_URL", "https://data.rtt.io")


def get_access_token():
    """Exchange the long-life refresh token for a short-life access token."""
    resp = requests.get(
        f"{BASE_URL}/api/get_access_token",
        headers={"Authorization": f"Bearer {REFRESH_TOKEN}"},
    )
    resp.raise_for_status()
    data = resp.json()
    return data["token"], data["validUntil"]


def get_location_board(access_token, code="LIV"):
    """Fetch the services at a station (Network Rail namespace)."""
    resp = requests.get(
        f"{BASE_URL}/gb-nr/location",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"code": code},
    )
    resp.raise_for_status()
    return resp.json()


def get_service(access_token, identity, departure_date):
    """Fetch a single service's full journey (all timing points)."""
    resp = requests.get(
        f"{BASE_URL}/gb-nr/service",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"identity": identity, "departureDate": departure_date},
    )
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    from datetime import date

    token, valid_until = get_access_token()
    print(f"Got access token, valid until {valid_until}\n")

    board = get_location_board(token, code="LIV")
    services = board.get("services", [])
    if not services:
        print("No services found at LIV right now.")
        raise SystemExit

    first = services[0]
    identity = first.get("scheduleMetadata", {}).get("identity")
    today = date.today().isoformat()
    print(f"Querying service {identity} for {today}\n")

    service = get_service(token, identity=identity, departure_date=today)
    svc = service.get("service", {})
    locations = svc.get("locations", [])
    print(f"Service {identity} has {len(locations)} timing points:\n")

    for loc in locations:
        location = loc.get("location", {})
        place = location.get("description", "?")
        short_codes = location.get("shortCodes") or []
        long_codes = location.get("longCodes") or []
        short = short_codes[0] if short_codes else "?"
        long = long_codes[0] if long_codes else "?"
        temporal = loc.get("temporalData", {})

        def pick(kind):
            block = temporal.get(kind) or {}
            return block.get("scheduleAdvertised") or block.get("scheduleInternal")

        time = pick("departure") or pick("arrival") or pick("pass") or "?"
        print(f"  {place:<26} {short:<5} {long:<9} {time}")