import type { Alert } from '../types';

interface Props { alerts: Alert[]; }

export default function AlertList({ alerts }: Props) {
  if (!alerts.length) return <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>No alerts.</p>;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {alerts.map(a => (
        <div key={a.alertId} className="card" style={{
          borderLeft: `4px solid ${a.priority === 'CRITICAL' ? 'var(--danger)' : a.priority === 'URGENT' ? 'var(--warning)' : 'var(--info)'}`,
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: 700 }}>{a.title}</span>
            <span className={`badge badge-${a.priority.toLowerCase()}`}>{a.priority}</span>
          </div>
          <p style={{ fontSize: 14, color: 'var(--text-secondary)', margin: '6px 0' }}>{a.description}</p>
          {a.recommendedAction && (
            <div style={{ fontSize: 13, padding: '8px 12px', background: '#f0fdf4', borderRadius: 6, color: '#15803d' }}>
              <strong>Action:</strong> {a.recommendedAction}
            </div>
          )}
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 8 }}>
            {a.createdAt} · <span className={`badge badge-${a.status.toLowerCase()}`}>{a.status}</span>
          </div>
        </div>
      ))}
    </div>
  );
}