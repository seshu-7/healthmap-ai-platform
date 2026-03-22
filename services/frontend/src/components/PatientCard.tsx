import { Link } from 'react-router-dom';
import type { Patient } from '../types';

interface Props { patient: Patient; }

export default function PatientCard({ patient }: Props) {
  return (
    <Link to={`/patients/${patient.patientId}`} style={{ textDecoration: 'none', color: 'inherit' }}>
      <div className="card" style={{ cursor: 'pointer', transition: 'box-shadow 0.15s' }}
        onMouseEnter={e => (e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)')}
        onMouseLeave={e => (e.currentTarget.style.boxShadow = 'var(--shadow)')}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16 }}>{patient.firstName} {patient.lastName}</div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 2 }}>ID: {patient.patientId}</div>
          </div>
          <span className="badge badge-moderate">{patient.primaryCondition}</span>
        </div>
        <div style={{ display: 'flex', gap: 16, marginTop: 12, fontSize: 13, color: 'var(--text-secondary)' }}>
          <span>DOB: {patient.dateOfBirth}</span>
          <span>{patient.gender}</span>
          <span>{patient.insurancePlan}</span>
        </div>
        <div style={{ display: 'flex', gap: 6, marginTop: 8, flexWrap: 'wrap' }}>
          {patient.conditions.map(c => (
            <span key={c} style={{ fontSize: 11, padding: '2px 8px', borderRadius: 4, background: '#f3f4f6', color: '#374151' }}>{c}</span>
          ))}
        </div>
      </div>
    </Link>
  );
}