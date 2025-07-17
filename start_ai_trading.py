#!/usr/bin/env python3
"""
Start AI Paper Trading Bot with Market Hours Scheduling
This script runs the AI bot automatically at market open and stops at market close
"""

import os
import time
import schedule
import logging
from datetime import datetime
from paper_trading_automation import PaperTradingBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AITradingScheduler:
    """Manages AI trading bot scheduling for market hours"""
    
    def __init__(self):
        self.bot = None
        self.running = False
        
    def start_trading(self):
        """Start AI trading bot"""
        logger.info("🚀 Market is open! Starting AI Paper Trading Bot...")
        
        try:
            self.bot = PaperTradingBot(base_url="http://localhost:5000")
            if self.bot.authenticate():
                logger.info("✅ AI Bot authenticated successfully")
                self.running = True
                
                # Start the trading cycle
                self.bot.run()
                
            else:
                logger.error("❌ Failed to authenticate AI bot")
                
        except Exception as e:
            logger.error(f"❌ Error starting AI bot: {e}")
    
    def stop_trading(self):
        """Stop AI trading bot"""
        logger.info("🛑 Market is closed! Stopping AI Paper Trading Bot...")
        
        if self.bot:
            self.running = False
            self.bot.save_report(f"trading_report_{datetime.now().strftime('%Y%m%d')}.json")
            logger.info("📊 Trading report saved")
        
        logger.info("✅ AI Bot stopped successfully")
    
    def check_status(self):
        """Check and log bot status"""
        if self.running:
            logger.info("📈 AI Bot is actively trading")
        else:
            logger.info("⏳ AI Bot is waiting for market hours")

def main():
    """Main scheduling function"""
    logger.info("🤖 AI Paper Trading Scheduler Starting...")
    
    scheduler = AITradingScheduler()
    
    # Schedule market hours (9:30 AM - 4:00 PM EST)
    schedule.every().monday.at("09:30").do(scheduler.start_trading)
    schedule.every().tuesday.at("09:30").do(scheduler.start_trading)
    schedule.every().wednesday.at("09:30").do(scheduler.start_trading)
    schedule.every().thursday.at("09:30").do(scheduler.start_trading)
    schedule.every().friday.at("09:30").do(scheduler.start_trading)
    
    schedule.every().monday.at("16:00").do(scheduler.stop_trading)
    schedule.every().tuesday.at("16:00").do(scheduler.stop_trading)
    schedule.every().wednesday.at("16:00").do(scheduler.stop_trading)
    schedule.every().thursday.at("16:00").do(scheduler.stop_trading)
    schedule.every().friday.at("16:00").do(scheduler.stop_trading)
    
    # Status check every hour
    schedule.every().hour.do(scheduler.check_status)
    
    logger.info("⏰ AI Trading Bot scheduled for market hours (9:30 AM - 4:00 PM EST)")
    logger.info("📅 Next market open: Tomorrow at 9:30 AM EST")
    logger.info("🔍 Status checks will run every hour")
    
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()