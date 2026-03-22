import axios from 'axios';
import type { Patient, LabResult, Medication, Alert, OnboardingResult, GuidelineResult, EvalReport } from '../types';

const gateway = axios.create({ baseURL: '/api/v1', timeout: 120000 });
const ai = axios.create({ baseURL: 'http://localhost:8000', timeout: 120000 });

// Intercept to add JWT
gateway.interceptors.request.use((config) => {
  const token = localStorage.getItem('jwt');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Patient APIs (via Gateway -> Spring Boot) ──

export const patientApi = {
  getById: (id: string) =>
    gateway.get<Patient>(`/patients/${id}`).then(r => r.data),

  search: (q: string) =>
    gateway.get<Patient[]>(`/patients/search`, { params: { q } }).then(r => r.data),

  getByCoordinator: (coordId: string) =>
    gateway.get<Patient[]>(`/patients/coordinator/${coordId}`).then(r => r.data),
};

// ── Lab APIs ──

export const labApi = {
  getByPatient: (patientId: string, limit = 10) =>
    gateway.get<{ results: LabResult[] }>(`/patients/${patientId}/labs`, { params: { limit } })
      .then(r => r.data.results),
};

// ── Medication APIs ──

export const medApi = {
  getByPatient: (patientId: string) =>
    gateway.get<{ medications: Medication[] }>(`/patients/${patientId}/medications`)
      .then(r => r.data.medications),
};

// ── Alert APIs ──

export const alertApi = {
  getByPatient: (patientId: string) =>
    gateway.get<Alert[]>(`/alerts/patient/${patientId}`).then(r => r.data),

  getOpen: () =>
    gateway.get<Alert[]>(`/alerts/open`).then(r => r.data),
};

// ── AI Agent APIs (via Gateway -> Python AI Service) ──

export const aiApi = {
  onboardPatient: (patientId: string) =>
    gateway.post<OnboardingResult>('/ai/onboarding', { patientId }).then(r => r.data),

  assessPatient: (patientId: string) =>
    gateway.post('/ai/assessment', { patientId }).then(r => r.data),

  searchGuidelines: (query: string, condition?: string) =>
    gateway.post<{ results: GuidelineResult[] }>('/ai/search', { query, condition })
      .then(r => r.data.results),
};

// ── Eval APIs (direct to AI service) ──

export const evalApi = {
  run: (threshold = 0.8) =>
    ai.post<EvalReport>('/api/v1/evals/run', null, { params: { threshold } }).then(r => r.data),
};

// ── MCP APIs ──

export const mcpApi = {
  getServers: () => ai.get('/api/v1/mcp/servers').then(r => r.data.servers),
  getTools: () => ai.get('/api/v1/mcp/tools').then(r => r.data.tools),
};