import type { Medication } from '../types';

interface Props { medications: Medication[]; }

export default function MedTable({ medications }: Props) {
  if (!medications.length) return <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>No medications found.</p>;
  return (
    <table className="table">
      <thead>
        <tr><th>Drug</th><th>Dosage</th><th>Frequency</th><th>Prescriber</th><th>Since</th></tr>
      </thead>
      <tbody>
        {medications.map(m => (
          <tr key={m.medicationId}>
            <td style={{ fontWeight: 600 }}>{m.drugName}</td>
            <td>{m.dosage}</td>
            <td>{m.frequency}</td>
            <td style={{ color: 'var(--text-secondary)' }}>{m.prescriber}</td>
            <td style={{ color: 'var(--text-secondary)' }}>{m.startDate}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}