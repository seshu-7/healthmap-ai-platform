import { Injectable } from "@nestjs/common";
import { ConfigService } from "@nestjs/config";
import axios, { AxiosInstance } from "axios";

@Injectable()
export class AlertsService {
  private readonly client: AxiosInstance;

  constructor(config: ConfigService) {
    this.client = axios.create({
      baseURL: config.get("PATIENT_SERVICE_URL", "http://localhost:8081"),
      timeout: 10000,
    });
  }

  async getOpen() {
    return (await this.client.get(`/api/v1/alerts/open`)).data;
  }

  async getByPatient(patientId: string) {
    return (await this.client.get(`/api/v1/alerts/patient/${patientId}`)).data;
  }
}
