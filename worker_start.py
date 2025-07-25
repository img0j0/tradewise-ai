#!/usr/bin/env python3
"""
Production worker startup script for TradeWise AI
Handles background task processing in Render environment
"""

import os
import sys
import logging
import time
from threading import Event

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def start_worker():
    """Start the background worker with proper error handling"""
    try:
        # Import after path setup
        from app import app
        
        # Import optional services with error handling
        task_queue = None
        precomputation_service = None
        
        try:
            from async_task_queue import task_queue
        except ImportError:
            logger.warning("async_task_queue not available, skipping task queue")
        
        try:
            from ai_precomputation_service import precomputation_service
        except ImportError:
            logger.warning("ai_precomputation_service not available, skipping precomputation")
        
        logger.info("Starting TradeWise AI background worker...")
        
        # Ensure we're in application context
        with app.app_context():
            # Initialize services
            if task_queue:
                logger.info("Initializing task queue...")
                if hasattr(task_queue, 'start_workers'):
                    task_queue.start_workers(num_workers=2)
                else:
                    logger.warning("Task queue start_workers method not available")
            
            # Start precomputation service if enabled
            if precomputation_service and os.getenv('PRECOMPUTATION_ENABLED', 'true').lower() == 'true':
                logger.info("Starting precomputation service...")
                if hasattr(precomputation_service, 'start_precomputation'):
                    precomputation_service.start_precomputation()
                else:
                    logger.warning("Precomputation start_precomputation method not available")
            
            logger.info("Worker services started successfully")
            
            # Keep the worker running
            shutdown_event = Event()
            
            try:
                while not shutdown_event.is_set():
                    # Health check - ensure services are running
                    if task_queue and hasattr(task_queue, 'is_healthy') and not task_queue.is_healthy():
                        logger.warning("Task queue unhealthy, attempting restart...")
                        if hasattr(task_queue, 'restart_workers'):
                            task_queue.restart_workers()
                    
                    # Sleep for 30 seconds between health checks
                    shutdown_event.wait(30)
                    
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
            except Exception as e:
                logger.error(f"Worker error: {e}")
                raise
            finally:
                # Graceful shutdown
                logger.info("Shutting down worker services...")
                if task_queue and hasattr(task_queue, 'stop_workers'):
                    task_queue.stop_workers()
                if precomputation_service and hasattr(precomputation_service, 'stop_precomputation'):
                    precomputation_service.stop_precomputation()
                logger.info("Worker shutdown complete")
                
    except Exception as e:
        logger.error(f"Failed to start worker: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_worker()