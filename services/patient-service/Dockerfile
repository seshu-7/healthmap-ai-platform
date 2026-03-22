FROM eclipse-temurin:17-jre-alpine
LABEL service="healthmap-patient-service"
WORKDIR /app
COPY target/patient-service-1.0.0.jar app.jar
RUN adduser -D appuser && chown -R appuser:appuser /app
USER appuser
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://localhost:8080/actuator/health || exit 1
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
