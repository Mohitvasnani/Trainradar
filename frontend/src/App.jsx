import { useState } from 'react'
import { useTrains } from './hooks/useTrains'

import Header from './components/Header'
import Sidebar from './components/Sidebar'
import MapView from './components/MapView'
import { usePin } from './hooks/usePin'
import PinPanel from './components/PinPanel'
import Notify from './components/Notify'
import './theme.css'
import './App.css'

export default function App() {
  const [theme, setTheme] = useState('dark')
  const [selectedUid, setSelectedUid] = useState(null)
  const [search, setSearch] = useState({ from: '', to: '', text: '' })

  const { trains, updatedAt, error, stale } = useTrains()
  const { pinnedUids, togglePin, journeys, notifications, dismiss } = usePin(trains)

  function matches(train) {
    const from = search.from.trim().toLowerCase()
    const to = search.to.trim().toLowerCase()
    const text = search.text.trim().toLowerCase()

    if (from && !(train.origin || '').toLowerCase().includes(from)) {
      return false
    }
    if (to && !(train.destination || '').toLowerCase().includes(to)) {
      return false
    }
    if (text) {
      const fields = [train.headcode, train.operator, train.uid]
      let found = false
      for (const f of fields) {
        if (f && f.toLowerCase().includes(text)) {
          found = true
        }
      }
      if (!found) {
        return false
      }
    }
    return true
  }

  const filtered = trains.filter(matches)

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
        <Sidebar
          trains={filtered}
          selectedUid={selectedUid}
          onSelect={setSelectedUid}
          search={search}
          onSearchChange={setSearch}
          pinnedUids={pinnedUids}
          onTogglePin={togglePin}
        />
        <MapView
          trains={trains}
          theme={theme}
          selectedUid={selectedUid}
          onSelect={setSelectedUid}
          pinnedJourneys={journeys}
        />
      </div>

      <PinPanel
        trains={trains}
        pinnedUids={pinnedUids}
        journeys={journeys}
        onUnpin={togglePin}
        onSelect={setSelectedUid}
      />
      <Notify items={notifications} onDismiss={dismiss} />
    </div>
  )
}