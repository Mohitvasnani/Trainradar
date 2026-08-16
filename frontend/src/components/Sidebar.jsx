import ServiceRow from './ServiceRow'
import SearchBox from './SearchBox'

export default function Sidebar({ trains, selectedUid, onSelect, search, onSearchChange, onTogglePin, pinnedUids }) {
  const hasSearch = search.from || search.to || search.text

  return (
    <aside className="sidebar">
      <h2 className="sidebar-title">Active services</h2>
      <SearchBox
        from={search.from}
        to={search.to}
        text={search.text}
        onChange={onSearchChange}
      />
      <div className="sidebar-list">
        {trains.length === 0 && (
          <p className="empty">{hasSearch ? 'No matching services' : 'No live services'}</p>
        )}
        {trains.map(t => (
          <ServiceRow
            key={t.uid}
            train={t}
            selected={t.uid === selectedUid}
            onSelect={onSelect}
            pinned={pinnedUids.includes(t.uid)}
            onTogglePin={onTogglePin}
          />
        ))}
      </div>
    </aside>
  )
}