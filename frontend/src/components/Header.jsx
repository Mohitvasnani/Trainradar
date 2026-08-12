export default function Header({ theme, onToggleTheme, updatedAt, error, stale }) {
  let statusDef = 'loading...'
  let statusLevel = 'status'

  if (error) {
    statusDef =`Error: ${error}`
    statusLevel='status status-error'
  } else if (stale) {
    statusDef =`showing last known positions`
    statusLevel='status status-stale'
  } else if (updatedAt) {
    statusDef =`live --- updated ${updatedAt.toLocaleTimeString()}`
    
  }
  return (
    <header className="header">
      <span className="brand">TrainRadar</span>
      <span className={statusLevel}>{statusDef}</span>
      <button className="theme-btn" onClick={onToggleTheme}>
        {theme === 'dark' ? 'Light' : 'Dark'}
      </button>
    </header>
  )
}