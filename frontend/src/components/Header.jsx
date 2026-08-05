export default function Header({ theme, onToggleTheme, updatedAt, error }) {
  return (
    <header className="header">
      <span className="brand">TrainRadar</span>
      <span className={`status ${error ? 'status-error' : ''}`}>
        {error ? `Error: ${error}` : updatedAt ? `Live · updated ${updatedAt.toLocaleTimeString()}` : 'Loading…'}
      </span>
      <button className="theme-btn" onClick={onToggleTheme}>
        {theme === 'dark' ? 'Light' : 'Dark'}
      </button>
    </header>
  )
}