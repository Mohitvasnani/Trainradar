import { MapContainer, TileLayer,CircleMarker, Popup, Polyline} from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { useLeg } from '../hooks/useLeg'
import  ZoomToTrain from './ZoomToTrain'
import { useJourney } from '../hooks/useJourney'

const TILES = {
  dark: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
  light: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
}

function fmt(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function stopLatLon(journey, crs) {
  const start = journey.legs.find(l => l.from === crs)
  if (start) return start.coordinates[0]
  const end = journey.legs.find(l => l.to === crs)
  if (end) return end.coordinates[end.coordinates.length - 1]
  return null
}

export default function MapView({trains, theme, selectedUid, onSelect}){
    const selectedTrain=trains.find(
        t=>t.uid === selectedUid
    )
    const journey = useJourney(selectedTrain)
    const legcords = useLeg(selectedTrain)
    return(
    
    <div className="map-wrap">
      <MapContainer center={[53.4808, -2.2426]} zoom={10} className="map">
        <TileLayer
          key={theme}
          url={TILES[theme]}
          attribution='&copy; OpenStreetMap contributors &copy; CARTO'
        />

        <ZoomToTrain train={selectedTrain} />

        {journey && journey.legs.map((leg, i) => (
          <Polyline
            key={`${leg.from}-${leg.to}-${i}`}
            positions={leg.coordinates}
            pathOptions={{
              color: leg.passed ? '#4caf7d' : '#8a8a90',
              weight: 4,
              opacity: leg.passed ? 0.85 : 0.5,
              dashArray: leg.passed ? null : '6 8',
            }}
          />
        ))}

        {journey && journey.stops.map(stop => {
          const latlon = stopLatLon(journey, stop.crs)
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
                {stop.isCancelled
                  ? 'Not calling here'
                  : stop.passed
                    ? `Departed ${fmt(stop.actualDep || stop.actualArr)}`
                    : `Due ${fmt(stop.schedArr || stop.schedDep)}`}
              </Popup>
            </CircleMarker>
          )
        })}

        {trains.map(train => {
          const selected = train.uid === selectedUid
          return (
            <CircleMarker
              key={train.uid}
              center={[train.lat, train.lon]}
              radius={selected ? 9 : 5}
              eventHandlers={{ click: () => onSelect(train.uid) }}
              pathOptions={{
                color: selected ? '#4da3ff' : '#9a9aa0',
                fillColor: selected ? '#4da3ff' : '#9a9aa0',
                fillOpacity: selected ? 1 : 0.7,
                weight: selected ? 3 : 1,
              }}
            >
              <Popup>
                <strong>{train.headcode || train.uid}</strong>{train.isEstimate && ' est'}<br />
                {train.operator}<br />
                between {train.legFrom} and {train.legTo}
              </Popup>
            </CircleMarker>
          )
        })}
      </MapContainer>
    </div>
    )
}