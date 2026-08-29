import csv
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "stations.csv")


def load_station_coords():
    
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


# 
    

    for crs in ["LIV", "EDG", "MCO", "WAC"]:
        print(f"  {crs}: {coords.get(crs)}")