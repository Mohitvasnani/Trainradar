import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.absolute()
APP_DIR = BASE_DIR / "app"

sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(APP_DIR))