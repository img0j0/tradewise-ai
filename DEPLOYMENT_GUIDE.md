# TradeWise AI - Production Deployment Guide
## Comprehensive Production Deployment and Maintenance Documentation
### Version: 1.0 | Date: July 25, 2025

---

## TABLE OF CONTENTS

1. [Environment Setup](#environment-setup)
2. [Security Configuration](#security-configuration)
3. [Database Management](#database-management)
4. [Deployment Process](#deployment-process)
5. [Monitoring & Maintenance](#monitoring--maintenance)
6. [Backup & Recovery](#backup--recovery)
7. [Security Hardening](#security-hardening)
8. [Troubleshooting](#troubleshooting)

---

## ENVIRONMENT SETUP

### Required Environment Variables

#### Production Required Variables
```bash
# Core Application
SESSION_SECRET=your-super-secure-session-secret-here
DATABASE_URL=postgresql://user:password@host:port/database

# Payment Processing
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key_here

# Optional Production Variables
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-app-password
MAIL_PORT=587

# System Variables (Auto-configured)
REPLIT_DEPLOYMENT=1  # Auto-set by Replit
REPLIT_DEV_DOMAIN=your-app.replit.app  # Auto-set by Replit
```

#### Development Variables
```bash
# Development minimal setup
SESSION_SECRET=dev-secret-key-change-for-production
DATABASE_URL=sqlite:///trading_platform.db  # Optional, defaults to SQLite
STRIPE_SECRET_KEY=sk_test_your_test_key_here  # Optional for testing
```

### Environment Variable Descriptions

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SESSION_SECRET` | Yes | Flask session encryption key (32+ random chars) | `abc123def456...` |
| `DATABASE_URL` | Yes* | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `STRIPE_SECRET_KEY` | Yes* | Stripe API secret key for payments | `sk_live_...` or `sk_test_...` |
| `MAIL_SERVER` | No | SMTP server for email notifications | `smtp.gmail.com` |
| `MAIL_USERNAME` | No | Email account username | `app@company.com` |
| `MAIL_PASSWORD` | No | Email account password/app password | `app-specific-password` |
| `REPLIT_DEPLOYMENT` | Auto | Production flag (auto-set by Replit) | `1` |

*Required for production, optional for development

---

## SECURITY CONFIGURATION

### Production Security Features

#### HTTPS Enforcement
- **Force HTTPS**: All HTTP requests redirected to HTTPS in production
- **HSTS Headers**: Strict-Transport-Security with 1-year max-age
- **Secure Cookies**: Session cookies only sent over HTTPS

#### Session Security
```python
# Production session configuration
SESSION_COOKIE_SECURE = True      # HTTPS only
SESSION_COOKIE_HTTPONLY = True    # Prevent XSS
SESSION_COOKIE_SAMESITE = 'Strict' # CSRF protection
PERMANENT_SESSION_LIFETIME = 8 hours
```

#### Security Headers
- **Content Security Policy**: Restricts resource loading
- **X-Frame-Options**: Prevents clickjacking
- **X-Content-Type-Options**: Prevents MIME sniffing
- **X-XSS-Protection**: Browser XSS protection
- **Referrer-Policy**: Controls referrer information

#### Input Validation
- **Rate Limiting**: 30 requests per minute per endpoint
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **XSS Prevention**: Jinja2 auto-escaping enabled
- **CSRF Protection**: WTF-CSRF tokens enabled

---

## DATABASE MANAGEMENT

### Database Setup

#### PostgreSQL Production Setup
```bash
# Example DATABASE_URL format
DATABASE_URL="postgresql://username:password@hostname:port/database_name"

# Replit PostgreSQL example
DATABASE_URL="postgresql://user:pass@db.replit.com:5432/tradewise_prod"
```

#### Connection Pool Settings
```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_recycle': 300,      # Recycle connections every 5 minutes
    'pool_pre_ping': True,    # Validate connections before use
    'pool_size': 10,          # Base connection pool size
    'max_overflow': 20,       # Additional connections if needed
    'echo': False             # Disable SQL logging in production
}
```

### Database Migrations

#### Running Migrations
```bash
# Manual schema updates (if needed)
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Or using Flask-Migrate (recommended for production)
flask db init     # Initialize migrations (first time only)
flask db migrate  # Create migration script
flask db upgrade  # Apply migrations
```

#### Schema Validation
```python
# Verify all tables exist
from app import app, db
from models import User, StockAnalysis, FavoriteStock, SearchHistory

with app.app_context():
    db.create_all()
    print("✅ All database tables created/verified")
```

---

## DEPLOYMENT PROCESS

### Pre-Deployment Checklist

- [ ] All environment variables configured in Replit Secrets
- [ ] Database connection tested and working
- [ ] Stripe integration tested with live keys
- [ ] Security headers verified in production
- [ ] Performance optimization services enabled
- [ ] Backup system configured and tested
- [ ] SSL certificate active and valid

### Replit Deployment Steps

#### 1. Environment Configuration
```bash
# In Replit Secrets Manager, add:
SESSION_SECRET=your-32-character-random-string
DATABASE_URL=your-postgresql-connection-string
STRIPE_SECRET_KEY=your-live-stripe-secret-key
```

#### 2. Database Initialization
```bash
# Run once during initial deployment
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database initialized')
"
```

#### 3. Application Startup
```bash
# Production startup command (in .replit)
run = "gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app"
```

#### 4. Post-Deployment Verification
```bash
# Health check
curl https://your-app.replit.app/api/health

# Performance stats
curl https://your-app.replit.app/api/performance/stats

# Task queue status
curl https://your-app.replit.app/api/task-queue/stats
```

### Deployment Validation

#### Functional Tests
```bash
# Test core endpoints
curl -X POST https://your-app.replit.app/api/stock-analysis \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL"}'

# Test async processing
curl -X POST https://your-app.replit.app/api/stock-analysis?async=true \
  -H "Content-Type: application/json" \
  -d '{"symbol": "TSLA"}'

# Test payment flow (with test card)
curl -X POST https://your-app.replit.app/create-checkout-session \
  -H "Content-Type: application/json"
```

#### Security Tests
```bash
# Verify HTTPS redirect
curl -I http://your-app.replit.app/

# Check security headers
curl -I https://your-app.replit.app/

# Verify rate limiting
for i in {1..35}; do curl https://your-app.replit.app/api/health; done
```

---

## MONITORING & MAINTENANCE

### Performance Monitoring

#### Real-time Metrics
- **Response Times**: `/api/performance/stats`
- **Cache Performance**: Hit/miss ratios tracked
- **Queue Health**: `/api/task-queue/stats`
- **Database Performance**: Query timing logged

#### Log Monitoring
```bash
# Monitor application logs
tail -f performance.log

# Check for errors
grep "ERROR" performance.log | tail -20

# Monitor slow requests
grep "slow_request.*true" performance.log
```

#### Key Performance Indicators
- **Target Response Times**: <500ms for stock analysis
- **Cache Hit Ratio**: >70% for frequently accessed data
- **Error Rate**: <1% across all endpoints
- **Queue Processing**: <3 seconds average task completion

### Health Monitoring

#### Automated Health Checks
```bash
# Add to cron or monitoring service
#!/bin/bash
# health_check.sh

ENDPOINT="https://your-app.replit.app/api/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $ENDPOINT)

if [ $RESPONSE -eq 200 ]; then
    echo "✅ Application healthy"
else
    echo "❌ Application unhealthy - HTTP $RESPONSE"
    # Send alert notification
fi
```

#### Service Monitoring
```python
# Monitor optimization services
import requests

def check_services():
    try:
        response = requests.get('https://your-app.replit.app/api/task-queue/stats')
        data = response.json()
        
        # Check task queue health
        if not data['task_queue']['queue_running']:
            alert("Task queue not running")
        
        # Check precomputation service
        if not data['precomputation_service']['service_running']:
            alert("Precomputation service not running")
            
    except Exception as e:
        alert(f"Service check failed: {e}")
```

---

## BACKUP & RECOVERY

### Automated Database Backups

#### Daily Backup Script
```bash
# Add to cron: 0 2 * * * /path/to/backup_daily.sh
#!/bin/bash
# backup_daily.sh

cd /path/to/tradewise-ai
python database_backup.py backup --description "Daily automated backup"

# Clean up old backups (keep 30 days)
python database_backup.py cleanup

echo "✅ Daily backup completed: $(date)"
```

#### Manual Backup Commands
```bash
# Create immediate backup
python database_backup.py backup --description "Pre-deployment backup"

# List all backups
python database_backup.py list

# Restore from backup
python database_backup.py restore backups/tradewise_backup_20250725_120000.sql.gz
```

### Backup Storage Recommendations

#### Local Backup Strategy
- **Retention**: 30 days of daily backups
- **Location**: `./backups/` directory
- **Format**: Compressed SQL dumps with metadata
- **Automation**: Daily cron job with cleanup

#### Remote Backup Strategy (Recommended)
```bash
# Upload to cloud storage (example with AWS S3)
aws s3 sync ./backups/ s3://your-backup-bucket/tradewise-ai/ \
  --exclude "*.tmp" --delete

# Or Google Cloud Storage
gsutil -m rsync -r -d ./backups/ gs://your-backup-bucket/tradewise-ai/
```

### Disaster Recovery Procedures

#### Complete System Recovery
1. **Deploy fresh application** on new infrastructure
2. **Configure environment variables** from secure backup
3. **Restore database** from latest backup
4. **Verify application functionality** with health checks
5. **Update DNS** to point to new deployment

#### Database Recovery
```bash
# Emergency database restore
python database_backup.py restore path/to/backup.sql.gz

# Verify data integrity
python -c "
from app import app, db
from models import User, StockAnalysis
with app.app_context():
    user_count = User.query.count()
    analysis_count = StockAnalysis.query.count()
    print(f'Restored: {user_count} users, {analysis_count} analyses')
"
```

---

## SECURITY HARDENING

### Security Best Practices

#### Secret Management
- **Never commit secrets** to version control
- **Use environment variables** for all sensitive data
- **Rotate secrets regularly** (monthly for production)
- **Monitor secret access** and usage

#### API Security
```python
# Rate limiting configuration
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "30 per minute"]
)
```

#### Input Validation
```python
# Example secure input handling
from marshmallow import Schema, fields, validate

class StockAnalysisSchema(Schema):
    symbol = fields.Str(required=True, validate=validate.Regexp(r'^[A-Z]{1,5}$'))
    strategy = fields.Str(validate=validate.OneOf(['growth', 'value', 'dividend', 'momentum']))
```

### Security Auditing

#### Regular Security Checks
```bash
# Check for vulnerable dependencies
pip-audit

# Scan for security issues
bandit -r . -f json -o security_report.json

# SSL certificate check
echo | openssl s_client -connect your-app.replit.app:443 | openssl x509 -noout -dates
```

#### Security Monitoring
- **Failed login attempts**: Monitor for brute force attacks
- **Unusual traffic patterns**: Rate limiting and anomaly detection
- **SQL injection attempts**: Log and monitor for injection patterns
- **XSS attempts**: Monitor for script injection in user inputs

---

## TROUBLESHOOTING

### Common Issues

#### Application Won't Start
```bash
# Check environment variables
echo $SESSION_SECRET
echo $DATABASE_URL
echo $STRIPE_SECRET_KEY

# Verify database connection
python -c "
import os
print('DATABASE_URL:', os.environ.get('DATABASE_URL', 'Not set'))
"

# Check for missing dependencies
pip install -r requirements.txt
```

#### Database Connection Issues
```bash
# Test database connectivity
python -c "
from sqlalchemy import create_engine
import os
engine = create_engine(os.environ['DATABASE_URL'])
connection = engine.connect()
print('✅ Database connection successful')
connection.close()
"
```

#### Performance Issues
```bash
# Check cache performance
curl https://your-app.replit.app/api/performance/stats | jq '.cache_hit_ratio'

# Monitor slow queries
grep "slow_request.*true" performance.log | tail -10

# Check queue health
curl https://your-app.replit.app/api/task-queue/stats | jq '.task_queue'
```

#### SSL/HTTPS Issues
```bash
# Verify SSL certificate
curl -I https://your-app.replit.app/

# Check HTTPS redirect
curl -I http://your-app.replit.app/

# Test security headers
curl -I https://your-app.replit.app/ | grep -E "(Strict-Transport|X-Frame|X-Content)"
```

### Error Code Reference

| Error Code | Description | Solution |
|------------|-------------|----------|
| 500 | Internal Server Error | Check application logs, verify environment variables |
| 502 | Bad Gateway | Application not responding, check if gunicorn is running |
| 503 | Service Unavailable | Database connection issues, check DATABASE_URL |
| 429 | Too Many Requests | Rate limit exceeded, implement backoff strategy |
| 404 | Not Found | Route not configured, check URL patterns |

### Emergency Procedures

#### Application Down
1. **Check Replit deployment status**
2. **Verify environment variables**
3. **Restart application** from Replit console
4. **Check database connectivity**
5. **Review error logs** for specific issues

#### Database Issues
1. **Check DATABASE_URL** environment variable
2. **Test database connectivity** with manual connection
3. **Restore from backup** if data corruption suspected
4. **Contact database provider** if persistent issues

#### Performance Degradation
1. **Check cache hit ratios** at `/api/performance/stats`
2. **Monitor task queue** at `/api/task-queue/stats`
3. **Restart optimization services** at `/api/precomputation/trigger`
4. **Clear cache** if corruption suspected

---

## MAINTENANCE SCHEDULE

### Daily Tasks
- [ ] Monitor application health and error logs
- [ ] Check backup completion status
- [ ] Review performance metrics
- [ ] Monitor security alerts

### Weekly Tasks
- [ ] Review performance trends and optimization opportunities
- [ ] Check for application updates and security patches
- [ ] Validate backup and restore procedures
- [ ] Review rate limiting and security logs

### Monthly Tasks
- [ ] Rotate security secrets (SESSION_SECRET, API keys)
- [ ] Perform comprehensive security audit
- [ ] Update dependencies and security patches
- [ ] Review and optimize database performance
- [ ] Test disaster recovery procedures

### Quarterly Tasks
- [ ] Complete security penetration testing
- [ ] Review and update security policies
- [ ] Optimize application architecture and scaling
- [ ] Update documentation and runbooks

---

## SUPPORT CONTACTS

### Technical Support
- **Application Issues**: Monitor logs and error tracking
- **Database Issues**: Check DATABASE_URL and connectivity
- **Payment Issues**: Verify Stripe configuration and keys
- **Performance Issues**: Review `/api/performance/stats` endpoint

### Escalation Procedures
1. **Application Down**: Immediate deployment restart and health check
2. **Data Loss**: Activate disaster recovery procedures
3. **Security Breach**: Rotate all secrets, review access logs
4. **Payment Issues**: Contact Stripe support with specific error codes

---

**Document Version**: 1.0  
**Last Updated**: July 25, 2025  
**Next Review**: August 25, 2025

---

**PRODUCTION READY** ✅  
TradeWise AI is now fully configured for secure, scalable production deployment with comprehensive monitoring, backup, and security features.