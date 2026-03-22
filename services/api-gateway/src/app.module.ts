import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import { ThrottlerModule, ThrottlerGuard } from "@nestjs/throttler";
import { APP_GUARD } from "@nestjs/core";
import { AuthModule } from "./auth/auth.module";
import { PatientsModule } from "./patients/patients.module";
import { AiModule } from "./ai/ai.module";
import { HealthModule } from "./health/health.module";
import { AlertsModule } from "./alerts/alerts.module";

@Module({
  imports: [ConfigModule.forRoot({ isGlobal: true }), ThrottlerModule.forRoot([{ ttl: 60000, limit: 100 }]), AuthModule, PatientsModule, AlertsModule, AiModule, HealthModule],
  providers: [{ provide: APP_GUARD, useClass: ThrottlerGuard }],
})
export class AppModule {}
