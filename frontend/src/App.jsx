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
        <Sidebar trains={trains} selectedUid={selectedUid} onSelect={setSelectedUid} />
        <MapView trains={trains} theme={theme} selectedUid={selectedUid} onSelect={setSelectedUid} />
      </div>
    </div>
  )
}