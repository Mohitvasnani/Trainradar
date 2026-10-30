import { useState, useEffect } from 'react'
import { API_BASE } from '../api/base'
export function useLeg(train) {
  const [coords, setCoords] = useState(null)

  useEffect(function () {
    if (!train) {
      setCoords(null)
      return
    }

    const fromStation = train.legFromCrs
    const toStation = train.legToCrs

    if (!fromStation || !toStation) {
      setCoords(null)
      return
    }

    let isCancelled = false

       const url = API_BASE + '/api/leg/' + fromStation + '/' + toStation

    fetch(url)
      .then(function (response) {
        if (response.ok) {
          return response.json()
        } else {
          throw new Error('Failed to fetch leg')
        }
      })
      .then(function (data) {
        if (!isCancelled) {
          setCoords(data.coordinates)
        }
      })
      .catch(function () {
        if (!isCancelled) {
          setCoords(null)
        }
      })

    return function cleanup() {
      isCancelled = true
    }
  }, [train?.legFromCrs, train?.legToCrs])

  return coords
}