import { useState } from 'react';
import { Bar, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend } from 'chart.js';
import { evalApi } from '../services/api';
import type { EvalReport } from '../types';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend);

export default function EvalDashboard() {
  const [report, setReport] = useState<EvalReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const run = async () => {
    setLoading(true); setError('');
    try { setReport(await evalApi.run(0.0)); }
    catch (e: any) {
      // 422 means threshold failed but we still get the report
      if (e?.response?.status === 422) setReport(e.response.data);
      else setError(e.message);
    }
    finally { setLoading(false); }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700 }}>✅ AI Eval Dashboard</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginTop: 4 }}>
            Automated quality testing for AI agent outputs
          </p>
        </div>
        <button className="btn btn-primary" onClick={run} disabled={loading}>
          {loading ? <><span className="spinner" /> Running Evals...</> : 'Run Eval Suite'}
        </button>
      </div>

      {error && <div className="card" style={{ borderLeft: '4px solid var(--danger)', color: 'var(--danger)' }}>{error}</div>}

      {report && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Summary cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
            {[
              { label: 'Pass Rate', value: `${(report.summary.passRate * 100).toFixed(0)}%`, color: report.summary.passRate >= 0.8 ? 'var(--success)' : 'var(--danger)' },
              { label: 'Avg Correctness', value: `${(report.scores.avgCorrectness * 100).toFixed(0)}%`, color: 'var(--info)' },
              { label: 'Avg Completeness', value: `${(report.scores.avgCompleteness * 100).toFixed(0)}%`, color: 'var(--primary)' },
              { label: 'Hallucinations', value: `${report.scores.hallucinationCount}`, color: report.scores.hallucinationCount === 0 ? 'var(--success)' : 'var(--danger)' },
            ].map(card => (
              <div key={card.label} className="card" style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 32, fontWeight: 700, color: card.color }}>{card.value}</div>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4 }}>{card.label}</div>
              </div>
            ))}
          </div>

          {/* Charts */}
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16 }}>
            <div className="card">
              <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Per-Scenario Scores</h3>
              <Bar data={{
                labels: report.results.map(r => r.scenarioId),
                datasets: [
                  { label: 'Correctness', data: report.results.map(r => r.correctness), backgroundColor: '#3b82f6' },
                  { label: 'Completeness', data: report.results.map(r => r.completeness), backgroundColor: '#14b8a6' },
                ],
              }} options={{ scales: { y: { min: 0, max: 1 } } }} />
            </div>
            <div className="card">
              <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Pass / Fail</h3>
              <Doughnut data={{
                labels: ['Passed', 'Failed'],
                datasets: [{ data: [report.summary.passed, report.summary.failed], backgroundColor: ['#10b981', '#dc2626'] }],
              }} />
            </div>
          </div>

          {/* Results table */}
          <div className="card">
            <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Scenario Results</h3>
            <table className="table">
              <thead><tr><th>Scenario</th><th>Status</th><th>Correctness</th><th>Completeness</th><th>Hallucination</th><th>Format</th></tr></thead>
              <tbody>
                {report.results.map(r => (
                  <tr key={r.scenarioId}>
                    <td style={{ fontWeight: 600 }}>{r.scenarioId}</td>
                    <td>{r.passed ? <span className="badge badge-low">PASS</span> : <span className="badge badge-high">FAIL</span>}</td>
                    <td>{(r.correctness * 100).toFixed(0)}%</td>
                    <td>{(r.completeness * 100).toFixed(0)}%</td>
                    <td>{r.hallucination ? <span className="badge badge-high">YES</span> : <span className="badge badge-low">No</span>}</td>
                    <td>{r.formatValid ? '✅' : '❌'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}