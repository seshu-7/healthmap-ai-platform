import { Controller, Get } from "@nestjs/common";
@Controller("health")
export class HealthController {
  @Get() check() { return { status: "ok", service: "healthmap-api-gateway" }; }
  @Get("ready") ready() { return { status: "ready" }; }
}
