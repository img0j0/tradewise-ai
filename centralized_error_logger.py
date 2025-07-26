#!/usr/bin/env python3
"""
Centralized Error Logger - Phase 6
Comprehensive error logging system for tools and async tasks
"""

import os
import json
import time
import logging
import sqlite3
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from functools import wraps
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high" 
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error categories"""
    DATABASE = "database"
    API = "api"
    REDIS = "redis"
    TOOLS = "tools"
    ASYNC_TASKS = "async_tasks"
    AUTHENTICATION = "authentication"
    PAYMENT = "payment"
    SYSTEM = "system"
    NETWORK = "network"
    VALIDATION = "validation"

@dataclass
class ErrorLog:
    """Centralized error log entry"""
    id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    component: str
    function_name: str
    error_type: str
    error_message: str
    stack_trace: Optional[str]
    user_id: Optional[str]
    request_id: Optional[str]
    metadata: Optional[Dict[str, Any]]
    resolved: bool = False
    resolution_notes: Optional[str] = None

class CentralizedErrorLogger:
    """Comprehensive centralized error logging system"""
    
    def __init__(self):
        self.db_path = "logs/centralized_errors.db"
        self.log_file = "logs/centralized_errors.log"
        
        # Initialize database and log file
        self._initialize_error_storage()
        
        # Setup file logger
        self._setup_file_logger()
        
        logger.info("✅ Centralized Error Logger initialized")

    def _initialize_error_storage(self):
        """Initialize SQLite database for error storage"""
        os.makedirs("logs", exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS error_logs (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    component TEXT NOT NULL,
                    function_name TEXT NOT NULL,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    user_id TEXT,
                    request_id TEXT,
                    metadata TEXT,
                    resolved INTEGER DEFAULT 0,
                    resolution_notes TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for faster queries
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON error_logs(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_severity ON error_logs(severity)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_category ON error_logs(category)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_resolved ON error_logs(resolved)')
            
        logger.info("✅ Error storage database initialized")

    def _setup_file_logger(self):
        """Setup file logger for errors"""
        self.file_logger = logging.getLogger('centralized_errors')
        self.file_logger.setLevel(logging.ERROR)
        
        # Create file handler
        handler = logging.FileHandler(self.log_file)
        handler.setLevel(logging.ERROR)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [%(component)s.%(function_name)s] - %(message)s'
        )
        handler.setFormatter(formatter)
        
        self.file_logger.addHandler(handler)

    def log_error(self, 
                  severity: ErrorSeverity,
                  category: ErrorCategory,
                  component: str,
                  function_name: str,
                  error: Exception,
                  user_id: Optional[str] = None,
                  request_id: Optional[str] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> str:
        """Log error to centralized system"""
        
        # Generate unique error ID
        error_id = f"{category.value}_{component}_{int(time.time() * 1000)}"
        
        # Create error log entry
        error_log = ErrorLog(
            id=error_id,
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            component=component,
            function_name=function_name,
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            user_id=user_id,
            request_id=request_id,
            metadata=metadata
        )
        
        # Store in database
        self._store_error(error_log)
        
        # Log to file
        self._log_to_file(error_log)
        
        # Trigger alert for critical errors
        if severity == ErrorSeverity.CRITICAL:
            self._trigger_critical_alert(error_log)
            
        return error_id

    def _store_error(self, error_log: ErrorLog):
        """Store error in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO error_logs (
                        id, timestamp, severity, category, component,
                        function_name, error_type, error_message, stack_trace,
                        user_id, request_id, metadata, resolved, resolution_notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    error_log.id,
                    error_log.timestamp.isoformat(),
                    error_log.severity.value,
                    error_log.category.value,
                    error_log.component,
                    error_log.function_name,
                    error_log.error_type,
                    error_log.error_message,
                    error_log.stack_trace,
                    error_log.user_id,
                    error_log.request_id,
                    json.dumps(error_log.metadata) if error_log.metadata else None,
                    int(error_log.resolved),
                    error_log.resolution_notes
                ))
                
        except Exception as e:
            # Fallback logging if database fails
            logger.error(f"Failed to store error in database: {e}")
            self.file_logger.error(f"Database storage failed for error {error_log.id}: {error_log.error_message}")

    def _log_to_file(self, error_log: ErrorLog):
        """Log error to file"""
        try:
            # Add component and function_name to logger context
            extra = {
                'component': error_log.component,
                'function_name': error_log.function_name
            }
            
            log_message = f"[{error_log.severity.value.upper()}] {error_log.error_message}"
            if error_log.metadata:
                log_message += f" | Metadata: {json.dumps(error_log.metadata)}"
                
            self.file_logger.error(log_message, extra=extra)
            
        except Exception as e:
            logger.error(f"Failed to log error to file: {e}")

    def _trigger_critical_alert(self, error_log: ErrorLog):
        """Trigger alert for critical errors"""
        try:
            # Import here to avoid circular imports
            from admin_monitoring_system import monitoring_system
            
            alert = monitoring_system._create_alert(
                'critical_error',
                'CRITICAL',
                f"Critical error in {error_log.component}: {error_log.error_message}",
                error_log.component
            )
            
            monitoring_system.alert_queue.put(alert)
            logger.info(f"Critical alert triggered for error {error_log.id}")
            
        except Exception as e:
            logger.error(f"Failed to trigger critical alert: {e}")

    def get_recent_errors(self, hours: int = 24, severity: Optional[ErrorSeverity] = None) -> List[Dict]:
        """Get recent errors from database"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            query = 'SELECT * FROM error_logs WHERE timestamp > ?'
            params = [cutoff_time.isoformat()]
            
            if severity:
                query += ' AND severity = ?'
                params.append(severity.value)
                
            query += ' ORDER BY timestamp DESC'
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                errors = []
                
                for row in cursor.fetchall():
                    error_dict = dict(zip(columns, row))
                    # Parse metadata if present
                    if error_dict['metadata']:
                        error_dict['metadata'] = json.loads(error_dict['metadata'])
                    errors.append(error_dict)
                    
                return errors
                
        except Exception as e:
            logger.error(f"Failed to get recent errors: {e}")
            return []

    def get_error_statistics(self, hours: int = 24) -> Dict:
        """Get error statistics"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with sqlite3.connect(self.db_path) as conn:
                # Total errors
                total_errors = conn.execute(
                    'SELECT COUNT(*) FROM error_logs WHERE timestamp > ?',
                    (cutoff_time.isoformat(),)
                ).fetchone()[0]
                
                # Errors by severity
                severity_stats = {}
                for severity in ErrorSeverity:
                    count = conn.execute(
                        'SELECT COUNT(*) FROM error_logs WHERE timestamp > ? AND severity = ?',
                        (cutoff_time.isoformat(), severity.value)
                    ).fetchone()[0]
                    severity_stats[severity.value] = count
                
                # Errors by category
                category_stats = {}
                for category in ErrorCategory:
                    count = conn.execute(
                        'SELECT COUNT(*) FROM error_logs WHERE timestamp > ? AND category = ?',
                        (cutoff_time.isoformat(), category.value)
                    ).fetchone()[0]
                    category_stats[category.value] = count
                
                # Top error components
                top_components = conn.execute('''
                    SELECT component, COUNT(*) as count 
                    FROM error_logs 
                    WHERE timestamp > ? 
                    GROUP BY component 
                    ORDER BY count DESC 
                    LIMIT 10
                ''', (cutoff_time.isoformat(),)).fetchall()
                
                return {
                    'total_errors': total_errors,
                    'severity_stats': severity_stats,
                    'category_stats': category_stats,
                    'top_components': [{'component': comp, 'count': count} for comp, count in top_components],
                    'period_hours': hours
                }
                
        except Exception as e:
            logger.error(f"Failed to get error statistics: {e}")
            return {'error': str(e)}

    def resolve_error(self, error_id: str, resolution_notes: str) -> bool:
        """Mark error as resolved"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute('''
                    UPDATE error_logs 
                    SET resolved = 1, resolution_notes = ?
                    WHERE id = ?
                ''', (resolution_notes, error_id))
                
                return result.rowcount > 0
                
        except Exception as e:
            logger.error(f"Failed to resolve error {error_id}: {e}")
            return False

    def cleanup_old_errors(self, days: int = 30):
        """Clean up old error logs"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute(
                    'DELETE FROM error_logs WHERE timestamp < ?',
                    (cutoff_time.isoformat(),)
                )
                
                logger.info(f"Cleaned up {result.rowcount} old error logs")
                return result.rowcount
                
        except Exception as e:
            logger.error(f"Failed to cleanup old errors: {e}")
            return 0

