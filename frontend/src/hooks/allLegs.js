import { useState, useEffect } from 'react'

export function allLegs() {
  const [legs, setLegs] = useState([])

  useEffect(() => {
    let cancelled = false
    fetch('http://127.0.0.1:5000/api/legs')
      .then(res => res.ok ? res.json() : Promise.reject(res.status))
      .then(data => { if (!cancelled) setLegs(data.legs || []) })
      .catch(() => { if (!cancelled) setLegs([]) })
    return () => { cancelled = true }
  }, [])

  return legs
}