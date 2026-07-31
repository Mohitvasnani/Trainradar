import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

function App() {
  const [trains, setTrains] = useState([])

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/trains')
      .then(res => res.json())
      .then(data => {
        console.log('got:', data)
        setTrains(data.trains)
      })
      .catch(err => console.error('fetch failed:', err))
  }, [])

  return (
    <MapContainer
      center={[53.4808, -2.2426]}
      zoom={10}
      style={{ height: '100vh', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />
      {trains.map(train => (
        <CircleMarker
          key={train.uid}
          center={[train.lat, train.lon]}
          radius={6}
          pathOptions={{ color: 'red', fillColor: 'red', fillOpacity: 0.8 }}
        >
          <Popup>
            <strong>{train.uid}</strong><br />
            {train.operator}<br />
            {train.legFrom} → {train.legTo}
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  )
}

export default App