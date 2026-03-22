import { useState } from 'react';
import { aiApi } from '../services/api';
import type { OnboardingResult } from '../types';
import RiskBadge from './RiskBadge';

interface Props { patientId: string; }

export default function OnboardingPanel({ patientId }: Props) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OnboardingResult | null>(null);
  const [error, setError] = useState('');

  const run = async () => {
    setLoading(true); setError(''); setResult(null);
    try {
      const data = await aiApi.onboardPatient(patientId);
      setResult(data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message || 'Failed');
    } finally { setLoading(false); }
  };

  return (
    <div className="card" style={{ borderLeft: '4px solid var(--primary)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <h3 style={{ fontSize: 16, margin: 0 }}>🤖 AI Onboarding Agent</h3>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '4px 0 0' }}>
            LangGraph 6-node workflow: demographics → labs → meds → guidelines → risk → route
          </p>
        </div>
        <button className="btn btn-primary" onClick={run} disabled={loading}>
          {loading ? <><span className="spinner" /> Running...</> : 'Run Onboarding'}
        </button>
      </div>

      {error && <div style={{ padding: 12, background: '#fef2f2', borderRadius: 8, color: 'var(--danger)', fontSize: 14 }}>{error}</div>}

      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
            <RiskBadge score={result.result.risk_score} level={result.result.risk_level} />
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Processed in {result.processing_time_ms}ms
            </span>
            {result.result.alert_created && <span className="badge badge-critical">Alert Created</span>}
          </div>

          <div style={{ fontSize: 14, lineHeight: 1.7 }}>{result.result.summary}</div>

          <div>
            <h4 style={{ fontSize: 13, fontWeight: 700, color: 'var(--primary)', marginBottom: 6 }}>Key Findings</h4>
            {result.result.key_findings.map((f, i) => (
              <div key={i} style={{ fontSize: 14, padding: '4px 0', display: 'flex', gap: 8 }}>
                <span style={{ color: 'var(--danger)' }}>⚠</span> {f}
              </div>
            ))}
          </div>

          <div>
            <h4 style={{ fontSize: 13, fontWeight: 700, color: 'var(--primary)', marginBottom: 6 }}>Recommendations</h4>
            {result.result.recommendations.map((r, i) => (
              <div key={i} style={{ fontSize: 14, padding: '4px 0', display: 'flex', gap: 8 }}>
                <span style={{ color: 'var(--success)' }}>→</span> {r}
              </div>
            ))}
          </div>

          <div>
            <h4 style={{ fontSize: 13, fontWeight: 700, color: 'var(--primary)', marginBottom: 6 }}>Next Steps</h4>
            {result.result.next_steps.map((s, i) => (
              <div key={i} style={{ fontSize: 14, padding: '4px 0' }}>{i + 1}. {s}</div>
            ))}
          </div>

          {result.errors.length > 0 && (
            <div style={{ padding: 12, background: '#fffbeb', borderRadius: 8, fontSize: 13, color: '#92400e' }}>
              <strong>Data gaps:</strong> {result.errors.join('; ')}
            </div>
          )}
        </div>
      )}
    </div>
  );
}