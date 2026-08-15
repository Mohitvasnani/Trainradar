export default function Switcher({layer, onChange, layers}) {
    return(
        <div className="layer_switcher">
            {Object.keys(layers).map(
                key=>(
                    <button key={key} className={`layer-btn ${key===layer?'isactive':''}`}
                    onClick={
                        ()=>onChange(key)
                    }>{
                        layers[key].label
                    }</button>
                )
            )
            }
        </div>
    )
}