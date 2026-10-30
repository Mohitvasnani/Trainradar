import '../css/Switcher.css'

export default function Switcher({ layer, onChange, layers }) {
  return (
    <div className="layer-switcher">
      {Object.keys(layers).map(function(key) {
        let buttonClass   = 'layer-btn'
        if (key===layer){
          buttonClass += ' isactive'}
        
        return (
          <button 
            key={key} 
            className={buttonClass}
            onClick={function() {
              onChange(key)
            }}
          >
            {layers[key].label}
          </button>
        )
      })}
    </div>
  )
}