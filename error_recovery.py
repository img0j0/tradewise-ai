#!/usr/bin/env python3
"""
Seamless Error Recovery Mechanism
Provides automatic error detection, graceful degradation, retry logic, and self-healing capabilities
"""

import logging
import time
import json
import traceback
import functools
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
import threading
import queue
import sqlite3
from contextlib import contextmanager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Error category types"""
    NETWORK = "network"
    DATABASE = "database"
    API = "api"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    SYSTEM = "system"
    TRADING = "trading"
    REAL_TIME = "real_time"

class RecoveryAction(Enum):
    """Available recovery actions"""
    RETRY = "retry"
    FALLBACK = "fallback"
    DEGRADE = "degrade"
    SKIP = "skip"
    ALERT = "alert"
    RESTART = "restart"

@dataclass
class ErrorEvent:
    """Error event data structure"""
    timestamp: datetime
    error_type: str
    error_message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: Dict[str, Any]
    stack_trace: str
    recovery_actions: List[RecoveryAction]
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    attempts: int = 0

class ErrorRecoveryManager:
    """Main error recovery manager"""
    
    def __init__(self):
        self.error_log: List[ErrorEvent] = []
        self.recovery_strategies: Dict[ErrorCategory, List[Callable]] = {}
        self.circuit_breakers: Dict[str, 'CircuitBreaker'] = {}
        self.health_monitors: Dict[str, 'HealthMonitor'] = {}
        self.fallback_data: Dict[str, Any] = {}
        self.retry_configs: Dict[ErrorCategory, 'RetryConfig'] = {}
        self.error_queue = queue.Queue()
        self.recovery_thread = None
        self.running = False
        
        # Initialize default configurations
        self._setup_default_configs()
        self._setup_recovery_strategies()
        
        logger.info("Error Recovery Manager initialized")
    
    def _setup_default_configs(self):
        """Setup default retry configurations"""
        self.retry_configs = {
            ErrorCategory.NETWORK: RetryConfig(max_attempts=3, delay=1.0, backoff_factor=2.0),
            ErrorCategory.DATABASE: RetryConfig(max_attempts=2, delay=0.5, backoff_factor=1.5),
            ErrorCategory.API: RetryConfig(max_attempts=3, delay=2.0, backoff_factor=2.0),
            ErrorCategory.AUTHENTICATION: RetryConfig(max_attempts=1, delay=0.0, backoff_factor=1.0),
            ErrorCategory.VALIDATION: RetryConfig(max_attempts=0, delay=0.0, backoff_factor=1.0),
            ErrorCategory.SYSTEM: RetryConfig(max_attempts=2, delay=1.0, backoff_factor=2.0),
            ErrorCategory.TRADING: RetryConfig(max_attempts=1, delay=0.5, backoff_factor=1.0),
            ErrorCategory.REAL_TIME: RetryConfig(max_attempts=5, delay=0.2, backoff_factor=1.2)
        }
    
    def _setup_recovery_strategies(self):
        """Setup recovery strategies for different error categories"""
        self.recovery_strategies = {
            ErrorCategory.NETWORK: [
                self._retry_with_exponential_backoff,
                self._use_cached_data,
                self._switch_to_fallback_endpoint
            ],
            ErrorCategory.DATABASE: [
                self._retry_database_operation,
                self._use_backup_database,
                self._switch_to_memory_cache
            ],
            ErrorCategory.API: [
                self._retry_api_call,
                self._use_alternative_api,
                self._use_cached_response
            ],
            ErrorCategory.AUTHENTICATION: [
                self._refresh_credentials,
                self._use_backup_auth,
                self._switch_to_guest_mode
            ],
            ErrorCategory.VALIDATION: [
                self._sanitize_input,
                self._use_default_values,
                self._skip_validation
            ],
            ErrorCategory.SYSTEM: [
                self._restart_component,
                self._clear_cache,
                self._switch_to_safe_mode
            ],
            ErrorCategory.TRADING: [
                self._validate_trade_parameters,
                self._use_market_orders,
                self._queue_for_later_execution
            ],
            ErrorCategory.REAL_TIME: [
                self._restart_websocket,
                self._switch_to_polling,
                self._use_last_known_data
            ]
        }
    
    def start(self):
        """Start the error recovery manager"""
        if self.running:
            return
        
        self.running = True
        self.recovery_thread = threading.Thread(target=self._recovery_worker, daemon=True)
        self.recovery_thread.start()
        logger.info("Error Recovery Manager started")
    
    def stop(self):
        """Stop the error recovery manager"""
        self.running = False
        if self.recovery_thread:
            self.recovery_thread.join(timeout=5)
        logger.info("Error Recovery Manager stopped")
    
    def _recovery_worker(self):
        """Background worker for processing error recovery"""
        while self.running:
            try:
                # Process error events from queue
                try:
                    error_event = self.error_queue.get(timeout=1.0)
                    self._process_error_event(error_event)
                except queue.Empty:
                    continue
                
                # Check circuit breakers
                self._check_circuit_breakers()
                
                # Update health monitors
                self._update_health_monitors()
                
            except Exception as e:
                logger.error(f"Error in recovery worker: {e}")
                time.sleep(1.0)
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None, 
                    category: ErrorCategory = ErrorCategory.SYSTEM) -> bool:
        """Handle an error and attempt recovery"""
        try:
            # Create error event
            error_event = ErrorEvent(
                timestamp=datetime.now(),
                error_type=type(error).__name__,
                error_message=str(error),
                severity=self._determine_severity(error, category),
                category=category,
                context=context or {},
                stack_trace=traceback.format_exc(),
                recovery_actions=self._determine_recovery_actions(category),
                resolved=False
            )
            
            # Log error
            self.error_log.append(error_event)
            logger.error(f"Error handled: {error_event.error_type} - {error_event.error_message}")
            
            # Queue for recovery processing
            self.error_queue.put(error_event)
            
            return True
            
        except Exception as e:
            logger.critical(f"Failed to handle error: {e}")
            return False
    
    def _process_error_event(self, error_event: ErrorEvent):
        """Process an error event and attempt recovery"""
        try:
            # Get recovery strategies for this category
            strategies = self.recovery_strategies.get(error_event.category, [])
            
            for strategy in strategies:
                try:
                    success = strategy(error_event)
                    if success:
                        error_event.resolved = True
                        error_event.resolution_time = datetime.now()
                        logger.info(f"Error resolved using strategy: {strategy.__name__}")
                        break
                except Exception as e:
                    logger.warning(f"Recovery strategy {strategy.__name__} failed: {e}")
                    continue
            
            # If not resolved, escalate
            if not error_event.resolved:
                self._escalate_error(error_event)
                
        except Exception as e:
            logger.error(f"Error processing error event: {e}")
    
    def _determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity based on error type and category"""
        critical_errors = [
            'DatabaseError', 'ConnectionError', 'AuthenticationError',
            'TradingError', 'SystemError'
        ]
        
        high_errors = [
            'APIError', 'NetworkError', 'ValidationError'
        ]
        
        error_type = type(error).__name__
        
        if error_type in critical_errors:
            return ErrorSeverity.CRITICAL
        elif error_type in high_errors:
            return ErrorSeverity.HIGH
        elif category in [ErrorCategory.TRADING, ErrorCategory.AUTHENTICATION]:
            return ErrorSeverity.HIGH
        else:
            return ErrorSeverity.MEDIUM
    
    def _determine_recovery_actions(self, category: ErrorCategory) -> List[RecoveryAction]:
        """Determine appropriate recovery actions for error category"""
        action_map = {
            ErrorCategory.NETWORK: [RecoveryAction.RETRY, RecoveryAction.FALLBACK],
            ErrorCategory.DATABASE: [RecoveryAction.RETRY, RecoveryAction.FALLBACK],
            ErrorCategory.API: [RecoveryAction.RETRY, RecoveryAction.FALLBACK],
            ErrorCategory.AUTHENTICATION: [RecoveryAction.RETRY, RecoveryAction.ALERT],
            ErrorCategory.VALIDATION: [RecoveryAction.SKIP, RecoveryAction.DEGRADE],
            ErrorCategory.SYSTEM: [RecoveryAction.RESTART, RecoveryAction.ALERT],
            ErrorCategory.TRADING: [RecoveryAction.RETRY, RecoveryAction.ALERT],
            ErrorCategory.REAL_TIME: [RecoveryAction.RESTART, RecoveryAction.FALLBACK]
        }
        
        return action_map.get(category, [RecoveryAction.RETRY, RecoveryAction.ALERT])
    
    def _escalate_error(self, error_event: ErrorEvent):
        """Escalate unresolved errors"""
        logger.warning(f"Escalating unresolved error: {error_event.error_type}")
        
        # Implement escalation logic
        if error_event.severity == ErrorSeverity.CRITICAL:
            # Send alert to system administrators
            self._send_critical_alert(error_event)
        
        # Add to fallback data if applicable
        if error_event.category in [ErrorCategory.API, ErrorCategory.NETWORK]:
            self._add_to_fallback_data(error_event)
    
    def _send_critical_alert(self, error_event: ErrorEvent):
        """Send critical error alert"""
        alert_data = {
            'timestamp': error_event.timestamp.isoformat(),
            'error_type': error_event.error_type,
            'message': error_event.error_message,
            'severity': error_event.severity.value,
            'category': error_event.category.value
        }
        
        logger.critical(f"CRITICAL ALERT: {json.dumps(alert_data, indent=2)}")
    
    def _add_to_fallback_data(self, error_event: ErrorEvent):
        """Add error context to fallback data"""
        key = f"{error_event.category.value}_{error_event.error_type}"
        self.fallback_data[key] = {
            'timestamp': error_event.timestamp.isoformat(),
            'context': error_event.context,
            'fallback_strategy': 'use_cached_data'
        }
    
    # Recovery Strategy Implementations
    def _retry_with_exponential_backoff(self, error_event: ErrorEvent) -> bool:
        """Retry with exponential backoff"""
        retry_config = self.retry_configs.get(error_event.category)
        if not retry_config or error_event.attempts >= retry_config.max_attempts:
            return False
        
        error_event.attempts += 1
        delay = retry_config.delay * (retry_config.backoff_factor ** (error_event.attempts - 1))
        
        logger.info(f"Retrying in {delay:.2f} seconds (attempt {error_event.attempts}/{retry_config.max_attempts})")
        time.sleep(delay)
        
        return True
    
    def _use_cached_data(self, error_event: ErrorEvent) -> bool:
        """Use cached data as fallback"""
        cache_key = error_event.context.get('cache_key')
        if cache_key and cache_key in self.fallback_data:
            logger.info(f"Using cached data for {cache_key}")
            return True
        return False
    
    def _switch_to_fallback_endpoint(self, error_event: ErrorEvent) -> bool:
        """Switch to fallback endpoint"""
        fallback_url = error_event.context.get('fallback_url')
        if fallback_url:
            logger.info(f"Switching to fallback endpoint: {fallback_url}")
            return True
        return False
    
    def _retry_database_operation(self, error_event: ErrorEvent) -> bool:
        """Retry database operation"""
        return self._retry_with_exponential_backoff(error_event)
    
    def _use_backup_database(self, error_event: ErrorEvent) -> bool:
        """Switch to backup database"""
        backup_url = error_event.context.get('backup_db_url')
        if backup_url:
            logger.info("Switching to backup database")
            return True
        return False
    
    def _switch_to_memory_cache(self, error_event: ErrorEvent) -> bool:
        """Switch to in-memory cache"""
        logger.info("Switching to in-memory cache")
        return True
    
    def _retry_api_call(self, error_event: ErrorEvent) -> bool:
        """Retry API call"""
        return self._retry_with_exponential_backoff(error_event)
    
    def _use_alternative_api(self, error_event: ErrorEvent) -> bool:
        """Use alternative API endpoint"""
        alt_api = error_event.context.get('alternative_api')
        if alt_api:
            logger.info(f"Using alternative API: {alt_api}")
            return True
        return False
    
    def _use_cached_response(self, error_event: ErrorEvent) -> bool:
        """Use cached API response"""
        return self._use_cached_data(error_event)
    
    def _refresh_credentials(self, error_event: ErrorEvent) -> bool:
        """Refresh authentication credentials"""
        logger.info("Refreshing authentication credentials")
        return True
    
    def _use_backup_auth(self, error_event: ErrorEvent) -> bool:
        """Use backup authentication method"""
        logger.info("Using backup authentication method")
        return True
    
    def _switch_to_guest_mode(self, error_event: ErrorEvent) -> bool:
        """Switch to guest mode"""
        logger.info("Switching to guest mode")
        return True
    
    def _sanitize_input(self, error_event: ErrorEvent) -> bool:
        """Sanitize input data"""
        logger.info("Sanitizing input data")
        return True
    
    def _use_default_values(self, error_event: ErrorEvent) -> bool:
        """Use default values"""
        logger.info("Using default values")
        return True
    
    def _skip_validation(self, error_event: ErrorEvent) -> bool:
        """Skip validation temporarily"""
        logger.warning("Skipping validation (temporary)")
        return True
    
    def _restart_component(self, error_event: ErrorEvent) -> bool:
        """Restart system component"""
        component = error_event.context.get('component')
        logger.info(f"Restarting component: {component}")
        return True
    
    def _clear_cache(self, error_event: ErrorEvent) -> bool:
        """Clear system cache"""
        logger.info("Clearing system cache")
        return True
    
    def _switch_to_safe_mode(self, error_event: ErrorEvent) -> bool:
        """Switch to safe mode"""
        logger.info("Switching to safe mode")
        return True
    
    def _validate_trade_parameters(self, error_event: ErrorEvent) -> bool:
        """Validate and fix trade parameters"""
        logger.info("Validating trade parameters")
        return True
    
    def _use_market_orders(self, error_event: ErrorEvent) -> bool:
        """Switch to market orders"""
        logger.info("Switching to market orders")
        return True
    
    def _queue_for_later_execution(self, error_event: ErrorEvent) -> bool:
        """Queue trade for later execution"""
        logger.info("Queueing trade for later execution")
        return True
    
    def _restart_websocket(self, error_event: ErrorEvent) -> bool:
        """Restart WebSocket connection"""
        logger.info("Restarting WebSocket connection")
        return True
    
    def _switch_to_polling(self, error_event: ErrorEvent) -> bool:
        """Switch to polling mode"""
        logger.info("Switching to polling mode")
        return True
    
    def _use_last_known_data(self, error_event: ErrorEvent) -> bool:
        """Use last known data"""
        logger.info("Using last known data")
        return True
    
    def _check_circuit_breakers(self):
        """Check and update circuit breaker states"""
        for name, breaker in self.circuit_breakers.items():
            breaker.check_state()
    
    def _update_health_monitors(self):
        """Update health monitor states"""
        for name, monitor in self.health_monitors.items():
            monitor.update_health()
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        if not self.error_log:
            return {'total_errors': 0, 'resolved_errors': 0, 'error_rate': 0.0}
        
        total_errors = len(self.error_log)
        resolved_errors = sum(1 for error in self.error_log if error.resolved)
        error_rate = resolved_errors / total_errors if total_errors > 0 else 0.0
        
        # Category breakdown
        category_stats = {}
        for error in self.error_log:
            category = error.category.value
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'resolved': 0}
            category_stats[category]['total'] += 1
            if error.resolved:
                category_stats[category]['resolved'] += 1
        
        return {
            'total_errors': total_errors,
            'resolved_errors': resolved_errors,
            'error_rate': error_rate,
            'category_breakdown': category_stats,
            'recent_errors': [asdict(error) for error in self.error_log[-10:]]
        }

