import { MapContainer, TileLayer,CircleMarker, Popup, Polyline} from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { useLeg } from '../hooks/useLeg'
import  ZoomToTrain from './ZoomToTrain'

const TILES = {
  dark: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
  light: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
}

export default function MapView({trains, theme, selectedUid, onSelect}){
    const selectedTrain=trains.find(
        t=>t.uid === selectedUid
    )
    const legcords = useLeg(selectedTrain)
    return(
    
    <div className="map-wrap">

    
    <MapContainer center={[53.4808, -2.2426]} zoom={10} className="map">
        <TileLayer
        key={theme}
        url={TILES[theme]}
        attribution='&copy; OpenStreetMap contributors &copy; CARTO'
      />
      {legcords && (
    <Polyline
      positions={legcords}
      pathOptions={{ color: '#4da3ff', weight: 4, opacity: 0.7 }}
    />
    
  )}
      {trains.map(train=>{
        const selected = train.uid=== selectedUid
        return(
            
            <CircleMarker 
            key={train.uid}
            center={[train.lat, train.lon]}
            radius={selected?9:5}
            eventHandlers={{click: ()=>onSelect(train.uid)}}
            pathOptions={{
               color: selected?'#4da3ff':'#9a9aa0',
                fillColor:selected?'#4da3ff':'#9a9aa0',
                fillOpacity:selected?1:0.7,
                weight: selected? 3:1,
            }}>
                <ZoomToTrain train={selectedTrain} />
                <Popup>
                    <strong>
                        {train.headcode || train.uid}
                    </strong>{train.isEstimate && ' est'} <br></br>
                    {train.operator}<br></br>
                    between {train.legFrom} and {train.legTo}
                </Popup>

            </CircleMarker>
        )
      })}

    </MapContainer>
    </div>
    )
}