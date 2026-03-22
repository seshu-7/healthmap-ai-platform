import { Controller, Get, Param, Query, UseGuards } from "@nestjs/common";
import { AuthGuard } from "../auth/auth.guard";
import { PatientsService } from "./patients.service";

@Controller("patients")
@UseGuards(AuthGuard)
export class PatientsController {
  constructor(private readonly svc: PatientsService) {}

  @Get("search")
  search(@Query("q") q: string) {
    return this.svc.searchPatients(q ?? "");
  }

  @Get("coordinator/:coordinatorId")
  byCoordinator(@Param("coordinatorId") coordinatorId: string) {
    return this.svc.getByCoordinator(coordinatorId);
  }

  @Get(":id") get(@Param("id") id: string) { return this.svc.getPatient(id); }
  @Get(":id/labs") labs(@Param("id") id: string) { return this.svc.getLabs(id); }
  @Get(":id/medications") meds(@Param("id") id: string) { return this.svc.getMeds(id); }
}
