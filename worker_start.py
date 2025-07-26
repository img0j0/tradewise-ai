#!/usr/bin/env python3
"""
Background Worker Startup Script for Render Deployment
"""

import os
import sys
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start background worker for async tasks"""
    logger.info("🚀 Starting TradeWise AI Background Worker")
    logger.info(f"Worker Type: {os.environ.get('WORKER_TYPE', 'background')}")
    logger.info(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    
    try:
        # Import and start async task queue worker
        try:
            from async_task_queue import start_worker
            logger.info("✅ Async task queue worker starting...")
            start_worker()
        except (ImportError, AttributeError):
            raise ImportError("Async task queue not available")
        
    except ImportError:
        logger.warning("⚠️ Async task queue not available, starting monitoring worker")
        
        try:
            # Start admin monitoring system as fallback
            from admin_monitoring_system import monitoring_system
            
            logger.info("✅ Admin monitoring system starting...")
            monitoring_system.start_monitoring()
            
            # Keep worker alive
            while True:
                time.sleep(30)
                logger.debug("Worker heartbeat")
                
        except Exception as e:
            logger.error(f"❌ Failed to start monitoring worker: {e}")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"❌ Failed to start background worker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()