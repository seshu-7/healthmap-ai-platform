import { NavLink, Outlet } from 'react-router-dom';

const navItems = [
  { to: '/', label: 'Dashboard', icon: '🏠' },
  { to: '/alerts', label: 'Alerts', icon: '🔔' },
  { to: '/guidelines', label: 'Guidelines', icon: '📋' },
  { to: '/evals', label: 'AI Evals', icon: '✅' },
  { to: '/monitor', label: 'Agent Monitor', icon: '📊' },
];

export default function Layout() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Sidebar */}
      <aside style={{
        width: 220, background: '#0d1117', color: '#e6edf3', padding: '20px 0',
        display: 'flex', flexDirection: 'column', flexShrink: 0,
      }}>
        <div style={{ padding: '0 20px 24px', borderBottom: '1px solid #21262d' }}>
          <div style={{ fontSize: 18, fontWeight: 700, color: '#58a6ff' }}>HealthMap</div>
          <div style={{ fontSize: 11, color: '#8b949e', marginTop: 2 }}>AI Care Platform</div>
        </div>
        <nav style={{ padding: '12px 0', flex: 1 }}>
          {navItems.map(item => (
            <NavLink key={item.to} to={item.to} end={item.to === '/'}
              style={({ isActive }) => ({
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '10px 20px', fontSize: 14, color: isActive ? '#58a6ff' : '#8b949e',
                background: isActive ? '#161b22' : 'transparent',
                borderLeft: isActive ? '3px solid #58a6ff' : '3px solid transparent',
                textDecoration: 'none', fontWeight: isActive ? 600 : 400,
              })}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
        <div style={{ padding: '12px 20px', borderTop: '1px solid #21262d', fontSize: 12, color: '#484f58' }}>
          Coordinator: C001
        </div>
      </aside>

      {/* Main content */}
      <main style={{ flex: 1, padding: '24px 32px', overflowY: 'auto' }}>
        <Outlet />
      </main>
    </div>
  );
}