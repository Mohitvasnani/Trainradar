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
  // State for theme, selected train, and search filters
  const [theme, setTheme] = useState('dark')
  const [selectedUid, setSelectedUid] = useState(null)
  const [search, setSearch] = useState({ from: '', to: '', text: '' })

  
  const trainsData = useTrains()
  const trains = trainsData.trains
  const updatedAt = trainsData.updatedAt
  const error = trainsData.error
  const stale = trainsData.stale

  
  const pinData = usePin(trains)
  const pinnedUids = pinData.pinnedUids
  const journeys = pinData.journeys
  const notifications = pinData.notifications

  
  const filtered = trains.filter(function(train) {
    
    const fromSearch = search.from.toLowerCase()
    const toSearch = search.to.toLowerCase()
    const textSearch = search.text.toLowerCase()

    
    if (fromSearch !== '') {
      const trainOrigin = train.origin ? train.origin.toLowerCase() : ''
      const trainCallingPoints = train.callingPoints || []
      
      let matchesFrom = trainOrigin.includes(fromSearch)
      
   
      if (!matchesFrom) {
        for (let i = 0; i < trainCallingPoints.length; i++) {
          if (trainCallingPoints[i].toLowerCase().includes(fromSearch)) {
            matchesFrom = true
            break
          }
        }
      }
      
    
      if (!matchesFrom) {
        return false
      }
    }

    
    if (toSearch !== '') {
      const trainDestination = train.destination ? train.destination.toLowerCase() : ''
      if (!trainDestination.includes(toSearch)) {
        return false
      }
    }

    
    if (textSearch !== '') {
      const trainHeadcode = train.headcode ? train.headcode.toLowerCase() : ''
      const trainOperator = train.operator ? train.operator.toLowerCase() : ''
      const trainUid = train.uid ? train.uid.toLowerCase() : ''
      
      const matchesText = trainHeadcode.includes(textSearch) || 
                         trainOperator.includes(textSearch) || 
                         trainUid.includes(textSearch)
      
      if (!matchesText) {
        return false
      }
    }    
    return true})

  
  function handleThemeToggle() {
    if (theme === 'dark') {
      setTheme('light')
    } else {
      setTheme('dark')
    }}

  return (
    <div className="app" data-theme={theme}>
      <Header
        theme={theme}
        onToggleTheme={handleThemeToggle}
        updatedAt={updatedAt}
        stale={stale}
        error={error}/> 
        
      <div className="body">
        <Sidebar
          trains={filtered}
          selectedUid={selectedUid}
          onSelect={setSelectedUid}
          search={search}
          onSearchChange={setSearch}
          pinnedUids={pinnedUids}
          onTogglePin={pinData.togglePin}
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
        onUnpin={pinData.togglePin}
        onSelect={setSelectedUid}
      />
      <Notify items={notifications} onDismiss={pinData.dismiss} />
    </div>
  )
}