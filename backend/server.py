from flask import Flask, jsonify, abort
from datetime import datetime
from app import rtt_client

app = Flask(__name__)

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
    data = rtt_client.your_function_here(crs)   # ← the only real change
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
