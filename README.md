# TrainRadar

TrainRadar shows estimated live positions of GB passenger trains on a web map.

- Live map: https://trainradar-uk.vercel.app
- API: https://trainradar-223v.onrender.com

UK rail feeds don't publish GPS, so positions have to be inferred. The pipeline
takes the last reported passing point for a service, works out which leg the
train is on, looks up the routed track geometry for that leg, and interpolates
a position along the line using scheduled times.

Every position on the map is an estimate from schedule data. There is no GPS
or telemetry anywhere in the pipeline.

## Coverage

Geometry is precomputed nationally from OpenStreetMap and committed as
`backend/data/route_cache.json`.

| | |
|---|---|
| Station pairs from the national timetable | 4,962 |
| Pairs with plausible routed geometry | 4,566 (92.0%) |
| Rail graph | 468,538 nodes, 941,316 edges |
| Route cache | 6.24 MB, simplified at 5 m |

A leg with no usable geometry is not dropped. The train is still shown, marked
as approximate, with no track line drawn.

## Requirements

- Python 3.13 (3.11+ should work)
- Node.js 20+ with npm
- A Realtime Trains API account for a personal refresh token (api.rtt.io)

Rebuilding the rail graph needs considerably more: see that section below.

## Quick start

The route geometry is committed, so neither the OSM graph nor osmnx is needed
to run the app. This is the normal path.

### Backend

From `backend/`:

    python -m venv .venv
    .venv\Scripts\activate        # Windows
    source .venv/bin/activate     # macOS or Linux

    pip install -r requirements.txt

`requirements.txt` is the runtime set only. The graph-building and analysis
dependencies (osmnx, networkx, scipy, matplotlib) are in
`requirements-dev.txt`, and are only needed to regenerate geometry.

Copy `.env.example` to `.env` and add your Realtime Trains refresh token:

    RTT_REFRESH_TOKEN=your_refresh_token_here
    RTT_BASE_URL=https://data.rtt.io

No token is included in the repository. Without one the backend won't fetch
live data.

    python server.py

Flask runs on http://127.0.0.1:5000. `GET /api/status` reports cache size and
station coverage.

### Frontend

From `frontend/`:

    npm install

Copy `.env.example` to `.env`:

    VITE_API_BASE=http://127.0.0.1:5000
    VITE_CARTO_API_KEY=your_carto_api_key_here

    npm run dev

Vite runs on http://localhost:5173.

`VITE_` variables are inlined at build time, not read at runtime, so they have
to be set before the build runs.

## Rebuilding the rail graph and route cache

Only needed to regenerate geometry, for example to widen coverage or pick up
newer OpenStreetMap data. Needs `requirements-dev.txt` installed, the
`osmium-tool` command line program, roughly 3 GB of free disk, and a Network
Rail Open Data account for the SCHEDULE and CORPUS feeds.

The graph is **not** downloaded automatically. Overpass cannot serve a request
this size, so the source is a prebuilt Geofabrik extract filtered locally.

### 1. OSM extract

    conda install -c conda-forge osmium-tool

    curl.exe -L -o great-britain-latest.osm.pbf https://download.geofabrik.de/europe/great-britain-latest.osm.pbf

    osmium tags-filter -o gb-rail.osm.pbf great-britain-latest.osm.pbf w/railway=rail
    osmium tags-filter -i -o gb-rail-main.osm.pbf gb-rail.osm.pbf w/service=yard w/service=siding w/service=spur w/service=crossover w/usage=industrial
    osmium cat -o gb-rail.osm gb-rail-main.osm.pbf

Pass one keeps railway ways plus every node they reference. Pass two drops
yard, siding, spur, crossover and industrial track. Put the output in
`osm-data/`, which is gitignored.

### 2. Build the graph

From `backend/`:

    python -c "from app.osm_graph import _download_graph; _download_graph()"

Reads `osm-data/gb-rail.osm`, removes orphan nodes left behind by the second
osmium pass, and writes `backend/data/rail_graph.graphml` (395 MB, gitignored).
Three minutes or so.

`STITCH_ENABLED` in `app/osm_graph.py` optionally joins disconnected track
ends. It is off: measured at 20 m it added 105 connectors and zero routable
legs.

### 3. Adjacency, diagnostics and warming

From `backend/scripts/`:

    python build_adjacency.py <schedule.json> <corpus.json> adjacency.json
    python filter_adjacency.py
    python diagnose_routing.py
    python warm_route_cache.py

`build_adjacency.py` streams the SCHEDULE extract (3.6 GB, never loaded whole)
and records consecutive calling points as station pairs.
`filter_adjacency.py` drops junction codes and splits resolved from
unresolved. `diagnose_routing.py` routes every pair and buckets the results.
`warm_route_cache.py` writes `backend/data/route_cache.json`.

`split_no_path.py`, `casualty_ratios.py` and `stitch_report.py` are analysis
scripts for the legs that fail.

## API endpoints

| Endpoint | Returns |
|---|---|
| `GET /api/status` | Health check: cached routes, station coverage |
| `GET /api/trains` | Running services with estimated positions |
| `GET /api/departures/<crs>` | Departure board for a station, by CRS code |
| `GET /api/leg/<crs_a>/<crs_b>` | Routed track geometry between two stations |
| `GET /api/legs` | Geometry for every leg currently occupied |
| `GET /api/journey/<uid>/<run_date>` | Full calling pattern for one service |

