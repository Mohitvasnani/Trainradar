import { useState, useEffect } from 'react'
import { API_BASE } from '../api/base'

export function allLegs() {
  const [legs, setLegs] = useState([])

  useEffect(() => {
    let cancelled = false
        fetch(API_BASE + '/api/legs')
    fetch('http://127.0.0.1:5000/api/legs')
      .then(res => {
        if (res.ok) return res.json()
        throw new Error('Failed')
      })
      .then(data => {
        if (!cancelled) setLegs(data.legs || [])
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