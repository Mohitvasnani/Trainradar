export default function SearchBox({ from, to, text, onChange }) {
  const hasAny = from || to || text

  return (
    <div className="search-panel">
      <input
        className="search-input"
        placeholder="From"
        value={from}
        onChange={e => onChange({ from: e.target.value, to, text })}
      />
      <input
        className="search-input"
        placeholder="To"
        value={to}
        onChange={e => onChange({ from, to: e.target.value, text })}
      />
      <input
        className="search-input"
        placeholder="Headcode or operator"
        value={text}
        onChange={e => onChange({ from, to, text: e.target.value })}
      />
      {hasAny && (
        <button
          className="search-clear-all"
          onClick={() => onChange({ from: '', to: '', text: '' })}
        >
          Clear filters
        </button>
      )}
    </div>
  )
}