import { Injectable } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import axios, { AxiosInstance } from "axios";

@Injectable()
export class PatientsService {
  private readonly client: AxiosInstance;
  constructor(config: ConfigService) {
    this.client = axios.create({ baseURL: config.get("PATIENT_SERVICE_URL", "http://localhost:8081"), timeout: 10000 });
  }
  async searchPatients(q: string) {
    return (await this.client.get(`/api/v1/patients/search`, { params: { q } })).data;
  }
  async getByCoordinator(coordinatorId: string) {
    return (await this.client.get(`/api/v1/patients/coordinator/${coordinatorId}`)).data;
  }
  async getPatient(id: string) { return (await this.client.get(`/api/v1/patients/${id}`)).data; }
  async getLabs(id: string) { return (await this.client.get(`/api/v1/labs/${id}`)).data; }
  async getMeds(id: string) { return (await this.client.get(`/api/v1/medications/${id}`)).data; }
}
