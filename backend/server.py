import sys
import time
from pathlib import Path

_start = time.time()

BASE_directory = Path(__file__).parent.absolute()
APP_directory = BASE_directory / "app"

sys.path.insert(0, str(BASE_directory))
sys.path.insert(0, str(APP_directory))

from flask import Flask
from flask_cors import CORS
from api.routes import bp
from services import cache

app = Flask(__name__)
CORS(app)
app.register_blueprint(bp)

cache.load_route_cache()
print(f"boot took {time.time() - _start:.2f}s")

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True, use_reloader=False)