# Global error logger instance
error_logger = CentralizedErrorLogger()

# Decorator for automatic error logging
def log_errors(component: str, 
               category: ErrorCategory = ErrorCategory.SYSTEM,
               severity: ErrorSeverity = ErrorSeverity.MEDIUM):
    """Decorator to automatically log errors from functions"""
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the error
                error_id = error_logger.log_error(
                    severity=severity,
                    category=category,
                    component=component,
                    function_name=func.__name__,
                    error=e,
                    metadata={'args': str(args), 'kwargs': str(kwargs)}
                )
                
                # Re-raise the exception
                raise e
                
        return wrapper
    return decorator

# Context manager for error logging
class ErrorContext:
    """Context manager for error logging in code blocks"""
    
    def __init__(self, component: str, function_name: str, 
                 category: ErrorCategory = ErrorCategory.SYSTEM,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 metadata: Optional[Dict[str, Any]] = None):
        self.component = component
        self.function_name = function_name
        self.category = category
        self.severity = severity
        self.metadata = metadata or {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            error_logger.log_error(
                severity=self.severity,
                category=self.category,
                component=self.component,
                function_name=self.function_name,
                error=exc_val,
                metadata=self.metadata
            )
        return False  # Don't suppress the exception

# Helper functions for common error patterns
def log_database_error(component: str, function_name: str, error: Exception, **metadata):
    """Log database-specific errors"""
    return error_logger.log_error(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.DATABASE,
        component=component,
        function_name=function_name,
        error=error,
        metadata=metadata
    )

def log_api_error(component: str, function_name: str, error: Exception, **metadata):
    """Log API-specific errors"""
    return error_logger.log_error(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.API,
        component=component,
        function_name=function_name,
        error=error,
        metadata=metadata
    )

def log_redis_error(component: str, function_name: str, error: Exception, **metadata):
    """Log Redis-specific errors"""
    return error_logger.log_error(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.REDIS,
        component=component,
        function_name=function_name,
        error=error,
        metadata=metadata
    )

def log_tool_error(component: str, function_name: str, error: Exception, **metadata):
    """Log tool-specific errors"""
    return error_logger.log_error(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.TOOLS,
        component=component,
        function_name=function_name,
        error=error,
        metadata=metadata
    )

def log_async_task_error(component: str, function_name: str, error: Exception, **metadata):
    """Log async task errors"""
    return error_logger.log_error(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.ASYNC_TASKS,
        component=component,
        function_name=function_name,
        error=error,
        metadata=metadata
    )

if __name__ == "__main__":
    # Test the error logging system
    try:
        raise ValueError("Test error for centralized logging")
    except Exception as e:
        error_id = error_logger.log_error(
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.SYSTEM,
            component="test_component",
            function_name="test_function",
            error=e,
            metadata={'test': True}
        )
        print(f"✅ Test error logged with ID: {error_id}")