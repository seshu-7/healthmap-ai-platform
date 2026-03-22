FROM python:3.11-slim as builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
LABEL service="healthmap-ai-agent"
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ ./app/
RUN mkdir -p /home/appuser/.mem0 \
  && useradd -r -d /home/appuser -s /usr/sbin/nologin appuser \
  && chown -R appuser:appuser /app /home/appuser
ENV HOME=/home/appuser
USER appuser
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]