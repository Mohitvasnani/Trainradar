import { useState, useEffect } from 'react'
import { fetchTrains } from '../api/trains'

export function useTrains(intervalMs = 60000) {
  const [trains, setTrains] = useState([])
  const [updatedAt, setUpdatedAt] = useState(null)
  const [error, setError] = useState(null)
  const [stale, setStale] = useState(false)

  useEffect(() => {
    
    async function getTrains() {
      try {
        const result = await fetchTrains()
        setTrains(result.trains)
        setUpdatedAt(new Date())
        setError(null)
        

        if (result.stale    === true) {
          setStale(true)
        } else{
          setStale(false)}
      } catch (err) {
        setError(err.message)
      }}    
    getTrains()
    
    
    const intervalId =setInterval(
      getTrains, intervalMs)
    
    
    return function cleanup() {
      clearInterval(intervalId)
    }}, [intervalMs])

  return {
    trains, updatedAt, 
    error, stale}}