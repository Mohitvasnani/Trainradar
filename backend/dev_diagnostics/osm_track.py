import webbrowser
import requests
import folium
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def fetch_rail_geometry(south, west, north, east):
    query = f"""
    [out:json][timeout:60];
    way["railway"="rail"]({south},{west},{north},{east});
    out geom;
    """
    headers = {"User-Agent": "TrainRadar/0.1 (MSc dissertation project)"}
    resp =requests.post(OVERPASS_URL,data={"data": query},headers=headers)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    south, west, north, east = 53.35, -3.05, 53.48, -2.85

    data =fetch_rail_geometry(south, west,
                               north, east)
    ways =data.get("elements", [])
    print(f"Fetched {len(ways)} rail track segments")

    m = folium.Map(location=[(south+north)/2, (west + east) /2],zoom_start=12)
    for way in ways:
        coords=[(pt["lat"],pt["lon"]) for pt in way.get("geometry", [])]
        if coords:
            folium.PolyLine(coords, 
                            color="black",
                              weight=2, 
                              opacity=0.6).add_to(m)

    out = "track_map.html"
    m.save(out)
    print(f"Map saved to {out}")
    webbrowser.open(out)