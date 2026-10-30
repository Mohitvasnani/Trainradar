import { useState, useEffect } from 'react'
import { API_BASE } from '../api/base'

export function useJourney(train) {
  const [journey, setJourney] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(function() {
    
    if (!train) {
      setJourney(null)
      setLoading(false)
      return
    }

    
    const uid = train.uid
    const runDate = train.runDate
    
    
    if (!uid || !runDate) {
      setJourney(null)
      setLoading(false)
      return
    }

    let isCancelled = false
    
    
    setLoading(true)


       const url = API_BASE + '/api/journey/' + uid + '/' + runDate

    
    fetch(url)
      .then(function(response) {
        
        if (response.ok) {
          return response.json()
        } else {
          throw new Error('Failed to fetch journey')
        }
      })
      .then(function(data) {
        
        if (!isCancelled) {
          setJourney(data)
        }
      })
      .catch(function(error) {
       
        if (!isCancelled) {
          setJourney(null)
        }
      })
      .finally(function() {        
        if (!isCancelled) {
          setLoading(false)
        }
      })

    
    return function cleanup() {
      isCancelled = true
    }
  }, [train?.uid, train?.runDate])

  return { journey, loading }
}