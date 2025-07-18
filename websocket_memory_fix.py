#!/usr/bin/env python3
"""
WebSocket Memory Fix Module
Addresses memory leaks and worker crashes for App Store readiness
"""

import logging
import os
import sys
from flask_socketio import SocketIO
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketMemoryOptimizer:
    """Optimizes WebSocket configuration for production stability"""
    
    def __init__(self):
        self.connections = {}
        self.cleanup_thread = None
        self.is_running = False
        
    def get_optimized_config(self):
        """Get optimized WebSocket configuration for production"""
        return {
            'async_mode': 'threading',
            'ping_timeout': 10,  # Reduced from default 60
            'ping_interval': 5,  # Reduced from default 25
            'max_http_buffer_size': 1000000,  # 1MB limit
            'cors_allowed_origins': "*",
            'allow_upgrades': True,
            'transports': ['websocket', 'polling'],
            'engineio_logger': False,  # Disable verbose logging
            'socketio_logger': False,  # Disable verbose logging
            'manage_session': False,  # Let Flask-Login handle sessions
        }
    
    def initialize_optimized_socketio(self, app):
        """Initialize SocketIO with optimized configuration"""
        config = self.get_optimized_config()
        
        logger.info("🔧 Initializing optimized WebSocket configuration...")
        
        # Create SocketIO instance with optimized settings
        socketio = SocketIO(app, **config)
        
        # Add connection tracking
        self.add_connection_tracking(socketio)
        
        # Start cleanup thread
        self.start_cleanup_thread()
        
        return socketio
    
    def add_connection_tracking(self, socketio):
        """Add connection tracking for memory management"""
        
        @socketio.on('connect')
        def handle_connect():
            client_id = request.sid
            self.connections[client_id] = {
                'connected_at': time.time(),
                'last_activity': time.time()
            }
            logger.info(f"📱 Client connected: {client_id}")
        
        @socketio.on('disconnect')
        def handle_disconnect():
            client_id = request.sid
            if client_id in self.connections:
                del self.connections[client_id]
                logger.info(f"📱 Client disconnected: {client_id}")
        
        @socketio.on('ping')
        def handle_ping():
            client_id = request.sid
            if client_id in self.connections:
                self.connections[client_id]['last_activity'] = time.time()
    
    def start_cleanup_thread(self):
        """Start background thread for connection cleanup"""
        if self.cleanup_thread is None:
            self.is_running = True
            self.cleanup_thread = threading.Thread(target=self.cleanup_connections)
            self.cleanup_thread.daemon = True
            self.cleanup_thread.start()
            logger.info("🧹 Started connection cleanup thread")
    
    def cleanup_connections(self):
        """Clean up stale connections to prevent memory leaks"""
        while self.is_running:
            try:
                current_time = time.time()
                stale_connections = []
                
                for client_id, info in self.connections.items():
                    # Remove connections inactive for > 5 minutes
                    if current_time - info['last_activity'] > 300:
                        stale_connections.append(client_id)
                
                for client_id in stale_connections:
                    del self.connections[client_id]
                    logger.info(f"🧹 Cleaned up stale connection: {client_id}")
                
                # Sleep for 30 seconds before next cleanup
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Error in cleanup thread: {e}")
                time.sleep(10)
    
    def stop_cleanup_thread(self):
        """Stop the cleanup thread"""
        self.is_running = False
        if self.cleanup_thread:
            self.cleanup_thread.join()
            logger.info("🛑 Stopped connection cleanup thread")

# Global optimizer instance
websocket_optimizer = WebSocketMemoryOptimizer()

def optimize_websocket_for_app_store(app):
    """Main function to optimize WebSocket for App Store deployment"""
    logger.info("🚀 Optimizing WebSocket for App Store deployment...")
    
    # Initialize optimized WebSocket
    socketio = websocket_optimizer.initialize_optimized_socketio(app)
    
    # Add error handling
    @socketio.on_error_default
    def default_error_handler(e):
        logger.error(f"❌ WebSocket error: {e}")
        # Don't crash the worker, just log the error
        pass
    
    logger.info("✅ WebSocket optimization complete")
    
    return socketio

def get_production_wsgi_config():
    """Get production WSGI configuration"""
    return {
        'bind': '0.0.0.0:5000',
        'workers': 2,  # Reduced from default to prevent memory issues
        'worker_class': 'eventlet',  # Better for WebSocket
        'worker_connections': 100,  # Limit connections per worker
        'max_requests': 1000,  # Restart workers after 1000 requests
        'max_requests_jitter': 50,  # Add jitter to prevent thundering herd
        'timeout': 30,  # Reduced timeout
        'keepalive': 2,  # Keep connections alive briefly
        'preload_app': True,  # Preload for better performance
        'reload': False,  # Disable reload in production
        'daemon': False,  # Don't daemonize
        'pidfile': None,  # No PID file needed
        'log_level': 'info',  # Reduced log verbosity
        'access_log_format': '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s',
        'error_log': '-',  # Log to stdout
        'access_log': '-',  # Log to stdout
    }

if __name__ == "__main__":
    print("🔧 WebSocket Memory Optimization Module")
    print("This module optimizes WebSocket configuration for App Store deployment")
    print("Import and use optimize_websocket_for_app_store(app) in your main application")