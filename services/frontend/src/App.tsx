import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import PatientDetail from './pages/PatientDetail';
import GuidelineSearch from './pages/GuidelineSearch';
import AlertsPage from './pages/AlertsPage';
import EvalDashboard from './pages/EvalDashboard';
import AgentMonitor from './pages/AgentMonitor';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/patients/:id" element={<PatientDetail />} />
          <Route path="/guidelines" element={<GuidelineSearch />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/evals" element={<EvalDashboard />} />
          <Route path="/monitor" element={<AgentMonitor />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}