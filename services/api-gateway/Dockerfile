FROM node:20-alpine as builder
WORKDIR /build
COPY package*.json ./
RUN npm ci
COPY tsconfig.json ./
COPY src/ ./src/
RUN npm run build

FROM node:20-alpine
LABEL service="healthmap-api-gateway"
WORKDIR /app
COPY --from=builder /build/dist ./dist
COPY --from=builder /build/node_modules ./node_modules
COPY --from=builder /build/package.json ./
RUN adduser -D appuser && chown -R appuser:appuser /app
USER appuser
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD wget -qO- http://localhost:3000/api/v1/health || exit 1
EXPOSE 3000
CMD ["node", "dist/main"]
