#!/bin/bash
set -e
TAG=${1:-latest}; REGION=${AWS_REGION:-us-east-1}; ACCT=$(aws sts get-caller-identity --query Account --output text)
ECR="$ACCT.dkr.ecr.$REGION.amazonaws.com"
echo "=== Deploy tag: $TAG ==="
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR
docker build -t $ECR/healthmap/ai-agent-service:$TAG services/ai-agent-service && docker push $ECR/healthmap/ai-agent-service:$TAG
docker build -t $ECR/healthmap/api-gateway:$TAG services/api-gateway && docker push $ECR/healthmap/api-gateway:$TAG
aws eks update-kubeconfig --name healthmap-ai-platform --region $REGION
sed "s|ACCOUNT_ID|$ACCT|g; s|:latest|:$TAG|g" infra/k8s/all-manifests.yaml | kubectl apply -f -
kubectl -n healthmap rollout status deployment/ai-agent-service --timeout=300s
kubectl -n healthmap rollout status deployment/api-gateway --timeout=300s
echo "=== Deploy complete ==="
