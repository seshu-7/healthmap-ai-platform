// Patient types
export interface Patient {
  patientId: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  gender: string;
  primaryCondition: string;
  conditions: string[];
  insurancePlan: string;
  assignedCoordinator: string;
}

// Lab result
export interface LabResult {
  labId: string;
  patientId: string;
  testName: string;
  value: number;
  unit: string;
  referenceRange: string;
  isAbnormal: boolean;
  collectedDate: string;
}

// Medication
export interface Medication {
  medicationId: string;
  patientId: string;
  drugName: string;
  dosage: string;
  frequency: string;
  prescriber: string;
  startDate: string;
  isActive: boolean;
}

// Alert
export interface Alert {
  alertId: string;
  patientId: string;
  priority: 'ROUTINE' | 'URGENT' | 'CRITICAL';
  title: string;
  description: string;
  recommendedAction: string;
  status: 'OPEN' | 'ACKNOWLEDGED' | 'RESOLVED';
  createdAt: string;
}

// AI Onboarding response
export interface OnboardingResult {
  request_id: string;
  agent_type: string;
  patient_id: string;
  status: string;
  result: {
    risk_score: number;
    risk_level: string;
    summary: string;
    key_findings: string[];
    recommendations: string[];
    alert_created: boolean;
    next_steps: string[];
  };
  sources: string[];
  processing_time_ms: number;
  errors: string[];
}

// RAG search
export interface GuidelineResult {
  content: string;
  score: number;
  metadata: {
    documentTitle: string;
    condition: string;
    documentType: string;
  };
}

// Eval report
export interface EvalReport {
  summary: {
    totalScenarios: number;
    passed: number;
    failed: number;
    passRate: number;
    threshold: number;
    meetsThreshold: boolean;
  };
  scores: {
    avgCorrectness: number;
    avgCompleteness: number;
    hallucinationCount: number;
    formatFailures: number;
  };
  results: EvalScenarioResult[];
}

export interface EvalScenarioResult {
  scenarioId: string;
  passed: boolean;
  correctness: number;
  completeness: number;
  hallucination: boolean;
  formatValid: boolean;
}