## Tests

From `backend/`:

    pytest testing_suite

Unit tests for the estimation pipeline: schedule parsing, leg selection,
position interpolation, geometry helpers, and route plausibility. Tests use
fixture data and don't hit the live API, so no token is needed. CI runs the
same command on every push.

## Reproducing the evaluation

`evaluation/measure_error.py` is the accuracy harness. It samples running
services, computes an estimated position for a point in a journey where the
true reporting-point position later becomes known, and records the distance
between the two.

    cd backend
    python evaluation/measure_error.py

Each run appends to a CSV of per-sample errors. The runs used in the
dissertation are in `evaluation/results/`:

| File | Collection window |
|---|---|
| `morning.csv` | Morning peak |
| `error_results.csv` | Afternoon |
| `evening.csv` | Evening peak |
| `quiet_time.csv` | Off-peak, full day |

Since the harness samples whatever is running at the time, a fresh run won't
reproduce these rows exactly. The included CSVs are the data behind the
figures and statistics in Chapter 5.

## Deployment

Backend on Render via `render.yaml`: `rootDir` is `backend`, served by
waitress, with `ALLOWED_ORIGINS`, `RTT_REFRESH_TOKEN` and `RTT_BASE_URL` set
in the dashboard. A `Dockerfile` is included as an alternative. Both install
`requirements.txt` only, which is why the graph must not be a runtime
dependency.

Frontend on Vercel with root directory `frontend`. Set `VITE_API_BASE` and
`VITE_CARTO_API_KEY` before the build runs.

## Project layout

    backend/
      server.py              Flask entry point
      api/routes.py          HTTP endpoints
      app/                   Core estimation pipeline
        rtt_client.py        Realtime Trains API client
        osm_graph.py         Rail graph build, orphan removal, stitching
        stations.py          CRS code to coordinate lookup
        find_current_leg.py  Which leg a train is on
        route_leg.py         Routing over the rail graph
        track_builder.py     Routed geometry assembly
        estimate.py          Position interpolation
      services/              Application services
        auth.py              Access token lifecycle
        cache.py             Route and departure board caching
        estimation.py        Pipeline orchestration
        geometry.py          Distance, plausibility, straight-line fallback
        state.py             Shared graph and last-known-good state
      data/
        stations.csv         Station coordinates
        route_cache.json     Precomputed national leg geometry
      scripts/               Geometry pipeline and analysis
      testing_suite/         Unit tests
      dev_diagnostics/       Dev scripts that render Folium maps
      evaluation/            Accuracy harness and collected results

    frontend/
      src/
        App.jsx              Root component
        api/                 Backend client
        components/          Map, sidebar, search, train detail panel
        hooks/               Data fetching and selection state
        css/                 Per-component styles

`dev_diagnostics/` holds scripts written during development to render single
journeys and routed legs to standalone HTML maps. They were used to debug the
geometry layer and are kept as a record of how the pipeline was verified, not
as part of the running app.

## Data sources and licensing

The licence in `LICENSE` covers this repository's source code. The data has
its own terms:

- **Rail network geometry**: OpenStreetMap, via a Geofabrik extract.
  © OpenStreetMap contributors, licensed under the Open Database Licence
  (ODbL). `backend/data/route_cache.json` is a derived database and carries
  the same obligations.
- **Timetable adjacency**: derived from Network Rail SCHEDULE and CORPUS open
  data feeds, used under the Network Rail open data terms.
  `backend/scripts/adjacency_*.json` is derived from them.
- **Live reporting data**: Realtime Trains API (api.rtt.io), used under a
  personal developer account. Not redistributed here.
- **Station coordinates**: publicly published UK station data.
- **Map tiles**: CARTO basemaps, rendered with Leaflet and react-leaflet.

Libraries: OSMnx, NetworkX, Shapely, GeoPy, SciPy, Flask, React, Leaflet.

## Known limitations

- 396 of 4,962 station pairs have no usable geometry: 321 cannot be routed,
  31 have no track within snapping distance, and 44 route only implausibly.
  Those trains are shown as approximate, with no line drawn.
- A further 164 pairs are held aside in `adjacency_unresolved.json` because
  their CRS codes are missing from `stations.csv`, mostly Elizabeth line
  platforms. NaPTAN is the intended fix.
- Positions are estimates from schedule data, not observations. Accuracy drops
  between sparsely spaced reporting points and for heavily delayed services.
  Error correlates more strongly with leg duration than with lateness.
- Plausibility uses a fixed ratio of 1.5 against straight-line distance, which
  is scale-dependent and over-rejects short legs where snapping error
  dominates.
- Which trains appear is limited by the station boards polled, not by
  geometry. Widening that is bounded by the Realtime Trains request quota.
- Route and departure board caching is in-process, so a restart or a free-tier
  spin-down clears it.
- Underground, metro, light rail and tram networks are excluded, both from the
  graph filter and from the national timetable feed.

## Licence

See `LICENSE`.
