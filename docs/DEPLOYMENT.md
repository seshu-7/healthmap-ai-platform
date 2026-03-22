# Deployment Guide

## Steps

1. **Provision Infrastructure**: `cd infra/terraform && terraform apply`
2. **Configure kubectl**: `aws eks update-kubeconfig --name healthmap-ai-platform`
3. **Create Secrets**: `kubectl create secret generic healthmap-secrets --namespace=healthmap --from-literal=openai-api-key=sk-...`
4. **Build & Push**: `docker build` + `docker push` to ECR (see scripts/deploy.sh)
5. **Deploy**: `kubectl apply -f infra/k8s/all-manifests.yaml`
6. **Verify**: `kubectl -n healthmap get pods` + `curl /health`
7. **Load RAG Data**: `python -m app.rag.ingestion --sample-data`
8. **Run Evals**: `curl -X POST /api/v1/evals/run?threshold=0.80`

## Rollback
```bash
kubectl -n healthmap rollout undo deployment/ai-agent-service
```

## Auto-scaling
HPA scales ai-agent-service from 2 to 8 pods based on CPU (70% threshold).
