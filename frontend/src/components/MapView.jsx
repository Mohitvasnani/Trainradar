import { MapContainer, TileLayer,CircleMarker, Popup, Polyline} from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

import  ZoomToTrain from './ZoomToTrain'
import { useJourney } from '../hooks/useJourney'
import {useState} from 'react'
import Switcher from './Switcher'
import { allLegs } from '../hooks/allLegs'
import Legend from "./Legend";
import TrainInfo from "./TrainInfo";





const LAYERS = {
  dark: {
    label: 'Dark',
    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
  },
  light: {
    label: 'Light',
    url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
  },
  terrain: {
    label: 'Terrain',
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenStreetMap contributors, SRTM | &copy; OpenTopoMap (CC-BY-SA)',
    maxZoom: 17,
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
export default function MapView({trains,  selectedUid, onSelect, pinnedJourneys}){
    const selectedTrain=trains.find(
        t=>t.uid === selectedUid
    )
    const { journey, loading } = useJourney(selectedTrain)
   
    const [layer, setLayer] = useState('dark')
  const tiles = LAYERS[layer]
  
  const all = allLegs()
    return(
    
    <div className="map-wrap">
     
       <Switcher layer={layer} onChange={setLayer} layers={LAYERS} />
      <MapContainer center={[53.4808, -2.2426]} zoom={10} className="map">
        <TileLayer
          key={layer}
          url={tiles.url}
          attribution={tiles.attribution} maxZoom={tiles.maxZoom||19}
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
  return journey.legs.map((leg, i) => (
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
        click: function() {
          onSelect(train.uid)
        }
      }}
      pathOptions={{
        color: markerColor,
        fillColor: markerColor,
        fillOpacity: isSelected ? 1 : 0.7,
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