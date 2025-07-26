#!/usr/bin/env python3
"""
Admin Monitoring System - Phase 6
Comprehensive system health monitoring with proactive alerts
"""

import os
import json
import time
import logging
import smtplib
import sqlite3
import psutil
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Blueprint, render_template, jsonify, request
from sqlalchemy import text
from app import db
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SystemAlert:
    """System alert data structure"""
    id: str
    alert_type: str
    severity: str  # CRITICAL, WARNING, INFO
    message: str
    component: str
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    active_connections: int
    redis_status: str
    database_status: str
    api_response_time: float
    queue_size: int
    error_rate: float

class AdminMonitoringSystem:
    """Comprehensive admin monitoring and alerting system"""
    
    def __init__(self):
        self.alerts_db_path = "logs/admin_alerts.db"
        self.metrics_db_path = "logs/system_metrics.db"
        self.monitoring_active = False
        self.alert_queue = queue.Queue()
        self.last_health_check = datetime.now()
        
        # Initialize databases
        self._initialize_databases()
        
        # Email configuration
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_username = os.environ.get('SMTP_USERNAME', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        self.admin_emails = os.environ.get('ADMIN_EMAILS', 'tradewise.founder@gmail.com').split(',')
        
        # Monitoring thresholds
        self.thresholds = {
            'cpu_warning': 80.0,
            'cpu_critical': 95.0,
            'memory_warning': 80.0, 
            'memory_critical': 95.0,
            'disk_warning': 85.0,
            'disk_critical': 95.0,
            'api_response_warning': 2000.0,  # ms
            'api_response_critical': 5000.0,  # ms
            'error_rate_warning': 5.0,  # percent
            'error_rate_critical': 15.0,  # percent
            'queue_size_warning': 50,
            'queue_size_critical': 100
        }
        
        logger.info("✅ Admin Monitoring System initialized")

    def _initialize_databases(self):
        """Initialize SQLite databases for alerts and metrics"""
        os.makedirs("logs", exist_ok=True)
        
        # Initialize alerts database
        with sqlite3.connect(self.alerts_db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    component TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    resolved INTEGER DEFAULT 0,
                    resolution_time TEXT,
                    metadata TEXT
                )
            ''')
            
        # Initialize metrics database
        with sqlite3.connect(self.metrics_db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_usage_percent REAL,
                    active_connections INTEGER,
                    redis_status TEXT,
                    database_status TEXT,
                    api_response_time REAL,
                    queue_size INTEGER,
                    error_rate REAL
                )
            ''')
            
        logger.info("✅ Monitoring databases initialized")

    def start_monitoring(self):
        """Start background monitoring processes"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        
        # Start alert processing thread
        alert_thread = threading.Thread(target=self._process_alerts, daemon=True)
        alert_thread.start()
        
        logger.info("✅ Background monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        logger.info("⏹️ Background monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                metrics = self._collect_system_metrics()
                
                # Store metrics
                self._store_metrics(metrics)
                
                # Check for alerts
                self._check_system_health(metrics)
                
                # Sleep for 30 seconds
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Monitoring loop error: {e}")
                time.sleep(60)  # Wait longer on error

    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect comprehensive system metrics"""
        try:
            # Basic system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network connections (approximate)
            active_connections = len(psutil.net_connections())
            
            # Redis status
            redis_status = self._check_redis_status()
            
            # Database status
            database_status = self._check_database_status()
            
            # API response time (simulate check)
            api_response_time = self._check_api_response_time()
            
            # Queue size (if Redis available)
            queue_size = self._get_queue_size()
            
            # Error rate (from logs)
            error_rate = self._calculate_error_rate()
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                active_connections=active_connections,
                redis_status=redis_status,
                database_status=database_status,
                api_response_time=api_response_time,
                queue_size=queue_size,
                error_rate=error_rate
            )
            
        except Exception as e:
            logger.error(f"❌ Error collecting metrics: {e}")
            # Return empty metrics with error status
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                active_connections=0,
                redis_status="error",
                database_status="error",
                api_response_time=9999.0,
                queue_size=0,
                error_rate=100.0
            )

    def _check_redis_status(self) -> str:
        """Check Redis connection status"""
        try:
            redis_client = redis.Redis(
                host=os.environ.get('REDIS_HOST', 'localhost'),
                port=int(os.environ.get('REDIS_PORT', '6379')),
                decode_responses=True,
                socket_connect_timeout=5
            )
            redis_client.ping()
            return "connected"
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            return "disconnected"

    def _check_database_status(self) -> str:
        """Check PostgreSQL database status"""
        try:
            # Import Flask app context
            from app import app
            with app.app_context():
                db.session.execute(text('SELECT 1'))
                db.session.commit()
                return "connected"
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return "disconnected"

    def _check_api_response_time(self) -> float:
        """Check API response time"""
        try:
            import requests
            start_time = time.time()
            response = requests.get('http://localhost:5000/api/health', timeout=10)
            end_time = time.time()
            
            if response.status_code == 200:
                return (end_time - start_time) * 1000  # Convert to milliseconds
            else:
                return 9999.0  # High value for failed requests
                
        except Exception as e:
            logger.warning(f"API health check failed: {e}")
            return 9999.0

    def _get_queue_size(self) -> int:
        """Get async task queue size"""
        try:
            redis_client = redis.Redis(
                host=os.environ.get('REDIS_HOST', 'localhost'),
                port=int(os.environ.get('REDIS_PORT', '6379')),
                decode_responses=True
            )
            queue_length = redis_client.llen('task_queue')
            if queue_length is None:
                return 0
            # Handle both sync and async returns
            if hasattr(queue_length, '__await__'):
                # This shouldn't happen with redis-py, but just in case
                return 0
            return int(queue_length)
        except Exception:
            return 0

    def _calculate_error_rate(self) -> float:
        """Calculate error rate from recent logs"""
        try:
            # Read recent log entries (last 5 minutes)
            log_file = "logs/app.log"
            if not os.path.exists(log_file):
                return 0.0
                
            cutoff_time = datetime.now() - timedelta(minutes=5)
            total_requests = 0
            error_requests = 0
            
            with open(log_file, 'r') as f:
                for line in f.readlines()[-1000:]:  # Check last 1000 lines
                    if 'Request:' in line:
                        total_requests += 1
                    elif 'ERROR' in line or 'WARNING' in line:
                        error_requests += 1
            
            if total_requests == 0:
                return 0.0
                
            return (error_requests / total_requests) * 100
            
        except Exception as e:
            logger.warning(f"Error calculating error rate: {e}")
            return 0.0

    def _store_metrics(self, metrics: SystemMetrics):
        """Store metrics in database"""
        if not metrics:
            return
            
        try:
            with sqlite3.connect(self.metrics_db_path) as conn:
                conn.execute('''
                    INSERT INTO metrics (
                        timestamp, cpu_percent, memory_percent, disk_usage_percent,
                        active_connections, redis_status, database_status,
                        api_response_time, queue_size, error_rate
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.timestamp.isoformat(),
                    metrics.cpu_percent,
                    metrics.memory_percent,
                    metrics.disk_usage_percent,
                    metrics.active_connections,
                    metrics.redis_status,
                    metrics.database_status,
                    metrics.api_response_time,
                    metrics.queue_size,
                    metrics.error_rate
                ))
                
        except Exception as e:
            logger.error(f"❌ Error storing metrics: {e}")

    def _check_system_health(self, metrics: SystemMetrics):
        """Check system health and generate alerts"""
        if not metrics:
            return
            
        alerts = []
        
        # CPU alerts
        if metrics.cpu_percent >= self.thresholds['cpu_critical']:
            alerts.append(self._create_alert(
                'cpu_usage', 'CRITICAL', 
                f'CPU usage critical: {metrics.cpu_percent:.1f}%', 'system'
            ))
        elif metrics.cpu_percent >= self.thresholds['cpu_warning']:
            alerts.append(self._create_alert(
                'cpu_usage', 'WARNING',
                f'CPU usage high: {metrics.cpu_percent:.1f}%', 'system'
            ))
            
        # Memory alerts
        if metrics.memory_percent >= self.thresholds['memory_critical']:
            alerts.append(self._create_alert(
                'memory_usage', 'CRITICAL',
                f'Memory usage critical: {metrics.memory_percent:.1f}%', 'system'
            ))
        elif metrics.memory_percent >= self.thresholds['memory_warning']:
            alerts.append(self._create_alert(
                'memory_usage', 'WARNING',
                f'Memory usage high: {metrics.memory_percent:.1f}%', 'system'
            ))
            
        # Redis alerts
        if metrics.redis_status == 'disconnected':
            alerts.append(self._create_alert(
                'redis_connection', 'CRITICAL',
                'Redis connection lost - async tasks may fail', 'redis'
            ))
            
        # Database alerts
        if metrics.database_status == 'disconnected':
            alerts.append(self._create_alert(
                'database_connection', 'CRITICAL',
                'Database connection lost - application may fail', 'database'
            ))
            
        # API response time alerts
        if metrics.api_response_time >= self.thresholds['api_response_critical']:
            alerts.append(self._create_alert(
                'api_performance', 'CRITICAL',
                f'API response time critical: {metrics.api_response_time:.0f}ms', 'api'
            ))
        elif metrics.api_response_time >= self.thresholds['api_response_warning']:
            alerts.append(self._create_alert(
                'api_performance', 'WARNING',
                f'API response time high: {metrics.api_response_time:.0f}ms', 'api'
            ))
            
        # Queue size alerts
        if metrics.queue_size >= self.thresholds['queue_size_critical']:
            alerts.append(self._create_alert(
                'queue_backlog', 'CRITICAL',
                f'Task queue backlog critical: {metrics.queue_size} tasks', 'queue'
            ))
        elif metrics.queue_size >= self.thresholds['queue_size_warning']:
            alerts.append(self._create_alert(
                'queue_backlog', 'WARNING',
                f'Task queue backlog high: {metrics.queue_size} tasks', 'queue'
            ))
            
        # Error rate alerts
        if metrics.error_rate >= self.thresholds['error_rate_critical']:
            alerts.append(self._create_alert(
                'error_rate', 'CRITICAL',
                f'Error rate critical: {metrics.error_rate:.1f}%', 'application'
            ))
        elif metrics.error_rate >= self.thresholds['error_rate_warning']:
            alerts.append(self._create_alert(
                'error_rate', 'WARNING',
                f'Error rate high: {metrics.error_rate:.1f}%', 'application'
            ))
            
        # Queue alerts for processing
        for alert in alerts:
            self.alert_queue.put(alert)

    def _create_alert(self, alert_type: str, severity: str, message: str, component: str) -> SystemAlert:
        """Create a system alert"""
        alert_id = f"{alert_type}_{component}_{int(time.time())}"
        
        return SystemAlert(
            id=alert_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            component=component,
            timestamp=datetime.now(),
            metadata={'threshold_breach': True}
        )

    def _process_alerts(self):
        """Process alerts queue and send notifications"""
        processed_alerts = set()
        
        while self.monitoring_active:
            try:
                # Get alert from queue (wait up to 30 seconds)
                alert = self.alert_queue.get(timeout=30)
                
                # Prevent duplicate alerts within 5 minutes
                alert_key = f"{alert.alert_type}_{alert.component}"
                current_time = time.time()
                
                if alert_key in processed_alerts:
                    continue
                    
                processed_alerts.add(alert_key)
                
                # Store alert
                self._store_alert(alert)
                
                # Send email notification for CRITICAL alerts
                if alert.severity == 'CRITICAL':
                    self._send_alert_email(alert)
                    
                # Clean up processed alerts older than 5 minutes
                cutoff_time = current_time - 300  # 5 minutes
                processed_alerts = {k for k in processed_alerts if not k.endswith(str(int(cutoff_time)))}
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"❌ Error processing alert: {e}")

    def _store_alert(self, alert: SystemAlert):
        """Store alert in database"""
        try:
            with sqlite3.connect(self.alerts_db_path) as conn:
                conn.execute('''
                    INSERT INTO alerts (
                        id, alert_type, severity, message, component,
                        timestamp, resolved, resolution_time, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.id,
                    alert.alert_type,
                    alert.severity,
                    alert.message,
                    alert.component,
                    alert.timestamp.isoformat(),
                    int(alert.resolved),
                    alert.resolution_time.isoformat() if alert.resolution_time else None,
                    json.dumps(alert.metadata) if alert.metadata else None
                ))
                
        except Exception as e:
            logger.error(f"❌ Error storing alert: {e}")

    def _send_alert_email(self, alert: SystemAlert):
        """Send email notification for critical alerts"""
        if not self.smtp_username or not self.smtp_password:
            logger.warning("⚠️ SMTP credentials not configured - cannot send alert emails")
            return
            
        try:
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = ', '.join(self.admin_emails)
            msg['Subject'] = f"🚨 TradeWise AI CRITICAL Alert: {alert.alert_type}"
            
            # Email body
            body = f"""
CRITICAL SYSTEM ALERT - TradeWise AI

Alert Type: {alert.alert_type}
Component: {alert.component}
Severity: {alert.severity}
Timestamp: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

Message: {alert.message}

Please investigate immediately.

This is an automated alert from the TradeWise AI monitoring system.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"✅ Critical alert email sent: {alert.alert_type}")
            
        except Exception as e:
            logger.error(f"❌ Failed to send alert email: {e}")

    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get recent alerts from database"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with sqlite3.connect(self.alerts_db_path) as conn:
                cursor = conn.execute('''
                    SELECT * FROM alerts 
                    WHERE timestamp > ? 
                    ORDER BY timestamp DESC
                ''', (cutoff_time.isoformat(),))
                
                columns = [desc[0] for desc in cursor.description]
                alerts = []
                
                for row in cursor.fetchall():
                    alert_dict = dict(zip(columns, row))
                    # Parse metadata if present
                    if alert_dict['metadata']:
                        alert_dict['metadata'] = json.loads(alert_dict['metadata'])
                    alerts.append(alert_dict)
                    
                return alerts
                
        except Exception as e:
            logger.error(f"❌ Error getting recent alerts: {e}")
            return []

    def get_system_metrics(self, hours: int = 24) -> List[Dict]:
        """Get recent system metrics"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            with sqlite3.connect(self.metrics_db_path) as conn:
                cursor = conn.execute('''
                    SELECT * FROM metrics 
                    WHERE timestamp > ? 
                    ORDER BY timestamp DESC
                ''', (cutoff_time.isoformat(),))
                
                columns = [desc[0] for desc in cursor.description]
                metrics = []
                
                for row in cursor.fetchall():
                    metrics.append(dict(zip(columns, row)))
                    
                return metrics
                
        except Exception as e:
            logger.error(f"❌ Error getting system metrics: {e}")
            return []

    def get_dashboard_summary(self) -> Dict:
        """Get dashboard summary data"""
        try:
            # Get latest metrics
            latest_metrics = self.get_system_metrics(hours=1)
            current_metrics = latest_metrics[0] if latest_metrics else None
            
            # Get recent alerts
            recent_alerts = self.get_recent_alerts(hours=24)
            critical_alerts = [a for a in recent_alerts if a['severity'] == 'CRITICAL' and not a['resolved']]
            
            # System status
            system_status = 'healthy'
            if critical_alerts:
                system_status = 'critical'
            elif any(a['severity'] == 'WARNING' for a in recent_alerts if not a['resolved']):
                system_status = 'warning'
                
            return {
                'system_status': system_status,
                'current_metrics': current_metrics,
                'active_alerts': len([a for a in recent_alerts if not a['resolved']]),
                'critical_alerts': len(critical_alerts),
                'total_alerts_24h': len(recent_alerts),
                'monitoring_active': self.monitoring_active,
                'last_health_check': self.last_health_check.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting dashboard summary: {e}")
            return {'error': str(e)}

# Global monitoring instance
monitoring_system = AdminMonitoringSystem()

# Flask Blueprint for admin endpoints
admin_bp = Blueprint('admin_monitoring', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
def admin_dashboard():
    """Admin monitoring dashboard"""
    try:
        summary = monitoring_system.get_dashboard_summary()
        recent_alerts = monitoring_system.get_recent_alerts(hours=24)
        recent_metrics = monitoring_system.get_system_metrics(hours=6)
        
        return render_template('admin_dashboard.html', 
                             summary=summary,
                             recent_alerts=recent_alerts,
                             recent_metrics=recent_metrics)
    except Exception as e:
        logger.error(f"❌ Admin dashboard error: {e}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/summary')
def api_summary():
    """API endpoint for dashboard summary"""
    return jsonify(monitoring_system.get_dashboard_summary())

@admin_bp.route('/api/alerts')
def api_alerts():
    """API endpoint for recent alerts"""
    hours = request.args.get('hours', 24, type=int)
    return jsonify(monitoring_system.get_recent_alerts(hours))

@admin_bp.route('/api/metrics')
def api_metrics():
    """API endpoint for system metrics"""
    hours = request.args.get('hours', 24, type=int)
    return jsonify(monitoring_system.get_system_metrics(hours))

@admin_bp.route('/api/start-monitoring', methods=['POST'])
def start_monitoring():
    """Start monitoring system"""
    monitoring_system.start_monitoring()
    return jsonify({'success': True, 'message': 'Monitoring started'})

@admin_bp.route('/api/stop-monitoring', methods=['POST'])
def stop_monitoring():
    """Stop monitoring system"""
    monitoring_system.stop_monitoring()
    return jsonify({'success': True, 'message': 'Monitoring stopped'})

@admin_bp.route('/api/test-alert', methods=['POST'])
def test_alert():
    """Test alert system"""
    test_alert = monitoring_system._create_alert(
        'test_alert', 'WARNING', 'This is a test alert', 'admin_test'
    )
    monitoring_system.alert_queue.put(test_alert)
    return jsonify({'success': True, 'message': 'Test alert queued'})

if __name__ == "__main__":
    # Start monitoring when module is run directly
    monitoring_system.start_monitoring()
    print("✅ Admin monitoring system started")