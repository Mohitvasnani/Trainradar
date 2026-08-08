import {useEffect} from 'react'
import {useMap} from  'react-leaflet'

export default function ZoomToTrain({train}){
    const map = useMap()
    let uid = null
    if (train){
        uid=train.uid
    }
    useEffect(()=>{
        if (!train) return
        map.flyTo([train.lat,train.lon], 15, {duration:1.2})
    }, [uid])
    return null
}