# TradeWise AI - Monitoring & Observability Guide
## Complete Observability Stack with Prometheus, Grafana & Alertmanager
### Version: 1.0 | Date: July 25, 2025

---

## TABLE OF CONTENTS

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Accessing Dashboards](#accessing-dashboards)
4. [Understanding Metrics](#understanding-metrics)
5. [Alert Management](#alert-management)
6. [Dashboard Usage](#dashboard-usage)
7. [Adding New Metrics](#adding-new-metrics)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Runbook References](#runbook-references)

---

## OVERVIEW

TradeWise AI includes a comprehensive observability stack providing real-time visibility into application performance, infrastructure health, and business metrics.

### Architecture Components
- **Prometheus**: Metrics collection and alerting engine
- **Grafana**: Visualization dashboards and analytics
- **Alertmanager**: Alert routing and notification management
- **ServiceMonitors**: Automatic service discovery and scraping

### Key Capabilities
- **Real-time Monitoring**: Sub-minute metric collection
- **Proactive Alerting**: Critical and warning notifications
- **Performance Analytics**: Request latency, error rates, throughput
- **Infrastructure Monitoring**: CPU, memory, storage, network
- **Business Intelligence**: Stock analysis usage, user patterns

---

## QUICK START

### Deploy Monitoring Stack
```bash
# Deploy complete observability stack
kubectl apply -f k8s/prometheus-deployment.yaml
kubectl apply -f k8s/grafana-deployment.yaml
kubectl apply -f k8s/alertmanager-deployment.yaml
kubectl apply -f k8s/servicemonitor.yaml

# Verify deployment
kubectl get pods -n tradewise-ai -l monitoring=prometheus
```

### Access Services Locally
```bash
# Prometheus
kubectl port-forward -n tradewise-ai service/prometheus-service 9090:9090

# Grafana
kubectl port-forward -n tradewise-ai service/grafana-service 3000:3000

# Alertmanager
kubectl port-forward -n tradewise-ai service/alertmanager-service 9093:9093
```

### Default Credentials
- **Grafana**: admin / tradewise_grafana_secure_password
- **Prometheus**: No authentication required
- **Alertmanager**: No authentication required

---

## ACCESSING DASHBOARDS

### Grafana Dashboards

#### Production Access (via Ingress)
```bash
# Access through ingress (production)
https://grafana.tradewise-ai.com

# Or via LoadBalancer service
kubectl patch service grafana-service -p '{"spec": {"type": "LoadBalancer"}}'
```

#### Available Dashboards

##### 1. TradeWise AI - API Performance
**Purpose**: Monitor API request patterns, response times, and error rates
**URL**: `/d/api-performance`

**Key Metrics**:
- Request rate (requests/second)
- Response time percentiles (p50, p90, p99)
- Error rate percentage
- Active API pods
- Cache hit rate

**Alert Thresholds**:
- Response time p99 > 500ms
- Error rate > 5%
- Cache hit rate < 50%

##### 2. TradeWise AI - Workers & Queue
**Purpose**: Monitor background processing and task queue health
**URL**: `/d/workers-queue`

**Key Metrics**:
- Task queue depth
- Worker CPU/memory usage
- Task success rate
- Active worker count
- Processing throughput

**Alert Thresholds**:
- Queue depth > 50 tasks
- Worker CPU > 80%
- Task failure rate > 10%

##### 3. TradeWise AI - Infrastructure
**Purpose**: Monitor cluster health and resource utilization
**URL**: `/d/infrastructure`

**Key Metrics**:
- Database/Redis status
- Pod restart count
- Cluster CPU/memory usage
- Storage utilization
- Network performance

**Alert Thresholds**:
- Database/Redis down
- Pod restarts > 3 in 15min
- Memory usage > 90%

### Prometheus Targets

#### View Scraping Status
```bash
# Access Prometheus UI
http://localhost:9090

# Check target health
http://localhost:9090/targets

# Query metrics directly
http://localhost:9090/graph
```

#### Key Endpoints Being Scraped
- **API Pods**: `/api/performance/stats` (30s interval)
- **Worker Pods**: `/metrics` (30s interval)
- **Database**: `/metrics` (30s interval)
- **Redis**: `/metrics` (30s interval)
- **Kubernetes**: Various cluster endpoints

---

## UNDERSTANDING METRICS

### Application Metrics

#### API Performance
```prometheus
# Request rate
rate(flask_request_total[5m])

# Response time percentiles
histogram_quantile(0.95, rate(flask_request_duration_seconds_bucket[5m]))

# Error rate
rate(flask_request_exceptions_total[5m]) / rate(flask_request_total[5m])

# Cache performance
tradewise_cache_hit_rate
tradewise_cache_miss_rate
```

#### Worker Performance
```prometheus
# Queue depth
tradewise_task_queue_length

# Task success rate
rate(tradewise_tasks_completed_total[5m]) / rate(tradewise_tasks_total[5m])

# Worker resource usage
rate(container_cpu_usage_seconds_total{pod=~"tradewise-worker.*"}[5m])
container_memory_usage_bytes{pod=~"tradewise-worker.*"}
```

#### Business Metrics
```prometheus
# Stock analysis requests
rate(flask_request_total{endpoint="/api/stock-analysis"}[1h])

# Premium user activity
rate(flask_request_total{user_tier="premium"}[1h])

# AI model usage
tradewise_ai_model_requests_total
tradewise_ai_model_latency_seconds
```

### Infrastructure Metrics

#### Kubernetes Cluster
```prometheus
# Pod health
up{job="kubernetes-pods"}

# Resource utilization
container_cpu_usage_seconds_total
container_memory_usage_bytes
kubelet_volume_stats_used_bytes

# Pod restarts
increase(kube_pod_container_status_restarts_total[15m])
```

#### Database Performance
```prometheus
# Connection status
up{job="postgres"}

# Query performance
postgres_stat_user_tables_seq_scan
postgres_stat_user_tables_n_tup_ins

# Cache performance
redis_connected_clients
redis_used_memory_bytes
```

---

## ALERT MANAGEMENT

### Alert Severity Levels

#### Critical Alerts (15-minute repeat)
- API error rate > 5%
- Database/Redis down
- Pod crash looping
- High memory usage (>90%)

#### Warning Alerts (1-hour repeat)
- High response time (p99 > 500ms)
- Task queue backlog (>50 tasks)
- Low cache hit rate (<50%)
- High CPU usage (>80%)

### Notification Channels

#### Email Notifications
```yaml
# Critical alerts
To: ops-team@tradewise-ai.com
Subject: 🚨 CRITICAL: [Alert Name] - TradeWise AI

# Warning alerts  
To: dev-team@tradewise-ai.com
Subject: ⚠️ WARNING: [Alert Name] - TradeWise AI
```

#### Slack Integration
```yaml
# Critical channel
Channel: #alerts-critical
Color: danger (red)

# Warning channel
Channel: #alerts-warning
Color: warning (yellow)
```

### Responding to Alerts

#### High API Error Rate
1. **Check Grafana dashboard** for error patterns
2. **Review application logs**: `kubectl logs -f deployment/tradewise-api-deployment`
3. **Scale up API pods** if resource constrained: `./scale.sh scale-api 10`
4. **Check database connectivity** and external API status

#### High Response Time
1. **Identify slow endpoints** in Grafana API dashboard
2. **Check cache hit rates** and database performance
3. **Scale horizontally** if CPU/memory constrained
4. **Review recent deployments** for performance regressions

#### Task Queue Backlog
1. **Scale worker pods**: `./scale.sh scale-workers 5`
2. **Check worker logs** for processing errors
3. **Monitor queue drain rate** in Grafana
4. **Investigate task failures** in application metrics

#### Database/Redis Down
1. **Check pod status**: `kubectl get pods -n tradewise-ai`
2. **Review pod logs**: `kubectl logs deployment/postgres-deployment`
3. **Verify persistent volume** health and connectivity
4. **Restart services** if necessary: `kubectl rollout restart deployment/postgres-deployment`

### Silencing Alerts

#### Temporary Silence (Maintenance)
```bash
# Access Alertmanager
http://localhost:9093

# Create silence
curl -X POST http://localhost:9093/api/v1/silences \
  -H 'Content-Type: application/json' \
  -d '{
    "matchers": [
      {"name": "alertname", "value": "HighLatency"}
    ],
    "startsAt": "2025-07-25T20:00:00Z",
    "endsAt": "2025-07-25T21:00:00Z",
    "createdBy": "ops-team",
    "comment": "Planned maintenance window"
  }'
```

---

## DASHBOARD USAGE

### Grafana Best Practices

#### Time Range Selection
- **Real-time monitoring**: Last 15 minutes, 30-second refresh
- **Incident investigation**: Last 1-4 hours, 1-minute refresh
- **Performance analysis**: Last 24 hours, 5-minute refresh
- **Capacity planning**: Last 7-30 days, 1-hour refresh

#### Panel Customization
```json
// Add new panel
{
  "title": "Custom Metric",
  "type": "graph",
  "targets": [
    {
      "expr": "your_prometheus_query_here",
      "legendFormat": "{{ label }}"
    }
  ]
}
```

#### Variable Usage
- **Environment**: Filter by production/staging
- **Service**: Focus on specific components
- **Time Range**: Dynamic time window selection
- **Instance**: Drill down to specific pods

### Creating Custom Dashboards

#### Dashboard Template
```json
{
  "dashboard": {
    "title": "Custom TradeWise Dashboard",
    "tags": ["tradewise", "custom"],
    "templating": {
      "list": [
        {
          "name": "namespace",
          "type": "constant",
          "current": {"value": "tradewise-ai"}
        }
      ]
    },
    "panels": [
      // Your panels here
    ]
  }
}
```

#### Import/Export
```bash
# Export dashboard
curl -H "Authorization: Bearer <api-key>" \
  http://localhost:3000/api/dashboards/uid/<dashboard-uid>

# Import dashboard
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer <api-key>" \
  -d @dashboard.json \
  http://localhost:3000/api/dashboards/db
```

---

## ADDING NEW METRICS

### Application Metrics

#### Custom Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, Gauge

# Counter: Monotonically increasing
user_actions_total = Counter('tradewise_user_actions_total', 
                           'Total user actions', 
                           ['action_type', 'user_tier'])

# Histogram: Measure durations/sizes
request_duration = Histogram('tradewise_request_duration_seconds',
                           'Request duration',
                           ['endpoint', 'method'])

# Gauge: Current value
active_users = Gauge('tradewise_active_users',
                    'Current active users')

# Usage
user_actions_total.labels(action_type='stock_search', user_tier='premium').inc()
request_duration.labels(endpoint='/api/stock-analysis', method='GET').observe(0.245)
active_users.set(42)
```

#### Expose Metrics Endpoint
```python
from flask import Flask
from prometheus_client import generate_latest

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}
```

### Infrastructure Metrics

#### Custom ServiceMonitor
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: custom-service-monitor
  namespace: tradewise-ai
spec:
  selector:
    matchLabels:
      app: custom-app
  endpoints:
  - port: metrics
    path: /metrics
    interval: 30s
```

#### Database Metrics
```yaml
# PostgreSQL Exporter
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres-exporter
spec:
  template:
    spec:
      containers:
      - name: postgres-exporter
        image: prometheuscommunity/postgres-exporter:v0.12.0
        env:
        - name: DATA_SOURCE_NAME
          value: "postgresql://user:pass@postgres:5432/db?sslmode=disable"
```

### Alert Rules

#### Custom Alert Definition
```yaml
groups:
- name: custom.alerts
  rules:
  - alert: CustomMetricHigh
    expr: custom_metric_value > 100
    for: 5m
    labels:
      severity: warning
      team: platform
    annotations:
      summary: "Custom metric is high"
      description: "Custom metric value is {{ $value }}"
      runbook_url: "https://docs.tradewise-ai.com/runbooks/custom-metric"
```

---

## TROUBLESHOOTING

### Common Issues

#### Prometheus Not Scraping Targets
```bash
# Check target discovery
kubectl logs -f deployment/prometheus-deployment -n tradewise-ai

# Verify service labels
kubectl get services -n tradewise-ai --show-labels

# Test metric endpoint
kubectl exec -it <api-pod> -- curl localhost:5000/api/performance/stats
```

#### Grafana Dashboard Not Loading
```bash
# Check Grafana logs
kubectl logs -f deployment/grafana-deployment -n tradewise-ai

# Verify datasource connection
curl -H "Authorization: Bearer <api-key>" \
  http://localhost:3000/api/datasources/proxy/1/api/v1/query?query=up

# Test Prometheus connectivity
kubectl exec -it <grafana-pod> -- nc -zv prometheus-service 9090
```

#### Alerts Not Firing
```bash
# Check alert rules
curl http://localhost:9090/api/v1/rules

# Verify Alertmanager config
curl http://localhost:9093/api/v1/status

# Test notification channels
kubectl logs -f deployment/alertmanager-deployment -n tradewise-ai
```

#### Missing Metrics
```bash
# Check metric exposition
curl http://localhost:5000/api/performance/stats

# Verify scrape targets
curl http://localhost:9090/api/v1/targets

# Review ServiceMonitor
kubectl get servicemonitor -n tradewise-ai -o yaml
```

### Performance Optimization

#### Prometheus Storage
```bash
# Monitor storage usage
kubectl exec prometheus-deployment-xxx -- df -h /prometheus

# Adjust retention period
--storage.tsdb.retention.time=15d

# Configure compaction
--storage.tsdb.retention.size=50GB
```

#### Query Optimization
```prometheus
# Use recording rules for expensive queries
groups:
- name: tradewise.recording
  rules:
  - record: tradewise:request_rate_5m
    expr: rate(flask_request_total[5m])
  
  - record: tradewise:error_rate_5m
    expr: rate(flask_request_exceptions_total[5m]) / rate(flask_request_total[5m])
```

---

## BEST PRACTICES

### Metric Design

#### Naming Conventions
- **Prefix**: `tradewise_` for all custom metrics
- **Units**: Include units in metric names (`_seconds`, `_bytes`, `_total`)
- **Labels**: Use consistent label names across metrics
- **Cardinality**: Limit label values to prevent metric explosion

#### Label Strategy
```python
# Good: Low cardinality
request_total.labels(method='GET', status='200', endpoint='/api/stock-analysis')

# Bad: High cardinality
request_total.labels(user_id='12345', session_id='abcdef', timestamp='...')
```

### Dashboard Design

#### Visual Hierarchy
1. **Overview panels**: Key SLIs at the top
2. **Drill-down panels**: Detailed metrics below
3. **Contextual information**: Logs and events at bottom
4. **Consistent time ranges**: Align all panels to same time window

#### Color Coding
- **Green**: Healthy/good performance
- **Yellow**: Warning thresholds
- **Red**: Critical issues
- **Blue**: Informational metrics

### Alert Design

#### Alert Fatigue Prevention
- **Meaningful thresholds**: Based on actual impact
- **Proper grouping**: Avoid duplicate notifications
- **Escalation policies**: Different severity levels
- **Runbook links**: Include troubleshooting steps

#### SLI-Based Alerting
```yaml
# Error rate SLI
- alert: ErrorRateSLI
  expr: tradewise:error_rate_5m > 0.01  # 1% error budget
  
# Latency SLI  
- alert: LatencySLI
  expr: tradewise:response_time_p99 > 0.5  # 500ms SLO
```

---

## RUNBOOK REFERENCES

### API Issues
- **High Latency**: `/runbooks/api-high-latency.md`
- **High Error Rate**: `/runbooks/api-high-error-rate.md`
- **Memory Leaks**: `/runbooks/api-memory-issues.md`

### Infrastructure Issues
- **Database Down**: `/runbooks/database-recovery.md`
- **Redis Issues**: `/runbooks/cache-troubleshooting.md`
- **Pod Crashes**: `/runbooks/pod-debugging.md`

### Performance Issues
- **Queue Backlog**: `/runbooks/worker-scaling.md`
- **Cache Performance**: `/runbooks/cache-optimization.md`
- **Resource Exhaustion**: `/runbooks/resource-scaling.md`

---

## MONITORING CHECKLIST

### Daily Operations
- [ ] Check critical alert status
- [ ] Review performance dashboard trends
- [ ] Verify backup completion
- [ ] Monitor error rate patterns

### Weekly Reviews
- [ ] Analyze performance trends
- [ ] Review alert effectiveness
- [ ] Update capacity planning
- [ ] Test alert notification channels

### Monthly Tasks
- [ ] Optimize dashboard layouts
- [ ] Review metric retention policies
- [ ] Update alerting thresholds
- [ ] Document new runbooks

---

**Document Version**: 1.0  
**Last Updated**: July 25, 2025  
**Next Review**: August 25, 2025

---

**OBSERVABILITY COMPLETE** ✅  
TradeWise AI now has comprehensive monitoring with Prometheus metrics collection, Grafana visualization dashboards, and Alertmanager notifications for proactive issue detection and resolution.