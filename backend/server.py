from flask import Flask, jsonify, abort
from datetime import datetime
from app import rtt_client

app = Flask(__name__)

#####################################
#RTT access token management
_token = None 
_token_expiry = None

def get_token():
    """here we will return a valid token everytime if its expired or missing it will refresh"""
    global  _token, _token_expiry
    now = datetime.now().timestamp()
    if _token is None or _token_expiry is None or now>= _token_expiry:
        token, valid_until = rtt_client.get_access_token()
        print(repr(valid_until))
        expiry = datetime.fromisoformat(valid_until).timestamp()-60
        _token = token
        _token_expiry = expiry
    return _token

@app.route("/")
def home():
   return "TrainRadar API is running "


    
@app.route("/api/status")
def status():
    return jsonify({
        "status": "ok",
        "service": "trainradar"
    })

@app.route("/api/train")
def train():
    return jsonify({
        "serviceUid": "P70998",
        "operator": "Northern",
        "position": {"lat": 53.4839, "lon": -2.2446},
        "fraction": 0.42,
        "timestamp": datetime.now().isoformat()
    })



@app.route("/api/departures/<crs>")
def departures(crs):
    crs = crs.upper()
    token = get_token()
    board = rtt_client.get_location_board(token, code=crs)

    services = []
    for svc in board.get("services", []):
        meta = svc.get("scheduleMetadata", {})
        operator = meta.get("operator", {})

        origin_list = svc.get("origin") or [{}]
        dest_list = svc.get("destination") or [{}]

        temporal = svc.get("temporalData", {})
        arrival = temporal.get("arrival") or {}
        departure = temporal.get("departure") or {}
        lateness = departure.get("realtimeAdvertisedLateness")
        if lateness is None:
            lateness = arrival.get("realtimeAdvertisedLateness")

        services.append({
            "uid": meta.get("identity"),
            "runDate": meta.get("departureDate"),
            "operator": operator.get("name"),
            "origin": origin_list[0].get("location", {}).get("description"),
            "destination": dest_list[0].get("location", {}).get("description"),
            "latenessMinutes": lateness,
            "isCancelled": arrival.get("isCancelled", False) or departure.get("isCancelled", False),
            "status": temporal.get("status"),
        })

    return jsonify({"station": crs, "services": services})

if __name__ == "__main__":
    app.run(debug=True)
