import { useState, useEffect } from 'react';
import { alertApi } from '../services/api';
import type { Alert } from '../types';
import AlertList from '../components/AlertList';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    alertApi.getOpen().then(setAlerts).catch(() => setAlerts([])).finally(() => setLoading(false));
  }, []);

  const critical = alerts.filter(a => a.priority === 'CRITICAL');
  const urgent = alerts.filter(a => a.priority === 'URGENT');
  const routine = alerts.filter(a => a.priority === 'ROUTINE');

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>🔔 Open Alerts</h1>
      <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginBottom: 20 }}>
        {alerts.length} open alerts · {critical.length} critical · {urgent.length} urgent
      </p>

      {loading ? <div className="spinner" /> : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {critical.length > 0 && <div><h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--danger)', marginBottom: 10 }}>🔴 Critical</h2><AlertList alerts={critical} /></div>}
          {urgent.length > 0 && <div><h2 style={{ fontSize: 16, fontWeight: 700, color: '#b45309', marginBottom: 10 }}>🟡 Urgent</h2><AlertList alerts={urgent} /></div>}
          {routine.length > 0 && <div><h2 style={{ fontSize: 16, fontWeight: 700, color: 'var(--info)', marginBottom: 10 }}>🔵 Routine</h2><AlertList alerts={routine} /></div>}
          {alerts.length === 0 && <p style={{ textAlign: 'center', color: 'var(--text-secondary)', padding: 40 }}>No open alerts. All clear!</p>}
        </div>
      )}
    </div>
  );
}