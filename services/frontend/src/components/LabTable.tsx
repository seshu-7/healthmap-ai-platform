import type { LabResult } from '../types';

interface Props { labs: LabResult[]; }

export default function LabTable({ labs }: Props) {
  if (!labs.length) return <p style={{ color: 'var(--text-secondary)', fontSize: 14 }}>No lab results found.</p>;
  return (
    <table className="table">
      <thead>
        <tr>
          <th>Test</th><th>Value</th><th>Ref Range</th><th>Status</th><th>Date</th>
        </tr>
      </thead>
      <tbody>
        {labs.map(lab => (
          <tr key={lab.labId}>
            <td style={{ fontWeight: 600 }}>{lab.testName}</td>
            <td>{lab.value} {lab.unit}</td>
            <td style={{ color: 'var(--text-secondary)' }}>{lab.referenceRange}</td>
            <td>
              {lab.isAbnormal
                ? <span className="badge badge-high">Abnormal</span>
                : <span className="badge badge-low">Normal</span>}
            </td>
            <td style={{ color: 'var(--text-secondary)' }}>{lab.collectedDate}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}