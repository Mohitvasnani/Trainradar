export default function SearchBox({ value, onChange }) {
  return (
    <div className="search-wrap">
      <input
        className="search-input"
        type="text"
        placeholder="Search service, station or operator"
        value={value}
        onChange={e => onChange(e.target.value)}
      />
      {value && (
        <button className="search-clear" onClick={() => onChange('')} aria-label="Clear search">
          ×
        </button>
      )}
    </div>
  )
}