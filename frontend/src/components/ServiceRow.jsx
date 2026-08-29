import '../css/Servicerow.css'

export default function ServiceRow({ train, selected, onSelect, pinned, onTogglePin }) {
  const late = train.latenessMinutes
  const isLiveTrain = train.lat != null
  
  
  let hasNextStation = false
  if (train.legTo && train.legTo !== train.destination) {
    hasNextStation = true
  }

  
  let statusText
  let statusClass
  
  if (!isLiveTrain) {
    statusText = 'no live data'
    statusClass = 'muted'
  } else if (late > 0) {
    statusText = '+' + late + ' min'
    statusClass = 'late'
  } else if (late < 0) {
    statusText = late + ' min early'
    statusClass = 'ontime'
  } else {
    statusText = 'on time'
    statusClass = 'ontime'
  }

  // Build class names
  let rowClass = 'service-row'
  if (selected) {
    rowClass += ' is-selected'
  }
  if (!isLiveTrain) {
    rowClass += ' is-stale'
  }

  return (
    <div
      className={rowClass}
      onClick={() => onSelect(train.uid)}
      role="button"
      tabIndex={0}
    >
      <div className="row-top">
        <span className="headcode">{train.headcode || train.uid}</span>
        <span className="row-right">
          <span className={statusClass}>{statusText}</span>
          <button
            className={pinned ? 'pin-btn is-pinned' : 'pin-btn'}
            onClick={function(e) {
              e.stopPropagation()
              onTogglePin(train.uid)
            }}
            aria-label={pinned ? 'Unpin train' : 'Pin train'}
          >
            ★
          </button>
        </span>
      </div>

      <div className="row-route">
        {train.origin} → {train.destination}
      </div>

      <div className="row-sub">
        {train.operator}
        {hasNextStation && ' → next ' + train.legTo}
      </div>
    </div>
  )
}