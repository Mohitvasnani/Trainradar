"""
Train radar entry point 
"""

import sys
from pathlib import Path


BASE_directory = Path(__file__).parent.absolute()
APP_directory= BASE_directory / "app"

sys.path.insert(0, str(BASE_directory))
sys.path.insert(0, str(APP_directory))

from flask import Flask
from flask_cors import CORS
from api.routes import bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(bp)

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True)