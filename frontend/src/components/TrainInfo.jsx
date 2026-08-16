import '../css/Traininfo.css'
export default function TrainInfo({ train, journey, onClose }) {
  if (!train) return null

  const late = train.latenessMinutes
  const nextStop = journey?.stops.find(s => !s.passed)

  return (
    <div className="train-info">
      <button className="info-close" onClick={onClose} aria-label="Close">×</button>

      <div className="info-head">
        <span className="info-headcode">{train.headcode || train.uid}</span>
        {train.isEstimate && <span className="info-est">est.</span>}
      </div>

      <div className="info-route">{train.origin} → {train.destination}</div>
      <div className="info-operator">{train.operator}</div>

      <div className="info-status">
        {late == null
          ? <span className="muted">No live report</span>
          : late > 0
            ? <span className="late">{late} min late</span>
            : late < 0
              ? <span className="ontime">{Math.abs(late)} min early</span>
              : <span className="ontime">On time</span>}
      </div>

      <div className="info-position">
        Estimated between <strong>{train.legFrom}</strong> and <strong>{train.legTo}</strong>
      </div>

      {nextStop && (
        <div className="info-next">
          Next stop {nextStop.name}
          {nextStop.schedArr && ` · due ${new Date(nextStop.schedArr)
            .toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`}
        </div>
      )}

      <div className="info-footnote">Position estimated from schedule data</div>
    </div>
  )
}