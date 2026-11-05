import { useState, useEffect } from 'react'
import { API_BASE } from '../api/base'

export function useAllLegs() {
  const [legs, setLegs] = useState([])

  useEffect(() => {
    let cancelled = false

    fetch(`${API_BASE}/api/legs`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => {
        if (!cancelled) setLegs(data.legs ?? [])
      })
      .catch(() => {
        if (!cancelled) setLegs([])
      })

    return () => {
      cancelled = true
    }
  }, [])

  return legs
}