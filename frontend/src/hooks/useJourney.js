import {useState,useEffect} from 'react'
export function useJourney(train) {
    const[journey, setJourney]= useState(null)

    useEffect(()=>{
        if (!train) {
            setJourney(null)
            return
        }
        const uid = train.uid
        const runDate=train.runDate
        if (!uid||!runDate){
            setJourney(null)
            return
        }
        let cancelled = false
        
        fetch(`http://127.0.0.1:5000/api/journey/${uid}/${runDate}`)
            .then(res=> res.ok ? res.json() : Promise.reject(res.status))
            .then(data =>{ 
                if (!cancelled) setJourney(data)
                 })
            .catch(() => {
                if (!cancelled) setJourney(null) })
        return () =>{
            cancelled=true}

    }, [train?.uid, train?.runDate])

    return journey
    
}
