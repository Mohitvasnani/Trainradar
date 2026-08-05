import { useState, useEffect } from 'react'
import { fetchTrains } from '../api/trains'

export function useTrains(intervalMs = 60000) {
  const [trains, setTrains] = useState([])
  const [updatedAt, setUpdatedAt] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false

    const load = async () => {
      try {
        const data = await fetchTrains()
        if (cancelled) return
        setTrains(data.trains)
        setUpdatedAt(new Date())
        setError(null)
      } catch (err) {
        if (!cancelled) setError(err.message)
      }
    }

    load()
    const id = setInterval(load, intervalMs)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [intervalMs])

  return { trains, updatedAt, error }
}