import { API_BASE } from './base'

export async function fetchTrains() {
  const res = await fetch(`${API_BASE}/api/trains`)
  if (!res.ok) throw new Error(`${res.status}`)
  return res.json()}