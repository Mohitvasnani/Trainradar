import { useState } from 'react'
import { useTrains } from './hooks/useTrains'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import MapView from './components/MapView'
import './theme.css'
import './App.css'

export default function App() {
  const [theme, setTheme] = useState('dark')
  const [selectedUid, setSelectedUid] = useState(null)
  const { trains, updatedAt, error, stale } = useTrains()
  const  [query, setQuery]=useState('')
  const q=query.trim().toLowerCase()
  let filtered
  if (!q) {
    filtered = trains
  } else {
    filtered=trains.filter(
      t=>[t.headcode,
        t.operator,
        t.origin,
        t.destination,
        t.legFrom,
        t.legTo,
        t.uid].some(field=>
        (field||'').toLowerCase().includes(q)
        )
    )
  }

  return (
    <div className="app" data-theme={theme}>
      <Header
        theme={theme}
        onToggleTheme={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        updatedAt={updatedAt}
        stale={stale}
        error={error}
      />
      <div className="body">
        <Sidebar trains={filtered} selectedUid={selectedUid} onSelect={setSelectedUid}
          query={query} onQueryChange={setQuery} />
        <MapView trains={filtered} theme={theme} selectedUid={selectedUid} onSelect={setSelectedUid} />
      </div>
    </div>
  )
}