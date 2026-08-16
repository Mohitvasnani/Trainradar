import '../css/Pinpanel.css'

export default function PinPanel({ trains, pinnedUids, journeys, onUnpin, onSelect }) {
  if (pinnedUids.length === 0) {
    return null
  }

  return (
    <div className="pinned-panel">
      <div className="pinned-title">Watching</div>
      {pinnedUids.map(uid => {
        const train = trains.find(t => t.uid === uid)
        if (!train) {
          return null
        }
        const journey = journeys[uid]
        let nextStop = null
        if (journey) {
          nextStop = journey.stops.find(s => !s.passed)
        }

        return (
          <div className="pinned-row" key={uid}>
            <button className="pinned-main" onClick={() => onSelect(uid)}>
              <div className="pinned-head">{train.headcode || uid}</div>
              <div className="pinned-route">{train.origin} → {train.destination}</div>
              {nextStop && <div className="pinned-next">Next {nextStop.name}</div>}
            </button>
            <button className="pinned-remove" onClick={() => onUnpin(uid)} aria-label="Unpin">×</button>
          </div>
        )
      })}
    </div>
  )
}