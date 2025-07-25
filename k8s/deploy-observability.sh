#!/bin/bash
# Quick deployment script for TradeWise AI observability stack

set -e

NAMESPACE="tradewise-ai"

echo "🔍 Deploying TradeWise AI Observability Stack..."

# Create namespace if it doesn't exist
kubectl get namespace $NAMESPACE 2>/dev/null || kubectl create namespace $NAMESPACE

# Deploy Prometheus
echo "📊 Deploying Prometheus..."
kubectl apply -f prometheus-deployment.yaml

# Deploy Grafana
echo "📈 Deploying Grafana..."
kubectl apply -f grafana-deployment.yaml

# Deploy Alertmanager
echo "🚨 Deploying Alertmanager..."
kubectl apply -f alertmanager-deployment.yaml

# Deploy ServiceMonitors (if Prometheus Operator available)
echo "🔗 Deploying ServiceMonitors..."
if kubectl api-resources | grep -q servicemonitors; then
    kubectl apply -f servicemonitor.yaml
    echo "✅ ServiceMonitors deployed"
else
    echo "⚠️  Prometheus Operator not found, skipping ServiceMonitors"
fi

# Wait for deployments to be ready
echo "⏳ Waiting for observability stack to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/prometheus-deployment -n $NAMESPACE
kubectl wait --for=condition=available --timeout=300s deployment/grafana-deployment -n $NAMESPACE
kubectl wait --for=condition=available --timeout=300s deployment/alertmanager-deployment -n $NAMESPACE

echo "✅ Observability stack deployed successfully!"
echo ""
echo "🌐 Access your monitoring tools:"
echo "Prometheus:   kubectl port-forward -n $NAMESPACE service/prometheus-service 9090:9090"
echo "Grafana:      kubectl port-forward -n $NAMESPACE service/grafana-service 3000:3000"
echo "Alertmanager: kubectl port-forward -n $NAMESPACE service/alertmanager-service 9093:9093"
echo ""
echo "🔑 Grafana credentials: admin / tradewise_grafana_secure_password"