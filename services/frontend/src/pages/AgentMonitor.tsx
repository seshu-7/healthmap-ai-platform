import { useState, useEffect } from 'react';
import { mcpApi } from '../services/api';

export default function AgentMonitor() {
  const [servers, setServers] = useState<any[]>([]);
  const [tools, setTools] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      mcpApi.getServers().catch(() => []),
      mcpApi.getTools().catch(() => []),
    ]).then(([s, t]) => { setServers(s); setTools(t); setLoading(false); });
  }, []);

  return (
    <div>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 4 }}>📊 Agent Monitor</h1>
      <p style={{ color: 'var(--text-secondary)', fontSize: 14, marginBottom: 20 }}>
        MCP servers, available tools, and agent infrastructure
      </p>

      {loading ? <div className="spinner" /> : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div className="card">
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>MCP Servers ({servers.length})</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 }}>
              {servers.map((s: any, i: number) => (
                <div key={i} style={{ padding: 16, border: '1px solid var(--border)', borderRadius: 8 }}>
                  <div style={{ fontWeight: 700, fontSize: 15 }}>{s.name}</div>
                  <div style={{ fontSize: 13, color: 'var(--text-secondary)', margin: '4px 0' }}>{s.description}</div>
                  <div style={{ fontSize: 12, color: 'var(--primary)' }}>{s.tools?.length || 0} tools · v{s.version}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 style={{ fontSize: 16, fontWeight: 700, marginBottom: 12 }}>Available Tools ({tools.length})</h3>
            <table className="table">
              <thead><tr><th>Tool</th><th>Server</th><th>Description</th></tr></thead>
              <tbody>
                {tools.map((t: any, i: number) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 600, fontFamily: 'monospace', fontSize: 13 }}>{t.name}</td>
                    <td><span className="badge badge-moderate">{t.server}</span></td>
                    <td style={{ color: 'var(--text-secondary)' }}>{t.description}</td>
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