// Basemap configuration.
//
// CARTO began requiring an API key on its raster tiles in late 2026:
// keyless requests still return HTTP 200, but every tile is stamped
// "API KEY REQUIRED", so the map looks broken while every status check
// passes. The map fell back to Esri Gray Canvas while that stood.
//
// A working CARTO key is now in place, so the map is back on CARTO's
// raster tiles. These are the {z}/{x}/{y} PNG endpoints, not the
// vector-tile style.json: Leaflet's TileLayer renders raster only, and
// a GL style would need maplibre-gl plus a Leaflet bridge layer.
//
// The basemap has to stay visually quiet so train markers and route
// polylines read clearly on top of it, which is what Positron and Dark
// Matter are for. Voyager is the more colourful option, kept as a third
// choice rather than a default.

const CARTO_KEY = import.meta.env.VITE_CARTO_KEY || 'cb1_33gh_1_ef35ef8db96579e92177048b'
const CARTO_BASE = 'https://basemaps.cartocdn.com/rastertiles'
const CARTO_ATTRIBUTION =
  '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'

function carto(style) {
  return `${CARTO_BASE}/${style}/{z}/{x}/{y}.png?key=${CARTO_KEY}`
}

export const LAYERS = {
  light: {
    label: 'Light',
    url: carto('light_all'),
    attribution: CARTO_ATTRIBUTION,
    maxZoom: 20,
    maxNativeZoom: 20,
  },
  dark: {
    label: 'Dark',
    url: carto('dark_nolabels'),
    attribution: CARTO_ATTRIBUTION,
    maxZoom: 20,
    maxNativeZoom: 20,
  },
  voyager: {
    label: 'Voyager',
    url: carto('voyager'),
    attribution: CARTO_ATTRIBUTION,
    maxZoom: 20,
    maxNativeZoom: 20,
  },
}
