import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import { PatientsController } from "./patients.controller";
import { PatientsService } from "./patients.service";
@Module({ imports: [ConfigModule], controllers: [PatientsController], providers: [PatientsService] })
export class PatientsModule {}
