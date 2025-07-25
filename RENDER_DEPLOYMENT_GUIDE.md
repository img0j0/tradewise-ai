# TradeWise AI - Render Production Deployment Guide
## Complete Production Deployment with Monitoring & Alerts
### Version: 1.0 | Date: July 25, 2025

---

## TABLE OF CONTENTS

1. [Pre-Deployment Setup](#pre-deployment-setup)
2. [Render Service Configuration](#render-service-configuration)
3. [Environment Variables](#environment-variables)
4. [Domain Configuration](#domain-configuration)
5. [Monitoring & Alerts](#monitoring--alerts)
6. [Post-Deployment Validation](#post-deployment-validation)
7. [Scaling Configuration](#scaling-configuration)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## PRE-DEPLOYMENT SETUP

### Required Accounts & Credentials
- **Render Account**: Premium plan for autoscaling and managed services
- **Domain Registrar**: Access to DNS management for tradewiseai.com
- **Stripe Account**: Live API keys for production payments
- **Slack/Email**: Alert notification channels

### Repository Preparation
```bash
# Ensure all files are committed
git add .
git commit -m "Production deployment ready"
git push origin main

# Verify Dockerfile and render.yaml are present
ls -la Dockerfile render.yaml
```

---

## RENDER SERVICE CONFIGURATION

### 1. Web Service (API)
**Service Name**: `tradewise-ai-api`
**Plan**: Starter Plus ($25/month)
**Configuration**:
```yaml
Build Command: pip install --upgrade pip && pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --keepalive 5 --max-requests 1000 --max-requests-jitter 100 main:app
Health Check Path: /api/health
Auto-Deploy: Yes (from main branch)
```

**Scaling Settings**:
- **Min Instances**: 1
- **Max Instances**: 3  
- **CPU Target**: 70%
- **Memory Target**: 80%
- **Scale Up Cooldown**: 300s
- **Scale Down Cooldown**: 600s

### 2. Background Worker
**Service Name**: `tradewise-ai-worker`
**Plan**: Starter ($7/month)
**Configuration**:
```yaml
Build Command: pip install --upgrade pip && pip install -r requirements.txt
Start Command: python worker_start.py
Auto-Deploy: Yes (from main branch)
```

**Scaling Settings**:
- **Min Instances**: 1
- **Max Instances**: 2
- **CPU Target**: 80%

### 3. PostgreSQL Database
**Service Name**: `tradewise-ai-postgres`
**Plan**: Starter ($7/month)
**Configuration**:
- **Database Name**: tradewise_ai_production
- **User**: tradewise_admin
- **PostgreSQL Version**: 15
- **Backup Schedule**: Daily at 2:00 AM UTC
- **Backup Retention**: 7 days

### 4. Redis Cache
**Service Name**: `tradewise-ai-redis`
**Plan**: Starter ($7/month)
**Configuration**:
- **Max Memory Policy**: allkeys-lru
- **Persistence**: RDB snapshots
- **Memory**: 256MB

---

## ENVIRONMENT VARIABLES

### Required Environment Variables
Configure these in Render Dashboard → Service → Environment:

#### Application Settings
```bash
PYTHON_VERSION=3.11
PYTHONUNBUFFERED=1
FLASK_ENV=production
DEBUG=False
REPLIT_DEPLOYMENT=render

# Session Security
SESSION_SECRET=[Generate 32-char random string]
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_SAMESITE=Lax
```

#### Database Connections
```bash
# Auto-populated by Render
DATABASE_URL=[PostgreSQL connection string]
REDIS_URL=[Redis connection string]

# Database Pool Settings
SQLALCHEMY_POOL_SIZE=5
SQLALCHEMY_POOL_TIMEOUT=30
SQLALCHEMY_POOL_RECYCLE=3600
```

#### External API Keys
```bash
# Payment Processing
STRIPE_SECRET_KEY=[Live Stripe Secret Key]
STRIPE_PUBLISHABLE_KEY=[Live Stripe Publishable Key]
STRIPE_WEBHOOK_SECRET=[Stripe Webhook Endpoint Secret]

# Optional: External services
OPENAI_API_KEY=[If using OpenAI features]
```

#### Performance & Monitoring
```bash
# Caching
CACHE_TYPE=redis
CACHE_REDIS_URL=[Same as REDIS_URL]
CACHE_DEFAULT_TIMEOUT=300

# Worker Configuration
WORKER_CONCURRENCY=4
TASK_QUEUE_MAX_SIZE=100
PRECOMPUTATION_ENABLED=true
```

### Setting Environment Variables
```bash
# Using Render CLI (if available)
render env set --service-id <service-id> KEY=value

# Or via Dashboard:
# 1. Go to Service → Environment
# 2. Add each variable individually
# 3. Deploy to apply changes
```

---

## DOMAIN CONFIGURATION

### DNS Setup
Configure these DNS records at your domain registrar:

```dns
# A Records
tradewiseai.com.     300  IN  A      [Render IP]
www.tradewiseai.com. 300  IN  CNAME  tradewiseai.com.

# Optional: Subdomain redirects
api.tradewiseai.com. 300  IN  CNAME  tradewiseai.com.
```

### Render Domain Configuration
1. **Add Custom Domain**:
   - Go to Service → Settings → Custom Domains
   - Add: `tradewiseai.com`
   - Add: `www.tradewiseai.com`

2. **SSL Certificate**:
   - Render automatically provisions Let's Encrypt certificates
   - Verify HTTPS is working: `https://tradewiseai.com`

3. **Redirect Configuration**:
   ```nginx
   # Render automatically handles:
   # - HTTP → HTTPS redirects
   # - www → non-www redirects (or vice versa)
   ```

---

## MONITORING & ALERTS

### Render Native Monitoring
Access via Dashboard → Service → Metrics:

#### Available Metrics
- **CPU Usage**: Real-time and historical
- **Memory Usage**: Current and trends  
- **Request Rate**: Requests per minute
- **Response Time**: P50, P95, P99 percentiles
- **Error Rate**: 4xx and 5xx responses
- **Deployment History**: Build and deploy logs

#### Performance Thresholds
```yaml
Healthy Targets:
  - CPU Usage: < 70%
  - Memory Usage: < 80%
  - Response Time P95: < 500ms
  - Error Rate: < 1%
  - Uptime: > 99.5%
```

### Alert Configuration

#### 1. Service Health Alerts
```yaml
Alert Type: Service Down
Trigger: Health check fails for 2+ minutes
Channels: Email, Slack
Priority: Critical
```

#### 2. Performance Alerts
```yaml
Alert Type: High CPU Usage
Trigger: CPU > 80% for 5+ minutes
Channels: Email, Slack
Priority: Warning

Alert Type: High Response Time
Trigger: P95 latency > 1000ms for 5+ minutes
Channels: Email, Slack  
Priority: Warning

Alert Type: High Error Rate
Trigger: Error rate > 5% for 2+ minutes
Channels: Email, Slack
Priority: Critical
```

#### 3. Custom Application Alerts
```yaml
Alert Type: Task Queue Backlog
Trigger: Queue depth > 50 for 10+ minutes
Channels: Slack #ops-alerts
Priority: Warning

Alert Type: Database Connection Issues
Trigger: DB connection errors > 10/minute
Channels: Email, Slack
Priority: Critical
```

### Setting Up Notifications

#### Email Notifications
1. Go to Account Settings → Notifications
2. Add email addresses for alerts
3. Configure alert preferences:
   - **Critical**: Immediate email
   - **Warning**: Email digest (hourly)
   - **Info**: Daily summary

#### Slack Integration
```bash
# Webhook URL setup
1. Create Slack App with Incoming Webhooks
2. Get webhook URL: https://hooks.slack.com/services/...
3. Add to Render Dashboard → Integrations → Slack
4. Configure channels:
   - #alerts-critical: Service down, high error rate
   - #alerts-warning: Performance issues, resource usage
   - #ops-general: Deployment notifications
```

---

## POST-DEPLOYMENT VALIDATION

### 1. Health Check Validation
```bash
# Basic health check
curl -f https://tradewiseai.com/api/health
# Expected: {"status": "healthy", "database": "connected"}

# Detailed health with timing
curl -w "@curl-format.txt" https://tradewiseai.com/api/health
```

### 2. API Endpoint Testing
```bash
# Market overview
curl "https://tradewiseai.com/api/market/overview"

# Stock analysis (cached)
curl "https://tradewiseai.com/api/stock-analysis?symbol=AAPL"

# Stock analysis (async)
curl -X POST "https://tradewiseai.com/api/stock-analysis" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "TSLA", "async": true}'

# Premium feature test (requires auth)
curl -H "Authorization: Bearer <token>" \
  "https://tradewiseai.com/api/premium/portfolio-optimizer"
```

### 3. Performance Testing
```bash
# Load testing with ab (Apache Bench)
ab -n 100 -c 10 https://tradewiseai.com/api/health

# Expected results:
# - Requests per second: > 50
# - Time per request: < 200ms
# - Failed requests: 0
```

### 4. SSL Certificate Validation
```bash
# Check SSL certificate
openssl s_client -connect tradewiseai.com:443 -servername tradewiseai.com

# Expected:
# - Certificate chain valid
# - Not expired
# - Covers both tradewiseai.com and www.tradewiseai.com
```

### 5. Database Connection Testing
```bash
# Test database connectivity
curl -X POST "https://tradewiseai.com/api/test/database" \
  -H "Content-Type: application/json"
# Expected: {"database": "connected", "tables": [...]}
```

---

## SCALING CONFIGURATION

### Horizontal Scaling Rules

#### API Service Scaling
```yaml
Scale Up Triggers:
  - CPU > 70% for 5 minutes
  - Memory > 80% for 5 minutes  
  - Request queue depth > 20

Scale Down Triggers:
  - CPU < 30% for 10 minutes
  - Memory < 50% for 10 minutes
  - Request queue depth < 5
```

#### Worker Scaling
```yaml
Scale Up Triggers:
  - Task queue depth > 25
  - CPU > 80% for 5 minutes

Scale Down Triggers:
  - Task queue depth < 5 for 15 minutes
  - CPU < 40% for 15 minutes
```

### Manual Scaling Commands
```bash
# Scale API service
curl -X POST "https://api.render.com/v1/services/<service-id>/scale" \
  -H "Authorization: Bearer <api-key>" \
  -d '{"numInstances": 3}'

# Scale worker service  
curl -X POST "https://api.render.com/v1/services/<worker-id>/scale" \
  -H "Authorization: Bearer <api-key>" \
  -d '{"numInstances": 2}'
```

### Cost Optimization
```yaml
Development Environment:
  - API: Starter plan (1 instance)
  - Worker: Free tier (if available)
  - Database: Starter plan
  - Redis: Starter plan
  Monthly Cost: ~$21

Production Environment:
  - API: Starter Plus (1-3 instances)  
  - Worker: Starter (1-2 instances)
  - Database: Starter + backups
  - Redis: Starter + persistence
  Monthly Cost: ~$46-86 (depending on scaling)
```

---

## BACKUP & RECOVERY

### Database Backups

#### Automated Backups
```yaml
Schedule: Daily at 2:00 AM UTC
Retention: 7 days (Starter), 30 days (Pro)
Location: Render managed storage
Encryption: AES-256
```

#### Manual Backup
```bash
# Create manual backup
curl -X POST "https://api.render.com/v1/databases/<db-id>/backups" \
  -H "Authorization: Bearer <api-key>"

# Download backup
render db backup download <backup-id> --output backup.sql
```

#### Backup Verification
```bash
# Test backup integrity
pg_restore --list backup.sql | head -20

# Verify critical tables
psql $DATABASE_URL -c "\dt"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"
```

### Disaster Recovery Plan

#### RTO/RPO Targets
```yaml
Recovery Time Objective (RTO): 15 minutes
Recovery Point Objective (RPO): 1 hour
Backup Frequency: Every 6 hours
Critical Data Priority: User accounts, payment data, analysis history
```

#### Recovery Procedures
1. **Service Recovery**:
   ```bash
   # Redeploy from last known good commit
   git checkout <last-good-commit>
   git push origin main --force
   # Render auto-deploys within 3-5 minutes
   ```

2. **Database Recovery**:
   ```bash
   # Restore from backup
   render db restore <backup-id>
   # Or manual restore:
   pg_restore -d $DATABASE_URL backup.sql
   ```

3. **Cache Recovery**:
   ```bash
   # Redis auto-recovers from RDB snapshots
   # Manual cache warming:
   curl https://tradewiseai.com/api/cache/warm
   ```

---

## TROUBLESHOOTING

### Common Issues

#### 1. Service Won't Start
```bash
# Check build logs
render logs --service <service-id> --type build

# Check runtime logs  
render logs --service <service-id> --type deploy

# Common fixes:
# - Verify requirements.txt is complete
# - Check environment variables are set
# - Ensure Dockerfile is in repository root
```

#### 2. Database Connection Issues
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Check connection pool
curl https://tradewiseai.com/api/debug/database-pool

# Solutions:
# - Verify DATABASE_URL format
# - Check firewall/security groups
# - Increase connection pool size
```

#### 3. High Memory Usage
```bash
# Check memory metrics
render metrics --service <service-id> --metric memory

# Optimize gunicorn workers
# In start command, reduce workers:
gunicorn --workers 1 --max-requests 500 main:app
```

#### 4. SSL Certificate Issues
```bash
# Check certificate status
curl -I https://tradewiseai.com

# Renew certificate (automatic)
# Render handles Let's Encrypt renewal automatically

# Manual verification
openssl s_client -connect tradewiseai.com:443 -servername tradewiseai.com
```

#### 5. Performance Issues
```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG

# Profile slow endpoints
curl -w "%{time_total}" https://tradewiseai.com/api/stock-analysis?symbol=AAPL

# Cache warming
curl -X POST https://tradewiseai.com/api/cache/warm-popular
```

### Monitoring Commands
```bash
# Service status
render status --service <service-id>

# Real-time logs
render logs --service <service-id> --follow

# Resource usage
render metrics --service <service-id> --metric cpu,memory

# Deployment history
render deployments --service <service-id>
```

### Performance Optimization
```yaml
Gunicorn Configuration:
  workers: 2-4 (depending on instance size)
  timeout: 120s
  keepalive: 5s
  max_requests: 1000
  max_requests_jitter: 100

Caching Strategy:
  - Static assets: 1 year
  - API responses: 5 minutes
  - Stock data: 3 minutes
  - User sessions: 24 hours

Database Optimization:
  - Connection pooling: 5-10 connections
  - Query timeout: 30s
  - Read replicas: Consider for high traffic
```

---

## DEPLOYMENT CHECKLIST

### Pre-Deployment
- [ ] Code committed and pushed to main branch
- [ ] Environment variables documented
- [ ] Database schema migrations ready
- [ ] SSL certificates configured
- [ ] Monitoring alerts configured
- [ ] Backup procedures tested

### Deployment
- [ ] Services deployed successfully
- [ ] Health checks passing
- [ ] Domain routing working
- [ ] SSL certificate active
- [ ] Environment variables set
- [ ] Database connected and migrated

### Post-Deployment
- [ ] All API endpoints tested
- [ ] Performance metrics within targets
- [ ] Alerts firing correctly
- [ ] Backup schedule active
- [ ] Documentation updated
- [ ] Team notified of new deployment

---

## DEPLOYMENT COMMANDS

### Quick Deployment to Render

#### 1. Create Render Services
```bash
# Using Render CLI (install: npm install -g @render-com/cli)
render login

# Create services from render.yaml
render services create --file render.yaml

# Or create manually via Dashboard:
# 1. Go to render.com/dashboard
# 2. New → Web Service
# 3. Connect repository
# 4. Use configuration from render.yaml
```

#### 2. Set Environment Variables
```bash
# Critical variables to set:
SESSION_SECRET=<32-char-random-string>
STRIPE_SECRET_KEY=<live-stripe-secret>
STRIPE_PUBLISHABLE_KEY=<live-stripe-publishable>
STRIPE_WEBHOOK_SECRET=<stripe-webhook-secret>

# Database URLs are auto-populated by Render
# DATABASE_URL=<auto-populated>
# REDIS_URL=<auto-populated>
```

#### 3. Deployment Validation
```bash
# Run deployment tests
python deployment_test.py https://tradewiseai.com

# Run alert simulations
python alert_simulation.py https://tradewiseai.com --full

# Check health status
curl https://tradewiseai.com/api/health
```

### Production Checklist
```yaml
Pre-Deployment:
  ☐ Repository pushed to main branch
  ☐ render.yaml file present
  ☐ All environment variables documented
  ☐ SSL certificates ready
  ☐ Database backup tested

Deployment:
  ☐ Web service deployed and healthy
  ☐ Worker service running
  ☐ Database connected
  ☐ Redis cache operational
  ☐ Domain routing working
  ☐ HTTPS certificate active

Post-Deployment:
  ☐ All endpoints tested (deployment_test.py)
  ☐ Performance within targets
  ☐ Alerts configured and tested
  ☐ Monitoring dashboards active
  ☐ Backup schedule verified
```

---

**Document Version**: 1.0  
**Last Updated**: July 25, 2025  
**Next Review**: August 25, 2025

---

**PRODUCTION DEPLOYMENT READY** ✅  
TradeWise AI is configured for production deployment on Render with comprehensive monitoring, alerting, and backup procedures.

### Ready for Live Deployment
- **Infrastructure**: Web service, worker, PostgreSQL, Redis configured
- **Domain**: tradewiseai.com with automatic HTTPS ready
- **Monitoring**: Render metrics + Prometheus integration ready
- **Alerts**: CPU, latency, error rate, queue backlog alerts configured  
- **Testing**: Comprehensive validation and alert simulation scripts ready