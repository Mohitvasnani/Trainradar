import '../css/Notify.css'

export default function Notify({ items, onDismiss }) {
  if (items.length === 0) {
    return null
  }

  return (
    <div className="toasts">
      {items.map(n => (
        <div className="toast" key={n.id}>
          <div className="toast-head">{n.headcode}</div>
          <div className="toast-text">{n.text}</div>
          <button className="toast-close" onClick={() => onDismiss(n.id)}>×</button>
        </div>
      ))}
    </div>
  )
}