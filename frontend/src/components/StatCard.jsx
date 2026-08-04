export function StatCard({ icon, label, value, note, tone }) {
  return <div className="stat"><div className={`stat-icon ${tone}`}>{icon}</div><div><p>{label}</p><h3>{value}</h3><small>{note}</small></div></div>;
}
