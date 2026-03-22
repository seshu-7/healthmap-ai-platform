import { useState } from 'react';
import { aiApi } from '../services/api';
import type { OnboardingResult } from '../types';
import RiskBadge from './RiskBadge';

interface Props { patientId: string; }

function toErrorMessage(err: any): string {
  const detail = err?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (detail && typeof detail === 'object') return JSON.stringify(detail);
  if (typeof err?.response?.data?.message === 'string') return err.response.data.message;
  if (typeof err?.message === 'string') return err.message;
  return 'Failed';
}

function toStringArray(value: any): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => {
    if (typeof item === 'string') return item;
    if (item == null) return '';
    if (typeof item === 'object') return JSON.stringify(item);
    return String(item);
  }).filter(Boolean);
}

function errorPayloadMessage(data: any): string | null {
  if (!data || typeof data !== 'object') return null;
  if (typeof data.detail === 'string' && data.detail.trim()) return data.detail;
  if (typeof data.message === 'string' && /failed|error/i.test(data.message)) return data.message;
  return null;
}

function normalizeResult(data: any): OnboardingResult {
  const result = data?.result ?? {};
  return {
    request_id: data?.request_id ?? '',
    agent_type: data?.agent_type ?? 'onboarding',
    patient_id: data?.patient_id ?? '',
    status: data?.status ?? 'completed',
    result: {
      risk_score: Number(result?.risk_score ?? 0),
      risk_level: String(result?.risk_level ?? ''),
      summary: String(result?.summary ?? ''),
      key_findings: toStringArray(result?.key_findings),
      recommendations: toStringArray(result?.recommendations),
      alert_created: Boolean(result?.alert_created),
      next_steps: toStringArray(result?.next_steps),
    },
    sources: Array.isArray(data?.sources) ? data.sources : [],
    processing_time_ms: Number(data?.processing_time_ms ?? 0),
    errors: toStringArray(data?.errors),
  };
}

export default function OnboardingPanel({ patientId }: Props) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<OnboardingResult | null>(null);
  const [error, setError] = useState('');

  const run = async () => {
    setLoading(true); setError(''); setResult(null);
    try {
      const data = await aiApi.onboardPatient(patientId);
      const responseError = errorPayloadMessage(data);
      if (responseError) {
        setError(responseError);
        return;
      }
      setResult(normalizeResult(data));
    } catch (e: any) {
      setError(toErrorMessage(e));
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

          {!result.result.summary && result.result.key_findings.length === 0 && result.result.recommendations.length === 0 && (
            <div style={{ padding: 12, background: '#f8fafc', borderRadius: 8, fontSize: 14, color: 'var(--text-secondary)' }}>
              No structured onboarding output was returned. Please retry once the AI service connection is available.
            </div>
          )}

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