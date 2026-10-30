# TrainRadar

TrainRadar shows estimated live positions of GB passenger trains on a web map.

UK rail feeds don't publish GPS, so positions have to be inferred. The pipeline
takes the last reported passing point for a service, works out which leg the
train is on, routes that leg over the OpenStreetMap rail network, and
interpolates a position along the routed line using scheduled times.

Every position on the map is an estimate from schedule data. There is no GPS
or telemetry anywhere in the pipeline.

## Requirements

- Python 3.13 (3.11+ should work)
- Node.js 20+ with npm
- A Realtime Trains API account for a personal refresh token (api.rtt.io)
- ~100 MB free disk space for the cached rail graph
- Internet access on first run

## Setup

### Backend

From `backend/`:

    python -m venv .venv
    .venv\Scripts\activate        # Windows
    source .venv/bin/activate     # macOS or Linux

    pip install -r requirements.txt

### API credentials

copy `.env.example` to `.env` and add your Realtime Trains refresh token:

    RTT_REFRESH_TOKEN=your_refresh_token_here
    RTT_BASE_URL=https://data.rtt.io

no token is included in the archive. Without one the backend won't fetch live data.

### Rail network graph

`backend/data/rail_graph.graphml` is not included (it's 64 MB and derived from
OpenStreetMap). It's regenerated automatically.

on first backend start, `app/osm_graph.py` sees the file is missing, downloads
the rail network for the study area from the Overpass API, and saves it. The
bounding box is roughly the Liverpool to Leeds corridor and surroundings.

First download takes several minutes and needs a stable connection. Later
starts load the cached file in a few seconds.

### Frontend

From `frontend/`:    npm install

## Running

2 terminals.

Terminal 1, backend:

    cd backend
    python server.py

Flask runs on http://127.0.0.1:5000. First start blocks while the rail
graph downloads or loads. `GET /api/status` reports the node count once
it's ready.

Terminal 2, frontend:

    cd frontend
    npm run dev

vite runs on http://localhost:5173. Open that in a browser.

the frontend hardcodes the backend URL as http://127.0.0.1:5000 (see
`frontend/src/api/trains.js`). if you run Flask on a different port,
change that constant.

## API endpoints



 `GET /api/status` -> Health check: graph size, cached routes, station coverage 
`GET /api/trains` -> currently running services in the covered area, with estimated positions 
 `GET /api/departures/<crs>` -> Departure board for a station, by CRS code 
 `GET /api/leg/<crs_a>/<crs_b>` -> Routed track geometry between two stations 
 `GET /api/legs` -> geometry for every leg currently occupied 
 `GET /api/journey/<uid>/<run_date>` -> Full calling pattern for one service 

## Tests

From `backend/`:

    pytest testing_suite

`testing_suite/` has unit tests for the estimation pipeline: schedule
parsing, leg selection, position interpolation, geometry helpers, and
route plausibility. Tests use fixture data and don't hit the live API,
so no token is needed.

## Reproducing the evaluation

`evaluation/measure_error.py` is the accuracy harness. It samples running
services, computes an estimated position for a point in a journey where
the true reporting-point position later becomes known, and records the
distance between the two.

    cd backend
    python evaluation/measure_error.py

Each run appends to a CSV of per-sample errors. The runs used in the
dissertation are in `evaluation/results/`:

| File | Collection window |

| `morning.csv` | Morning peak |
| `error_results.csv` | Afternoon |
| `evening.csv` | Evening peak |
| `quiet_time.csv` | Off-peak, full day |

Since the harness samples whatever is running at the time, a fresh run
won't reproduce these rows exactly. The included CSVs are the data behind
the figures and statistics in Chapter 5.

## Project layout

    backend/
      server.py              Flask entry point
      api/routes.py          HTTP endpoints
      app/                   Core estimation pipeline
        rtt_client.py        Realtime Trains API client
        osm_graph.py         Rail network download and caching
        stations.py          CRS code to coordinate lookup
        find_current_leg.py  Which leg a train is on
        route_leg.py         Shortest path over the rail graph
        track_builder.py     Routed geometry assembly
        estimate.py          Position interpolation
      services/              Application services
        auth.py              Access token lifecycle
        cache.py             Route and departure board caching
        estimation.py        Pipeline orchestration
        geometry.py          Distance and interpolation helpers
        state.py             Shared graph and last-known-good state
      data/stations.csv      Station coordinates
      testing_suite/         Unit tests
      dev_diagnostics/       Dev scripts that render Folium maps
      evaluation/            Accuracy harness and collected results
      make_fragmentation_figure.py

    frontend/
      src/
        App.jsx              Root component
        api/trains.js        Backend client
        components/          Map, sidebar, search, train detail panel
        hooks/               Data fetching and selection state
        css/                 Per-component styles

`dev_diagnostics/` holds scripts written during development to render
single journeys and routed legs to standalone HTML maps. They were used
to debug the geometry layer and are included as a record of how the
pipeline was developed and verified, not as part of the running app.

## Data and libraries used

- Rail network geometry: OpenStreetMap via OSMnx and the Overpass API
  (© OpenStreetMap contributors, ODbL)
- Schedule and live reporting data: Realtime Trains API (api.rtt.io),
  used under a personal developer account
- Station coordinates: derived from publicly published UK station data
- Map tiles and rendering: Leaflet and react-leaflet
- Rail graph handling: OSMnx and NetworkX
- Geometry helpers: Shapely and GeoPy

## Known limitations

- Coverage is limited to the bounding box in `app/osm_graph.py`. Trains
  outside it aren't tracked.
- Positions are estimates from schedule data, not observations. Accuracy
  drops between sparsely spaced reporting points and for heavily delayed
  services.
- The rail graph uses `simplify=False` and `retain_all=True`, which keeps
  the raw OSM topology including disconnected fragments. If a leg can't be
  routed across a fragment boundary, the system reports no track for that
  leg rather than drawing a wrong one.
- Route and departure board caching is in-process. Restarting the backend
  clears it.