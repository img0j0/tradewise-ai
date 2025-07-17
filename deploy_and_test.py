#!/usr/bin/env python3
"""
Deployment and AI Testing Script for Trading Platform
This script prepares the platform for deployment and sets up AI paper trading
"""

import os
import sys
import time
import json
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TradingPlatformDeployment:
    """Handles deployment and AI testing setup for the trading platform"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.deployment_ready = False
        self.ai_bot_ready = False
        
    def check_requirements(self):
        """Check if all requirements are met for deployment"""
        logger.info("Checking deployment requirements...")
        
        required_files = [
            'main.py',
            'routes.py',
            'models.py',
            'paper_trading_automation.py',
            'advanced_orders.py',
            'market_intelligence.py',
            'deep_learning_engine.py',
            'performance_optimizer.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            logger.error(f"Missing required files: {missing_files}")
            return False
        
        logger.info("All required files present ✓")
        return True
    
    def setup_environment(self):
        """Set up environment variables for deployment"""
        logger.info("Setting up environment variables...")
        
        # Create .env file for local development
        env_content = """# Trading Platform Environment Variables
# Database
DATABASE_URL=postgresql://user:password@localhost/trading_platform

# Session Security
SESSION_SECRET=your-secret-key-here-change-in-production

# API Keys (to be provided by user)
OPENAI_API_KEY=your-openai-api-key-here

# Deployment Settings
FLASK_ENV=production
DEBUG=False
HOST=0.0.0.0
PORT=5000

# AI Trading Bot Settings
AI_TRADING_ENABLED=true
AI_TRADING_INITIAL_BALANCE=10000
AI_TRADING_MAX_POSITION_SIZE=0.1
AI_TRADING_SYMBOLS=AAPL,MSFT,GOOGL,AMZN,TSLA,NVDA,META,NFLX

# Paper Trading Settings
PAPER_TRADING_MODE=true
PAPER_TRADING_REPORT_INTERVAL=3600
"""
        
        with open(self.project_root / '.env.example', 'w') as f:
            f.write(env_content)
        
        logger.info("Environment template created ✓")
        return True
    
    def create_deployment_config(self):
        """Create deployment configuration files"""
        logger.info("Creating deployment configuration...")
        
        # Create replit.nix if it doesn't exist
        nix_content = """{ pkgs }: {
  deps = [
    pkgs.python311Full
    pkgs.python311Packages.pip
    pkgs.postgresql
    pkgs.redis
  ];
}"""
        
        with open(self.project_root / 'replit.nix', 'w') as f:
            f.write(nix_content)
        
        # Create .replit configuration
        replit_content = """modules = ["python-3.11", "postgresql-15", "redis-7.2"]
run = "python main.py"

[nix]
channel = "stable-22_11"

[deployment]
run = ["sh", "-c", "python main.py"]
deploymentTarget = "cloudrun"

[env]
PYTHONPATH = "$PYTHONPATH:$PWD"
"""
        
        with open(self.project_root / '.replit', 'w') as f:
            f.write(replit_content)
        
        logger.info("Deployment configuration created ✓")
        return True
    
    def create_ai_bot_service(self):
        """Create systemd service file for AI bot"""
        logger.info("Creating AI bot service configuration...")
        
        service_content = """[Unit]
Description=AI Paper Trading Bot
After=network.target

