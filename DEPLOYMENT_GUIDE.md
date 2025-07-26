# TradeWise AI - Render Deployment Guide 🚀

## Prerequisites
- GitHub account
- Render account (free tier available)
- Stripe account (for payments)
- Email service credentials (Gmail/SendGrid)

## Step 1: GitHub Repository Setup

### 1.1 Create New Repository
```bash
# On GitHub, create a new repository named "tradewise-ai"
# Make it public or private (your choice)
```

### 1.2 Push Your Code
```bash
# Initialize git in your project directory
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit - TradeWise AI complete platform"

# Add remote origin (replace with your GitHub URL)
git remote add origin https://github.com/YOUR_USERNAME/tradewise-ai.git

# Push to GitHub
git push -u origin main
```

## Step 2: Render Deployment

### 2.1 Connect GitHub to Render
1. Go to [render.com](https://render.com)
2. Sign up/login with GitHub
3. Click "New +" → "Blueprint"
4. Connect your GitHub repository
5. Select `tradewise-ai` repository

### 2.2 Configure Environment Variables
Set these environment variables in Render dashboard:

#### Required Secrets
```bash
# Stripe (Required for payments)
STRIPE_SECRET_KEY=sk_live_... # Your Stripe secret key

# Email Notifications (Optional but recommended)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Gmail app password
```

#### Auto-Generated (Render will create these)
```bash
SESSION_SECRET=auto-generated
DATABASE_URL=auto-generated
REDIS_URL=auto-generated
```

## Step 3: Domain Configuration (Optional)

### 3.1 Custom Domain
```bash
# In Render dashboard:
# 1. Go to your web service settings
# 2. Add custom domain: tradewise.ai or your domain
# 3. Configure DNS records as shown
```

### 3.2 SSL Certificate
- Render automatically provides SSL certificates
- Your site will be available at `https://your-app.onrender.com`

## Step 4: Post-Deployment Setup

### 4.1 Verify Deployment
```bash
# Check these URLs after deployment:
https://your-app.onrender.com/              # Main dashboard
https://your-app.onrender.com/api/health    # Health check
https://your-app.onrender.com/admin/dashboard # Admin monitoring
```

### 4.2 Test Core Features
1. **User Registration/Login**: Test OAuth flows
2. **Stock Search**: Verify API connections
3. **Premium Checkout**: Test Stripe integration
4. **Admin Dashboard**: Check monitoring system
5. **Email Alerts**: Test notification system

## Step 5: Production Configuration

### 5.1 Gmail App Password Setup
```bash
# For SMTP notifications:
# 1. Go to Google Account settings
# 2. Enable 2-Factor Authentication
# 3. Generate App Password for "Mail"
# 4. Use this password for SMTP_PASSWORD
```

### 5.2 Stripe Configuration
```bash
# 1. Get your Stripe secret key from dashboard
# 2. Configure webhook endpoints:
#    - https://your-app.onrender.com/subscription/webhook
# 3. Test payment flows
```

### 5.3 Monitoring Setup
```bash
# Admin dashboard available at:
# https://your-app.onrender.com/admin/dashboard
# 
# Monitor:
# - System health
# - Error rates
# - Performance metrics
# - Alert notifications
```

## Step 6: Environment-Specific Settings

### 6.1 Production Environment Variables
These are automatically set by render.yaml:

```yaml
ENVIRONMENT=production
FLASK_ENV=production
DEBUG=false
ERROR_NOTIFICATIONS_ENABLED=true
PREMIUM_FEATURES_ENABLED=true
ADVANCED_ANALYTICS_ENABLED=true
LOG_LEVEL=INFO
ASYNC_WORKER_COUNT=3
```

### 6.2 Resource Scaling
```bash
# Starter Plan includes:
# - Web service: 512MB RAM, shared CPU
# - Worker service: 512MB RAM, shared CPU  
# - PostgreSQL: 1GB storage
# - Redis: 25MB memory

# To scale up:
# 1. Go to Render dashboard
# 2. Upgrade service plans as needed
# 3. Increase worker count in environment variables
```

## Step 7: Monitoring & Maintenance

### 7.1 Health Monitoring
- **Automatic Health Checks**: Render monitors `/api/health`
- **Admin Dashboard**: Real-time system metrics
- **Email Alerts**: Critical system notifications
- **Performance Tracking**: Built-in monitoring system

### 7.2 Log Management
```bash
# View logs in Render dashboard:
# 1. Select your service
# 2. Go to "Logs" tab
# 3. Filter by service (web/worker)

# Log levels:
# - INFO: General information
# - WARNING: Non-critical issues
# - ERROR: Application errors
# - CRITICAL: System failures
```

### 7.3 Database Backups
```bash
# Render automatically backs up PostgreSQL
# - Daily backups for 7 days (Starter plan)
# - Point-in-time recovery available
# - Manual backups via dashboard
```

## Step 8: Troubleshooting

### 8.1 Common Issues
```bash
# Build failures:
# - Check requirements.txt syntax
# - Verify Python version compatibility
# - Check for missing dependencies

# Runtime errors:
# - Check environment variables
# - Verify database connections
# - Review application logs

# Performance issues:
# - Monitor resource usage
# - Check admin dashboard
# - Review error rates
```

### 8.2 Support Resources
- **Admin Dashboard**: Real-time system status
- **Render Logs**: Detailed error information  
- **Health Endpoints**: API status checks
- **Contact**: tradewise.founder@gmail.com

## Step 9: Success Checklist ✅

After deployment, verify these work:

- [ ] Main dashboard loads at your domain
- [ ] User authentication (OAuth) working
- [ ] Stock search and analysis functional
- [ ] Premium subscription checkout working
- [ ] Email notifications sending
- [ ] Admin monitoring dashboard accessible
- [ ] Background worker processing tasks
- [ ] Database connections stable
- [ ] Redis caching operational
- [ ] SSL certificate active

## Step 10: Launch Preparation

### 10.1 Final Testing
```bash
# Complete user journey test:
# 1. Sign up new account
# 2. Search and analyze stocks
# 3. Subscribe to premium plan
# 4. Test all premium features
# 5. Verify admin monitoring
```

### 10.2 Go Live
```bash
# Your TradeWise AI platform is now live at:
# https://your-domain.onrender.com
# 
# Features available:
# ✅ Stock analysis and AI insights
# ✅ Premium subscription tiers
# ✅ Real-time market data
# ✅ Admin monitoring and alerts
# ✅ Mobile-responsive design
# ✅ Production security
```

---

## Files Created for Deployment

1. **`render.yaml`** - Render deployment configuration
2. **`worker_start.py`** - Background worker startup script
3. **`.gitignore`** - Git ignore patterns
4. **`DEPLOYMENT_GUIDE.md`** - This deployment guide

## Auto-Configured Services

- **Web Service**: Main Flask application
- **Worker Service**: Background task processing
- **PostgreSQL**: Primary database
- **Redis**: Caching and task queue

## Contact & Support

- **Email**: tradewise.founder@gmail.com
- **Phone**: 631-810-9473
- **Admin Dashboard**: `/admin/dashboard`

---

**🚀 Your TradeWise AI platform is ready for production deployment!**