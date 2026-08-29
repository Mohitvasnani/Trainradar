import '../css/Traininfo.css'

export default function TrainInfo({ train, journey, loading, onClose }) {
  if (!train) return null

  const late = train.latenessMinutes
  
  let nextStop = null
  if (journey && journey.stops) {
    for (let i = 0; i < journey.stops.length; i++) {
      if (!journey.stops[i].passed) {
        nextStop = journey.stops[i]
        break
      }
    }
  }

  let statusText
  let statusClass
  
  if (late == null) {
    statusText = 'No live report'
    statusClass = 'muted'
  } else if (late > 0) {
    statusText = late + ' min late'
    statusClass = 'late'
  } else if (late < 0) {
    statusText = Math.abs(late) + ' min early'
    statusClass = 'ontime'
  } else {
    statusText = 'On time'
    statusClass = 'ontime'
  }

  return (
    <div className="train-info">
      <button className="info-close" onClick={onClose} aria-label="Close">×</button>

      <div className="info-head">
        <span className="info-headcode">{train.headcode || train.uid}</span>
        {train.isEstimate && <span className="info-est">est.</span>}
      </div>

      <div className="info-route">
        {loading && <div className="info-loading">Loading route…</div>}
        {train.origin} → {train.destination}
      </div>
      
      <div className="info-operator">{train.operator}</div>

      <div className="info-status">
        <span className={statusClass}>{statusText}</span>
      </div>

      <div className="info-position">
        Estimated between <strong>{train.legFrom}</strong> and <strong>{train.legTo}</strong>
      </div>

      {nextStop && (
        <div className="info-next">
          Next stop {nextStop.name}
          {nextStop.schedArr && ' · due ' + new Date(nextStop.schedArr)
            .toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      )}

      <div className="info-footnote">Position estimated from schedule data</div>
    </div>
  )
}