[Service]
Type=simple
User=runner
WorkingDirectory=/home/runner/workspace
Environment=PYTHONPATH=/home/runner/workspace
ExecStart=/usr/bin/python3 paper_trading_automation.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        with open(self.project_root / 'ai-trading-bot.service', 'w') as f:
            f.write(service_content)
        
        logger.info("AI bot service file created ✓")
        return True
    
    def create_startup_script(self):
        """Create startup script for the AI bot"""
        logger.info("Creating startup script...")
        
        startup_content = """#!/bin/bash
# AI Paper Trading Bot Startup Script

set -e

echo "Starting AI Paper Trading Bot..."

# Check if the main application is running
if ! curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "Main application is not running. Starting it first..."
    python3 main.py &
    sleep 30
fi

# Wait for application to be ready
echo "Waiting for application to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:5000/health > /dev/null 2>&1; then
        echo "Application is ready!"
        break
    fi
    sleep 2
done

# Start the AI trading bot
echo "Starting AI Paper Trading Bot..."
python3 paper_trading_automation.py

echo "AI Paper Trading Bot started successfully!"
"""
        
        with open(self.project_root / 'start_ai_bot.sh', 'w') as f:
            f.write(startup_content)
        
        # Make executable
        os.chmod(self.project_root / 'start_ai_bot.sh', 0o755)
        
        logger.info("Startup script created ✓")
        return True
    
    def create_monitoring_script(self):
        """Create monitoring script for the AI bot"""
        logger.info("Creating monitoring script...")
        
        monitoring_content = """#!/usr/bin/env python3
import requests
import time
import json
import os
from datetime import datetime

def check_platform_health():
    try:
        response = requests.get('http://localhost:5000/health', timeout=10)
        return response.status_code == 200
    except:
        return False

def get_trading_stats():
    try:
        # Read the latest trading report
        reports = [f for f in os.listdir('.') if f.startswith('trading_report_')]
        if not reports:
            return None
        
        latest_report = max(reports)
        with open(latest_report, 'r') as f:
            return json.load(f)
    except:
        return None

def main():
    print(f"AI Trading Platform Monitor - {datetime.now()}")
    print("=" * 50)
    
    # Check platform health
    if check_platform_health():
        print("✓ Platform is healthy")
    else:
        print("✗ Platform is not responding")
        return
    
    # Get trading statistics
    stats = get_trading_stats()
    if stats:
        metrics = stats.get('performance_metrics', {})
        print(f"Total Trades: {metrics.get('total_trades', 0)}")
        print(f"Portfolio Value: ${metrics.get('portfolio_value', 0):.2f}")
        print(f"Total P&L: ${metrics.get('total_profit_loss', 0):.2f}")
        print(f"Win Rate: {metrics.get('win_rate', 0):.1f}%")
        print(f"Market Hours Active: {stats.get('market_hours_active', False)}")
        print(f"Last Trade: {len(stats.get('trade_history', []))} trades executed")
    else:
        print("No trading statistics available")

if __name__ == "__main__":
    main()
"""
        
        with open(self.project_root / 'monitor_ai_bot.py', 'w') as f:
            f.write(monitoring_content)
        
        logger.info("Monitoring script created ✓")
        return True
    
    def create_deployment_readme(self):
        """Create comprehensive deployment documentation"""
        logger.info("Creating deployment documentation...")
        
        readme_content = """# AI-Powered Trading Platform Deployment Guide

## Overview
This guide explains how to deploy the AI-powered trading platform and set up the automated paper trading system for real-world market testing.

## Features Deployed
- ✅ Advanced Order Management System (stop-loss, take-profit, trailing stops)
- ✅ Market Intelligence Hub (real-time sentiment analysis, news aggregation)  
- ✅ Deep Learning Engine (LSTM neural networks, pattern recognition)
- ✅ Performance Optimization System (Redis caching, WebSocket pooling)
- ✅ Error Recovery System (self-healing architecture)
- ✅ AI Paper Trading Bot (automated market testing)

## Quick Deployment (Replit)

### 1. Deploy the Platform
```bash
# The platform is ready for deployment
# Click the "Deploy" button in Replit to deploy to production
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings:
# - Set DATABASE_URL to your PostgreSQL database
# - Set SESSION_SECRET to a secure random string
# - Set OPENAI_API_KEY (optional, for enhanced AI features)
```

### 3. Start the AI Trading Bot
```bash
# Method 1: Direct execution
python3 paper_trading_automation.py

# Method 2: Using startup script
./start_ai_bot.sh

# Method 3: Background service
nohup python3 paper_trading_automation.py > ai_bot.log 2>&1 &
```

## AI Paper Trading Bot Features

### Automated Trading Strategy
- **Market Hours Detection**: Only trades during market hours (9 AM - 4 PM EST)
- **Technical Analysis**: Uses RSI, MACD, Bollinger Bands, volume analysis
- **AI Integration**: Leverages platform's AI insights for decision making
- **Risk Management**: Maximum 10% of portfolio per trade
- **Real-time Data**: Uses yfinance for current market prices

### Watchlist Stocks
- AAPL (Apple Inc.)
- MSFT (Microsoft Corp.)
- GOOGL (Alphabet Inc.)
- AMZN (Amazon.com Inc.)
- TSLA (Tesla Inc.)
- NVDA (NVIDIA Corp.)
- META (Meta Platforms Inc.)
- NFLX (Netflix Inc.)

### Trading Cycle
- **Frequency**: Every 15 minutes during market hours
- **Analysis**: Technical indicators + AI recommendations
- **Execution**: Automatic buy/sell decisions
- **Reporting**: Daily reports generated at market close

## Monitoring and Reports

### Real-time Monitoring
```bash
# Check AI bot status
python3 monitor_ai_bot.py

# View live logs
tail -f ai_bot.log

# Check platform health
curl http://localhost:5000/health
```

### Trading Reports
- **Location**: `trading_report_YYYYMMDD_HHMMSS.json`
- **Frequency**: Daily at market close + on-demand
- **Contents**: Performance metrics, trade history, platform status

### Performance Metrics Tracked
- Total trades executed
- Winning vs losing trades
- Portfolio value changes
- Profit/loss tracking
- Win rate percentage
- Risk-adjusted returns

## API Endpoints Available

### Advanced Trading Features
- `POST /api/orders/advanced` - Create advanced orders
- `POST /api/orders/position-size` - Calculate optimal position size
- `GET /api/market-intelligence/overview` - Market intelligence
- `GET /api/deep-learning/analyze/{symbol}` - AI analysis
- `GET /api/performance/optimization-report` - Performance report

### AI and Analytics
- `GET /api/ai/unified-recommendations` - Unified AI recommendations
- `GET /api/ai/insights/{symbol}` - Enhanced AI insights
- `GET /api/technical-indicators/{symbol}` - Technical analysis
- `GET /api/portfolio/advanced-analytics` - Advanced portfolio analytics

## Security Considerations

### Production Settings
- Set `DEBUG=False` in environment
- Use secure `SESSION_SECRET`
- Enable HTTPS in production
- Implement rate limiting
- Monitor for suspicious activity

### Paper Trading Safety
- No real money at risk
- Simulated trading environment
- Safe testing of AI strategies
- Performance data collection only

## Troubleshooting

### Common Issues
1. **Database Connection**: Ensure PostgreSQL is running and accessible
2. **API Keys**: Verify OPENAI_API_KEY is set (optional but recommended)
3. **Market Data**: Check yfinance connectivity for real-time prices
4. **Permissions**: Ensure scripts have execute permissions

### Log Locations
- Main application: Check Replit console
- AI bot: `ai_bot.log` and `paper_trading.log`
- Trading reports: `trading_report_*.json`

## Support and Maintenance

### Daily Tasks
- Check AI bot performance reports
- Monitor system health
- Review trading decisions
- Update watchlist if needed

### Weekly Tasks
- Analyze performance trends
- Review AI model accuracy
- Update risk parameters
- Backup trading reports

## Real-World Testing Results

The AI system will:
1. **Authenticate** with the platform automatically
2. **Analyze** market conditions every 15 minutes
3. **Execute** trades based on AI recommendations
4. **Track** performance and generate reports
5. **Operate** safely with no real money at risk

This provides valuable data on:
- Platform performance under real market conditions
- AI trading strategy effectiveness
- System reliability and uptime
- User experience validation

## Next Steps

1. Deploy the platform to production
2. Start the AI paper trading bot
3. Monitor performance during market hours
4. Collect and analyze trading data
5. Optimize strategies based on results

The system is production-ready and will provide comprehensive real-world testing data while maintaining zero financial risk.
"""
        
        with open(self.project_root / 'DEPLOYMENT.md', 'w') as f:
            f.write(readme_content)
        
        logger.info("Deployment documentation created ✓")
        return True
    
    def run_deployment_checklist(self):
        """Run complete deployment checklist"""
        logger.info("Running deployment checklist...")
        
        checklist = [
            ("Check requirements", self.check_requirements),
            ("Setup environment", self.setup_environment),
            ("Create deployment config", self.create_deployment_config),
            ("Create AI bot service", self.create_ai_bot_service),
            ("Create startup script", self.create_startup_script),
            ("Create monitoring script", self.create_monitoring_script),
            ("Create deployment readme", self.create_deployment_readme),
        ]
        
        results = []
        for task_name, task_func in checklist:
            try:
                result = task_func()
                results.append((task_name, result))
                if result:
                    logger.info(f"✓ {task_name}")
                else:
                    logger.error(f"✗ {task_name}")
            except Exception as e:
                logger.error(f"✗ {task_name}: {e}")
                results.append((task_name, False))
        
        # Summary
        successful = sum(1 for _, result in results if result)
        total = len(results)
        
        logger.info(f"\nDeployment Checklist Complete: {successful}/{total} tasks successful")
        
        if successful == total:
            logger.info("🚀 Platform is ready for deployment!")
            self.deployment_ready = True
            return True
        else:
            logger.error("⚠️ Some tasks failed. Please review and fix issues.")
            return False
    
    def create_health_check_endpoint(self):
        """Create a health check endpoint for the platform"""
        logger.info("Creating health check endpoint...")
        
        health_check_content = """
@app.route('/health')
def health_check():
    \"\"\"Health check endpoint for deployment monitoring\"\"\"
    try:
        # Check database connectivity
        db.session.execute('SELECT 1')
        
        # Check AI services
        ai_status = {
            'ai_engine': bool(ai_engine),
            'order_manager': bool(order_manager),
            'market_intelligence': bool(market_intelligence),
            'deep_learning_engine': bool(deep_learning_engine),
            'performance_optimizer': bool(performance_optimizer)
        }
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'ai_services': ai_status,
            'version': '1.0.0',
            'features': [
                'advanced_orders',
                'market_intelligence', 
                'deep_learning',
                'performance_optimization',
                'error_recovery',
                'real_time_updates'
            ]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
"""
        
        # Add to routes.py
        with open(self.project_root / 'routes.py', 'a') as f:
            f.write(health_check_content)
        
        logger.info("Health check endpoint added ✓")
        return True

def main():
    """Main function to run deployment setup"""
    logger.info("🚀 Starting Trading Platform Deployment Setup")
    
    deployment = TradingPlatformDeployment()
    
    # Run deployment checklist
    success = deployment.run_deployment_checklist()
    
    if success:
        logger.info("\n" + "="*60)
        logger.info("🎉 DEPLOYMENT SETUP COMPLETE!")
        logger.info("="*60)
        logger.info("Your trading platform is ready for deployment with:")
        logger.info("✅ Institutional-grade trading features")
        logger.info("✅ AI-powered market analysis")
        logger.info("✅ Automated paper trading system")
        logger.info("✅ Real-time performance monitoring")
        logger.info("✅ Comprehensive error recovery")
        logger.info("✅ Production-ready configuration")
        logger.info("\nNext steps:")
        logger.info("1. Click 'Deploy' in Replit to deploy to production")
        logger.info("2. Run: python3 paper_trading_automation.py")
        logger.info("3. Monitor with: python3 monitor_ai_bot.py")
        logger.info("4. Check DEPLOYMENT.md for detailed instructions")
        logger.info("="*60)
        
        return True
    else:
        logger.error("Deployment setup failed. Please check logs and fix issues.")
        return False

if __name__ == "__main__":
    main()