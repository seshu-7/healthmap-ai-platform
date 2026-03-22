import { Injectable } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import axios, { AxiosInstance } from "axios";

@Injectable()
export class AiService {
  private readonly client: AxiosInstance;
  constructor(config: ConfigService) {
    this.client = axios.create({ baseURL: config.get("AI_SERVICE_URL", "http://localhost:8000"), timeout: 120000 });
  }
  async runOnboarding(patientId: string, coordinatorId: string) {
    return (await this.client.post("/api/v1/agents/onboarding", { patient_id: patientId, coordinator_id: coordinatorId })).data;
  }
  async runAssessment(patientId: string, type?: string) {
    return (await this.client.post("/api/v1/agents/assessment", { patient_id: patientId, assessment_type: type || "comprehensive" })).data;
  }
  async searchGuidelines(query: string, condition?: string, topK?: number) {
    return (await this.client.post("/api/v1/rag/search", null, { params: { query, condition, top_k: topK } })).data;
  }
}
