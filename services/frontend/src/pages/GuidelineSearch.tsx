import { useState } from 'react';
import { aiApi } from '../services/api';
import type { GuidelineResult } from '../types';

export default function GuidelineSearch() {
  const [query, setQuery] = useState('');
  const [condition, setCondition] = useState('');
  const [results, setResults] = useState<GuidelineResult[]>([]);
  const [loading, setLoading] = useState(false);

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const data = await aiApi.searchGuidelines(query, condition || undefined);
      setResults(data);
    } catch { setResults([]); }
    finally { setLoading(false); }
  };

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>📋 Clinical Guideline Search</h1>
      <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginBottom: 20 }}>
        RAG-powered search across clinical guidelines stored in Pinecone
      </p>

      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'flex-end' }}>
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: 13, fontWeight: 600, display: 'block', marginBottom: 4 }}>Clinical Question</label>
            <input value={query} onChange={e => setQuery(e.target.value)}
              placeholder="e.g., What is the eGFR monitoring schedule for CKD Stage 3?"
              style={{ width: '100%' }}
              onKeyDown={e => e.key === 'Enter' && search()} />
          </div>
          <div style={{ width: 180 }}>
            <label style={{ fontSize: 13, fontWeight: 600, display: 'block', marginBottom: 4 }}>Condition Filter</label>
            <select value={condition} onChange={e => setCondition(e.target.value)} style={{ width: '100%' }}>
              <option value="">All conditions</option>
              <option value="ckd">CKD</option>
              <option value="diabetes">Diabetes</option>
              <option value="heart_failure">Heart Failure</option>
            </select>
          </div>
          <button className="btn btn-primary" onClick={search} disabled={loading} style={{ height: 38 }}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {results.map((r, i) => (
        <div key={i} className="card" style={{ marginBottom: 12 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <span style={{ fontWeight: 700, fontSize: 15 }}>{r.metadata.documentTitle}</span>
              <span className="badge badge-moderate">{r.metadata.condition}</span>
            </div>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
              Relevance: {(r.score * 100).toFixed(1)}%
            </span>
          </div>
          <p style={{ fontSize: 14, lineHeight: 1.7, color: 'var(--text)', whiteSpace: 'pre-wrap' }}>{r.content}</p>
        </div>
      ))}
    </div>
  );
}