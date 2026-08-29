import { useState, useEffect, useRef } from 'react'

const MAX_PINNED = 2

export function usePin(trains, intervalMs = 60000) {
  const [pinnedUids, setPinnedUids] = useState([])
  const [journeys, setJourneys] = useState({})
  const [notifications, setNotifications] = useState([])
  const previousJourneys = useRef({})

  
  function togglePin(uid) {
    setPinnedUids(function(currentPins) {
      
      if (currentPins.includes(uid)) {
        return currentPins.filter(function(pinnedUid) {
          return pinnedUid !== uid
        })
      }
      
   
      if (currentPins.length >= MAX_PINNED) {
        return [currentPins[1], uid]
      }
      
      
      return [...currentPins, uid]
    })
  }

  // Remove a notification
  function dismiss(notificationId) {
    setNotifications(function(currentNotifications) {
      return currentNotifications.filter(function(notification) {
        return notification.id !== notificationId
      })
    })
  }

  useEffect(function() {
    
    if (pinnedUids.length === 0) {
      setJourneys({})
      previousJourneys.current = {}
      return
    }

    let isCancelled = false

    
    async function loadJourneys() {
      const newJourneys = {}
      const newNotifications = []

      for (let i = 0; i < pinnedUids.length; i++) {
        const uid = pinnedUids[i]
        
        
        const train = trains.find(function(t) {
          return t.uid === uid
        })
        
        
        if (!train || !train.runDate) {
          continue
        }
        
        try {
          const response = await fetch(
            'http://127.0.0.1:5000/api/journey/' + uid + '/' + train.runDate
          )
          
          if (!response.ok) {
            continue
          }
          
          const journeyData = await response.json()
          newJourneys[uid] = journeyData
          
          
          const oldJourney = previousJourneys.current[uid]
          if (oldJourney) {
            for (let j = 0; j < journeyData.stops.length; j++) {
              const stop = journeyData.stops[j]
              
             
              const oldStop = oldJourney.stops.find(function(s) {
                return s.crs === stop.crs
              })
              
    
              if (oldStop && !oldStop.passed && stop.passed) {
                newNotifications.push({
                  id: uid + '-' + stop.crs + '-' + Date.now(),
                  headcode: train.headcode || uid,
                  text: 'Reported at ' + stop.name,
                })
              }
            }
          }
        } catch (error) {
          // skip
        }
      }

      if (isCancelled) {
        return
      }
      
      previousJourneys.current = newJourneys
      setJourneys(newJourneys)
      
      if (newNotifications.length > 0) {
        setNotifications(function(currentNotifications) {
          return currentNotifications.concat(newNotifications)
        })
      }
    }

    
    loadJourneys()
    const intervalId = setInterval(loadJourneys, intervalMs)
    
    
    return function cleanup() {
      isCancelled = true
      clearInterval(intervalId)
    }
  }, [pinnedUids.join(','), intervalMs])

  return { 
    pinnedUids, 
    togglePin, 
    journeys, 
    notifications, 
    dismiss 
  }
}