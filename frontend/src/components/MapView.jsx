import { MapContainer, TileLayer, CircleMarker, Popup, Polyline } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

import ZoomToTrain from './ZoomToTrain'
import { useJourney } from '../hooks/useJourney'
import { useState } from 'react'
import Switcher from './Switcher'
import { useAllLegs } from '../hooks/allLegs'
import Legend from "./Legend";
import TrainInfo from "./TrainInfo";

// CARTO's raster basemaps serve without a key. The variable stays supported
// in case an account ever requires one, but an empty value must not be sent:
// "?key=" with nothing after it returns watermarked tiles.
const CARTO_API_KEY = import.meta.env.VITE_CARTO_API_KEY || ''
const CARTO_SUFFIX = CARTO_API_KEY ? '?key=' + CARTO_API_KEY : ''

const LAYERS = {
  light: {
    label: 'Light',
    url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png' + CARTO_SUFFIX,
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    maxZoom: 20,
  },
  dark: {
    label: 'Dark',
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png' + CARTO_SUFFIX,
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    maxZoom: 20,
  },
}

function fmt(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function getStopPosition(journey, crs) {
  for (let i = 0; i < journey.legs.length; i++) {
    const leg = journey.legs[i]
    if (leg.from === crs) {
      return leg.coordinates[0]
    }
    if (leg.to === crs) {
      return leg.coordinates[leg.coordinates.length - 1]
    }
  }
  return null
}

export default function MapView({ trains, selectedUid, onSelect, pinnedJourneys }) {
  const selectedTrain = trains.find(t => t.uid === selectedUid)
  const { journey, loading } = useJourney(selectedTrain)

  const [layer, setLayer] = useState('dark')
  const tiles = LAYERS[layer]

  const all = useAllLegs()

  return (
    <div className="map-wrap">
      <Switcher layer={layer} onChange={setLayer} layers={LAYERS} />
      <MapContainer center={[53.4808, -2.2426]} zoom={10} className="map">
        <TileLayer
          key={layer}
          url={tiles.url}
          attribution={tiles.attribution}
          maxZoom={tiles.maxZoom || 19}
        />

        {all.map((leg, i) => (
          <Polyline
            key={`bg-${leg.from}-${leg.to}-${i}`}
            positions={leg.coordinates}
            pathOptions={{ color: '#4a4a52', weight: 2, opacity: 0.6 }}
          />
        ))}

        <ZoomToTrain train={selectedTrain} />

        {journey && journey.legs.map((leg, i) => {
          // No geometry means no line. An approximate leg is a straight
          // segment between two stations, which would cut through buildings
          // and claim track that isn't there. The train marker still shows,
          // hollow, so the service stays visible without the map lying.
          if (leg.approximate) return null

          let lineColor = '#8a8a90'
          let lineDash = '6 8'
          let lineOpacity = 0.5

          if (leg.passed) {
            lineColor = '#4caf7d'
            lineDash = null
            lineOpacity = 0.85
          }

          return (
            <Polyline
              key={leg.from + '-' + leg.to + '-' + i}
              positions={leg.coordinates}
              pathOptions={{
                color: lineColor,
                weight: 4,
                opacity: lineOpacity,
                dashArray: lineDash,
              }}
            />
          )
        })}

        {pinnedJourneys && Object.keys(pinnedJourneys).map(uid => {
          const journey = pinnedJourneys[uid]
          return journey.legs.filter(leg => !leg.approximate).map((leg, i) => (
            <Polyline
              key={'pin-' + uid + '-' + i}
              positions={leg.coordinates}
              pathOptions={{ color: '#e0a030', weight: 3, opacity: 0.5 }}
            />
          ))
        })}

        {journey && journey.stops.map(stop => {
          const latlon = getStopPosition(journey, stop.crs)
          if (!latlon) return null
          return (
            <CircleMarker
              key={stop.crs}
              center={latlon}
              radius={4}
              pathOptions={{
                color: stop.isCancelled ? '#b3372a' : stop.passed ? '#4caf7d' : '#8a8a90',
                fillColor: stop.isCancelled ? '#b3372a' : stop.passed ? '#4caf7d' : '#1c1c1e',
                fillOpacity: 1,
                weight: 2,
              }}
            >
              <Popup>
                <strong>{stop.name}</strong><br />
                {stop.isCancelled && 'Not calling here'}
                {!stop.isCancelled && stop.passed && `Departed ${fmt(stop.actualDep || stop.actualArr)}`}
                {!stop.isCancelled && !stop.passed && `Due ${fmt(stop.schedArr || stop.schedDep)}`}
              </Popup>
            </CircleMarker>
          )
        })}

        {trains.map(train => {
          const isSelected = train.uid === selectedUid
          let markerColor = '#9a9aa0'
          let markerRadius = 5

          if (isSelected) {
            markerColor = '#4da3ff'
            markerRadius = 9
          }

          return (
            <CircleMarker
              key={train.uid}
              center={[train.lat, train.lon]}
              radius={markerRadius}
              eventHandlers={{
                click: function () {
                  onSelect(train.uid)
                }
              }}
              pathOptions={{
                color: markerColor,
                fillColor: markerColor,
                fillOpacity: train.isApproximate ? 0 : (isSelected ? 1 : 0.25),
                dashArray: train.isApproximate ? '3 3' : null,
                weight: isSelected ? 3 : 1,
              }}
            >
              <Popup>
                <strong>{train.headcode || train.uid}</strong>
                {train.isEstimate && ' est'}
                <br />
                {train.operator}
                <br />
                between {train.legFrom} and {train.legTo}
              </Popup>
            </CircleMarker>
          )
        })}
      </MapContainer>
      <TrainInfo train={selectedTrain} journey={journey} loading={loading} onClose={() => onSelect(null)} />
      <Legend />
    </div>
  )
}