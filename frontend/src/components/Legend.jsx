export default function Legend() {
  return (
    <div className="legend">
      <div className="legend-row">
        <span className="legend-dot" style={{ background: '#4da3ff' }} />
        Selected train
      </div>
      <div className="legend-row">
        <span className="legend-dot" style={{ background: '#9a9aa0' }} />
        Other trains
      </div>
      <div className="legend-row">
        <span className="legend-dot" style={{ background: '#e0a030' }} />
        Pinned route
      </div>
      <div className="legend-row">
        <span className="legend-line" style={{ background: '#4caf7d' }} />
        Track travelled
      </div>
      <div className="legend-row">
        <span className="legend-line legend-dashed" />
        Track ahead
      </div>
      <div className="legend-row">
        <span className="legend-dot legend-hollow" style={{ borderColor: '#b3372a' }} />
        Stop not served
      </div>
      <div className="legend-note">Positions are estimated from schedule data</div>
    </div>
  )
}