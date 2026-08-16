import '../css/Servicerow.css'
export default function ServiceRow({ train, selected, onSelect, pinned, onTogglePin }) {
    const late = train.latenessMinutes
    const isLiveTrain = train.lat != null
    const nextTrain = train.legTo && train.legTo !== train.destination

    return (
        <div
            className={`service-row ${selected ? 'is-selected' : ''} ${isLiveTrain ? '' : 'is-stale'}`}
            onClick={() => onSelect(train.uid)}
            role="button"
            tabIndex={0}
        >
            <div className="row-top">
                <span className="headcode">{train.headcode || train.uid}</span>
                <span className="row-right">
                    {!isLiveTrain
                        ? <span className="muted">no live data</span>
                        : late > 0
                            ? <span className="late">+{late} min</span>
                            : late < 0
                                ? <span className="ontime">{late} min early</span>
                                : <span className="ontime">on time</span>}
                    <button
                        className={`pin-btn ${pinned ? 'is-pinned' : ''}`}
                        onClick={e => { e.stopPropagation(); onTogglePin(train.uid) }}
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
                {nextTrain && ` → next ${train.legTo}`}
            </div>
        </div>
    )
}