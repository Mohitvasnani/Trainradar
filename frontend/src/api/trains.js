const BASE = 'http://127.0.0.1:5000'

export async function fetchTrains() {
  const res = await fetch(`${BASE}/api/trains`)
  if (!res.ok) throw new Error(`${res.status}`)
  return res.json()}