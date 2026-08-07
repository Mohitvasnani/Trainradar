import {useState,useEffect} from 'react'

export function useLeg(train){
    const [coords, setCoords]=useState(null)

    useEffect(() => {
        if (!train) {
            setCoords(null)
            return
        }
        const from =train.legFromCrs
        const to= train.legToCrs


        if(!from||!to){
            setCoords(null)
            return
        }
        let cancelled = false
        fetch(`http://127.0.0.1:5000/api/leg/${train.legFromCrs}/${train.legToCrs}`)
        .then(res=>{
            if (res.ok) {
                return res.json()
            } else {
                return Promise.reject(res.status)
            }
        })
        .then(
            data=>{
                if (!cancelled) {
                    setCoords(data.coordinates)
                }
            }
        )
        .catch(
            ()=> {
                if (!cancelled) {
                    setCoords(null)
                }

            }
        )
        return () => {
        cancelled = true}
    }, [train?.legFromCrs, train?.legToCrs]

     
)
return coords
}