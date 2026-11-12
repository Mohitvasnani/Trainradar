# TrainRadar frontend

React and Leaflet map client for the TrainRadar API. See the
[repository README](../README.md) for the project as a whole, the estimation
pipeline, and the coverage figures.

## Running locally

    npm install
    cp .env.example .env
    npm run dev

Vite serves on http://localhost:5173. `VITE_API_BASE` must point at a running
backend, `http://127.0.0.1:5000` by default.

`VITE_` variables are inlined at build time rather than read at runtime, so
they have to be set before `npm run build` runs, not after.

## Layout

    src/
      App.jsx          Root component, owns selection and pin state
      api/             Backend client
      components/      Map, sidebar, search, legend, train detail panel
      hooks/           Data fetching, journey and leg geometry, pinning
      css/             Per-component styles
      theme.css        Light and dark custom properties

Basemaps are CARTO Positron, Dark Matter and Voyager, served without an API
key.

## Scripts

| Command | Does |
|---|---|
| `npm run dev` | Dev server with HMR |
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Serve the built output |
| `npm run lint` | ESLint |

## Deployment

Vercel, with root directory `frontend` and `VITE_API_BASE` set to the deployed
API origin before the build runs.
