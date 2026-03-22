import { Module } from "@nestjs/common";
import { JwtModule } from "@nestjs/jwt";
import { PassportModule } from "@nestjs/passport";
import { ConfigModule, ConfigService } from "@nestjs/config";
import { JwtStrategy } from "./jwt.strategy";
import { AuthGuard } from "./auth.guard";

@Module({
  imports: [PassportModule.register({ defaultStrategy: "jwt" }),
    JwtModule.registerAsync({ imports: [ConfigModule], inject: [ConfigService],
      useFactory: (c: ConfigService) => ({ secret: c.get("JWT_SECRET", "dev-secret-change-in-prod"), signOptions: { expiresIn: "8h" } }) })],
  providers: [JwtStrategy, AuthGuard],
  exports: [JwtModule, PassportModule, AuthGuard],
})
export class AuthModule {}
