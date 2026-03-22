import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { patientApi, labApi, medApi, alertApi } from '../services/api';
import type { Patient, LabResult, Medication, Alert } from '../types';
import LabTable from '../components/LabTable';
import MedTable from '../components/MedTable';
import AlertList from '../components/AlertList';
import OnboardingPanel from '../components/OnboardingPanel';

export default function PatientDetail() {
  const { id } = useParams<{ id: string }>();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [labs, setLabs] = useState<LabResult[]>([]);
  const [meds, setMeds] = useState<Medication[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [tab, setTab] = useState<'overview' | 'ai'>('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    Promise.all([
      patientApi.getById(id).catch(() => null),
      labApi.getByPatient(id).catch(() => []),
      medApi.getByPatient(id).catch(() => []),
      alertApi.getByPatient(id).catch(() => []),
    ]).then(([p, l, m, a]) => {
      setPatient(p); setLabs(l); setMeds(m); setAlerts(a); setLoading(false);
    });
  }, [id]);

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: 60 }}><span className="spinner" /></div>;
  if (!patient) return <div className="card"><p>Patient not found. Is patient-service running?</p><Link to="/">← Back</Link></div>;

  return (
    <div>
      <Link to="/" style={{ fontSize: 14, color: 'var(--text-secondary)' }}>← Back to Dashboard</Link>

      <div className="card" style={{ marginTop: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0 }}>{patient.firstName} {patient.lastName}</h1>
            <div style={{ display: 'flex', gap: 16, marginTop: 6, fontSize: 14, color: 'var(--text-secondary)' }}>
              <span>ID: {patient.patientId}</span>
              <span>DOB: {patient.dateOfBirth}</span>
              <span>{patient.gender}</span>
              <span>{patient.insurancePlan}</span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 6 }}>
            {patient.conditions.map(c => <span key={c} className="badge badge-moderate">{c}</span>)}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 4, marginTop: 16, marginBottom: 16 }}>
        {(['overview', 'ai'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)} className={`btn ${tab === t ? 'btn-primary' : 'btn-outline'}`}>
            {t === 'overview' ? '📋 Clinical Data' : '🤖 AI Agents'}
          </button>
        ))}
      </div>

      {tab === 'overview' ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div className="card">
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>Lab Results ({labs.length})</h3>
            <LabTable labs={labs} />
          </div>
          <div className="card">
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>Active Medications ({meds.length})</h3>
            <MedTable medications={meds} />
          </div>
          <div className="card">
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>Alerts</h3>
            <AlertList alerts={alerts} />
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <OnboardingPanel patientId={patient.patientId} />
        </div>
      )}
    </div>
  );
}