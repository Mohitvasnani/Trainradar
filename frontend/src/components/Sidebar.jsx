import ServiceRow from './ServiceRow'

export default function Sidebar({ trains, selectedUid, onSelect }) {
  return (
    <aside className="sidebar">
      <h2 className="sidebar-title">Active services</h2>
      <div className="sidebar-list">
        {trains.length === 0 && <p className="empty">No live services</p>}
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