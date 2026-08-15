import ServiceRow from './ServiceRow'
import SearchBox from './SearchBox'

export default function Sidebar({ trains, selectedUid, onSelect, query, onQueryChange }) {
  return (
    <aside className="sidebar">
      <h2 className="sidebar-title">Active services</h2>
       <SearchBox value={query} onChange={onQueryChange} />
      <div className="sidebar-list">
        {trains.length === 0 && <p className="empty">{query ? 'No matching services' : 'No live services'}</p>}
        {trains.map(t => (
          <ServiceRow
            key={t.uid}
            train={t}
            selected={t.uid === selectedUid}
            onSelect={onSelect}
          />
        ))}
      </div>
    </aside>
  )
}