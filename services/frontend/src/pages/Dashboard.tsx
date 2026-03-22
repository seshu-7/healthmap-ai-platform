import { useState, useEffect } from 'react';
import { patientApi, alertApi } from '../services/api';
import type { Patient, Alert } from '../types';
import PatientCard from '../components/PatientCard';
import AlertList from '../components/AlertList';

export default function Dashboard() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      patientApi.search('').catch(() => []),
      alertApi.getOpen().catch(() => []),
    ]).then(([p, a]) => { setPatients(p); setAlerts(a); setLoading(false); });
  }, []);

  const filtered = search
    ? patients.filter(p =>
        `${p.firstName} ${p.lastName} ${p.primaryCondition}`.toLowerCase().includes(search.toLowerCase()))
    : patients;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700 }}>Care Dashboard</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 4 }}>
            {patients.length} patients · {alerts.length} open alerts
          </p>
        </div>
        <input
          placeholder="Search patients..."
          value={search} onChange={e => setSearch(e.target.value)}
          style={{ width: 280 }}
        />
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}><span className="spinner" /></div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 360px', gap: 24 }}>
          <div>
            <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>Patients</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: -4, marginBottom: 12 }}>
              Open a patient card and switch to the AI Agents tab to run onboarding.
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {filtered.map(p => <PatientCard key={p.patientId} patient={p} />)}
              {filtered.length === 0 && (
                <p style={{ color: 'var(--text-secondary)', fontSize: 14, padding: 20, textAlign: 'center' }}>
                  No patients found. The Spring Boot patient-service may not be running.
                </p>
              )}
            </div>
          </div>

          <div>
            <h2 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>🔔 Open Alerts</h2>
            <AlertList alerts={alerts} />
          </div>
        </div>
      )}
    </div>
  );
}