import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

function App() {
  const [trains, setTrains] = useState([])

  useEffect(() => {
    const load = () => {
      fetch('http://127.0.0.1:5000/api/trains')
        .then(res => res.json())
        .then(data => {
          console.log(new Date().toLocaleTimeString(), 'got:', data.count, 'trains')
          setTrains(data.trains)
        })
        .catch(err => console.error('fetch failed:', err))
    }

    load()
    const id = setInterval(load, 30000)
    return () => clearInterval(id)
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
            <strong>{train.headcode || train.uid}</strong>{train.isEstimate && ' · est.'}<br />
            {train.operator}<br />
            between {train.legFrom} and {train.legTo}<br />
            {train.latenessMinutes ? `${train.latenessMinutes} min late` : 'on time'}
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  )
}

export default App