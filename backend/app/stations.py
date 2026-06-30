import csv
import os

# Path to the CSV relative to this file
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "stations.csv")


def load_station_coords():
    """Return a dict mapping CRS code -> (lat, lon)."""
    coords = {}
    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            crs = row.get("crsCode", "").strip()
            lat = row.get("lat", "").strip()
            lon = row.get("long", "").strip()
            if crs and lat and lon:
                coords[crs] = (float(lat), float(lon))
    return coords


if __name__ == "__main__":
    coords = load_station_coords()
    print(f"Loaded {len(coords)} stations with coordinates")
    # Spot check a few from your route
    for crs in ["LIV", "EDG", "MCO", "WAC"]:
        print(f"  {crs}: {coords.get(crs)}")