import { Injectable, ExecutionContext } from "@nestjs/common";
import { AuthGuard as PassportAuthGuard } from "@nestjs/passport";

@Injectable()
export class AuthGuard extends PassportAuthGuard("jwt") {
  canActivate(context: ExecutionContext) {
    const authDisabled = (process.env.AUTH_DISABLED ?? "true").toLowerCase() === "true";
    if (authDisabled) return true;
    return super.canActivate(context);
  }
}
