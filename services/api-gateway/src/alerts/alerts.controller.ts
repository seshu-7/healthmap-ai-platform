import { Controller, Get, Param, UseGuards } from "@nestjs/common";
import { AuthGuard } from "../auth/auth.guard";
import { AlertsService } from "./alerts.service";

@Controller("alerts")
@UseGuards(AuthGuard)
export class AlertsController {
  constructor(private readonly svc: AlertsService) {}

  @Get("open")
  getOpen() {
    return this.svc.getOpen();
  }

  @Get("patient/:patientId")
  getByPatient(@Param("patientId") patientId: string) {
    return this.svc.getByPatient(patientId);
  }
}
