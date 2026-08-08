"""
TrainRadar entry point.

Creates the Flask app, enables CORS for the React dev server, and registers
the API blueprint. All logic lives in services/ and api/.

Run:  python server.py
"""

import sys
from pathlib import Path

# Make the flat modules in app/ importable (rtt_client, osm_graph, etc.)
sys.path.insert(0, str(Path(__file__).parent / "app"))

from flask import Flask
from flask_cors import CORS

from api.routes import bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(bp)


if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True) 