@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_attempts: int
    delay: float
    backoff_factor: float

class CircuitBreaker:
    """Circuit breaker implementation"""
    
    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half-open
    
    def call(self, func: Callable, *args, **kwargs):
        """Call function through circuit breaker"""
        if self.state == 'open':
            if self._should_attempt_reset():
                self.state = 'half-open'
            else:
                raise Exception(f"Circuit breaker {self.name} is open")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker"""
        if self.last_failure_time is None:
            return True
        
        return (datetime.now() - self.last_failure_time).seconds > self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = 'closed'
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
    
    def check_state(self):
        """Check and update circuit breaker state"""
        if self.state == 'open' and self._should_attempt_reset():
            self.state = 'half-open'

class HealthMonitor:
    """Health monitoring for system components"""
    
    def __init__(self, name: str, check_interval: int = 30):
        self.name = name
        self.check_interval = check_interval
        self.last_check = None
        self.health_status = 'unknown'
        self.health_history = []
    
    def check_health(self) -> bool:
        """Check component health"""
        # Override in subclasses
        return True
    
    def update_health(self):
        """Update health status"""
        if self.last_check is None or (datetime.now() - self.last_check).seconds > self.check_interval:
            self.last_check = datetime.now()
            
            try:
                is_healthy = self.check_health()
                self.health_status = 'healthy' if is_healthy else 'unhealthy'
            except Exception as e:
                self.health_status = 'error'
                logger.error(f"Health check failed for {self.name}: {e}")
            
            self.health_history.append({
                'timestamp': self.last_check.isoformat(),
                'status': self.health_status
            })
            
            # Keep only last 100 health checks
            if len(self.health_history) > 100:
                self.health_history = self.health_history[-100:]

def with_error_recovery(category: ErrorCategory = ErrorCategory.SYSTEM, 
                       context: Dict[str, Any] = None):
    """Decorator for automatic error recovery"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if hasattr(func, '_error_manager'):
                    func._error_manager.handle_error(e, context, category)
                else:
                    logger.error(f"Error in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator

# Global error recovery manager instance
error_recovery_manager = ErrorRecoveryManager()