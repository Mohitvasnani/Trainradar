export default function ServiceRow ({train, selected, onSelect}) {


    const late =  train.latenessMinutes
    const isLiveTrain = train.lat  != null
    const nextTrain=train.legTo && train.legTo !==train.destination


    return(
        <button className={`service-row ${selected?'is-selected':''} ${isLiveTrain? '' : 'is-stale'}`} onClick={()=>onSelect(train.uid)}>
            
            <div className="service-route">
                <span className="headcode">{train.headcode || train.uid}                    
                </span>
                {'.'}
                {!isLiveTrain
                    ?<span className="muted">no live data</span> : late ? <span className="late">+{late} min</span> : <span className="ontime">on time</span>
                }
                </div>
              <div className="row-route">
                {train.origin} → {train.destination}
            </div>

            <div className="row-sub">
                {train.operator}
                {nextTrain && ` → next ${train.legTo}`}
            </div>

        </button>
    )
}