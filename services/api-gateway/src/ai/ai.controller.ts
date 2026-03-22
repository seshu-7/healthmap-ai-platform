import { Controller, Post, Body, UseGuards, Req, HttpException, HttpStatus, Logger } from "@nestjs/common";
import { AuthGuard } from "../auth/auth.guard";
import { AiService } from "./ai.service";
import { IsString, IsOptional, IsInt, Min, Max } from "class-validator";

export class OnboardingDto { @IsString() patientId!: string; @IsOptional() @IsString() notes?: string; }
export class AssessmentDto { @IsString() patientId!: string; @IsOptional() @IsString() assessmentType?: string; }
export class SearchDto { @IsString() query!: string; @IsOptional() @IsString() condition?: string; @IsOptional() @IsInt() @Min(1) @Max(20) topK?: number; }

@Controller("ai")
@UseGuards(AuthGuard)
export class AiController {
  private readonly logger = new Logger(AiController.name);
  constructor(private readonly ai: AiService) {}

  @Post("onboarding")
  async onboard(@Body() dto: OnboardingDto, @Req() req: any) {
    const cid = req.user?.coordinatorId || "unknown";
    this.logger.log(`Onboarding ${dto.patientId} by ${cid}`);
    try { return await this.ai.runOnboarding(dto.patientId, cid); }
    catch (e) { throw new HttpException({ message: "Onboarding failed", detail: (e as Error).message }, HttpStatus.INTERNAL_SERVER_ERROR); }
  }

  @Post("assessment")
  async assess(@Body() dto: AssessmentDto) {
    try { return await this.ai.runAssessment(dto.patientId, dto.assessmentType); }
    catch (e) { throw new HttpException({ message: "Assessment failed", detail: (e as Error).message }, HttpStatus.INTERNAL_SERVER_ERROR); }
  }

  @Post("search")
  async search(@Body() dto: SearchDto) {
    try { return await this.ai.searchGuidelines(dto.query, dto.condition, dto.topK || 5); }
    catch (e) { throw new HttpException({ message: "Search failed", detail: (e as Error).message }, HttpStatus.INTERNAL_SERVER_ERROR); }
  }
}
