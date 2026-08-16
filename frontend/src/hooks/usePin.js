import { useState, useEffect, useRef } from 'react'

const MAX_PINNED = 2

export function usePin(trains, intervalMs = 60000) {
  const [pinnedUids, setPinnedUids] = useState([])
  const [journeys, setJourneys] = useState({})
  const [notifications, setNotifications] = useState([])
  const previous = useRef({})

  function togglePin(uid) {
    setPinnedUids(current => {
      if (current.includes(uid)) {
        return current.filter(u => u !== uid)
      }
      if (current.length >= MAX_PINNED) {
        return [current[1], uid]
      }
      return [...current, uid]
    })
  }

  function dismiss(id) {
    setNotifications(current => current.filter(n => n.id !== id))
  }

  useEffect(() => {
    if (pinnedUids.length === 0) {
      setJourneys({})
      previous.current = {}
      return
    }

    let cancelled = false

    async function load() {
      const next = {}
      const fresh = []

      for (const uid of pinnedUids) {
        const train = trains.find(t => t.uid === uid)
        if (!train || !train.runDate) {
          continue
        }
        try {
          const res = await fetch(
            `http://127.0.0.1:5000/api/journey/${uid}/${train.runDate}`
          )
          if (!res.ok) {
            continue
          }
          const data = await res.json()
          next[uid] = data

          const before = previous.current[uid]
          if (before) {
            for (const stop of data.stops) {
              const was = before.stops.find(s => s.crs === stop.crs)
              if (was && !was.passed && stop.passed) {
                fresh.push({
                  id: `${uid}-${stop.crs}-${Date.now()}`,
                  headcode: train.headcode || uid,
                  text: `Reported at ${stop.name}`,
                })
              }
            }
          }
        } catch {
          // leave this journey as-is on failure
        }
      }

      if (cancelled) {
        return
      }
      previous.current = next
      setJourneys(next)
      if (fresh.length > 0) {
        setNotifications(current => [...current, ...fresh])
      }
    }

    load()
    const id = setInterval(load, intervalMs)
    return () => {
      cancelled = true
      clearInterval(id)
    }
  }, [pinnedUids.join(','), intervalMs])

  return { pinnedUids, togglePin, journeys, notifications, dismiss }
}