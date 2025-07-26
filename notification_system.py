"""
Critical Error Notification System for TradeWise AI
Sends alerts for critical system errors via Slack and Email
"""

import os
import logging
import smtplib
import requests
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
import traceback

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manages critical error notifications"""
    
    def __init__(self):
        self.enabled = os.getenv('ERROR_NOTIFICATIONS_ENABLED', 'false').lower() == 'true'
        self.slack_webhook = os.getenv('SLACK_ERROR_WEBHOOK')
        self.email_config = self._get_email_config()
        
    def _get_email_config(self) -> Optional[Dict[str, str]]:
        """Get email configuration from environment"""
        config = {
            'smtp_server': os.getenv('SMTP_SERVER'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'smtp_user': os.getenv('SMTP_USER'),
            'smtp_password': os.getenv('SMTP_PASSWORD'),
            'error_email': os.getenv('ERROR_EMAIL')
        }
        
        # Return None if any required config is missing
        if not all([config['smtp_server'], config['smtp_user'], 
                   config['smtp_password'], config['error_email']]):
            return None
            
        return config
    
    def send_critical_alert(self, error: Exception, context: Dict[str, Any] = None):
        """Send critical error alert via all configured channels"""
        if not self.enabled:
            logger.debug("Error notifications disabled - skipping alert")
            return
            
        error_info = {
            'error_type': type(error).__name__,
            'message': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'stack_trace': traceback.format_exc(),
            'context': context or {}
        }
        
        # Send Slack notification
        if self.slack_webhook:
            try:
                self._send_slack_alert(error_info)
                logger.info("Critical error alert sent to Slack")
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {e}")
        
        # Send email notification
        if self.email_config:
            try:
                self._send_email_alert(error_info)
                logger.info("Critical error alert sent via email")
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
    
    def _send_slack_alert(self, error_info: Dict[str, Any]):
        """Send Slack notification for critical errors"""
        severity_color = self._get_severity_color(error_info['error_type'])
        
        message = {
            "text": "🚨 TradeWise AI Critical Error Alert",
            "attachments": [
                {
                    "color": severity_color,
                    "title": f"Critical Error: {error_info['error_type']}",
                    "fields": [
                        {
                            "title": "Error Message",
                            "value": error_info['message'][:500],
                            "short": False
                        },
                        {
                            "title": "Timestamp",
                            "value": error_info['timestamp'],
                            "short": True
                        },
                        {
                            "title": "Context",
                            "value": str(error_info['context'])[:200] if error_info['context'] else "None",
                            "short": True
                        }
                    ],
                    "footer": "TradeWise AI Error Monitor",
                    "ts": int(datetime.utcnow().timestamp())
                }
            ]
        }
        
        response = requests.post(
            self.slack_webhook,
            json=message,
            timeout=10
        )
        response.raise_for_status()
    
    def _send_email_alert(self, error_info: Dict[str, Any]):
        """Send email notification for critical errors"""
        msg = MIMEMultipart()
        msg['From'] = self.email_config['smtp_user']
        msg['To'] = self.email_config['error_email']
        msg['Subject'] = f"🚨 TradeWise AI Critical Error - {error_info['error_type']}"
        
        body = f"""
Critical Error Alert - TradeWise AI Platform

Error Details:
═══════════════════════════════════════
Error Type: {error_info['error_type']}
Message: {error_info['message']}
Timestamp: {error_info['timestamp']}

Context Information:
{self._format_context(error_info['context'])}

Stack Trace:
{error_info['stack_trace']}

═══════════════════════════════════════
This is an automated alert from TradeWise AI error monitoring system.
Please investigate this issue immediately.

Platform Status: https://your-domain.com/api/health
Error Logs: Check logs/errors.log for additional details
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
        server.starttls()
        server.login(self.email_config['smtp_user'], self.email_config['smtp_password'])
        server.send_message(msg)
        server.quit()
    
    def _get_severity_color(self, error_type: str) -> str:
        """Get color code based on error severity"""
        critical_errors = ['DatabaseError', 'ConnectionError', 'RedisError', 'SystemError']
        warning_errors = ['TimeoutError', 'RateLimitError', 'ValidationError']
        
        if any(critical in error_type for critical in critical_errors):
            return "#ff0000"  # Red
        elif any(warning in error_type for warning in warning_errors):
            return "#ff9900"  # Orange
        else:
            return "#ffcc00"  # Yellow
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context information for email"""
        if not context:
            return "No additional context available"
            
        formatted = []
        for key, value in context.items():
            formatted.append(f"  {key}: {value}")
        
        return "\n".join(formatted)
    
    def send_system_health_alert(self, component: str, status: str, details: str = ""):
        """Send system health monitoring alert"""
        if not self.enabled:
            return
            
        alert_info = {
            'component': component,
            'status': status,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if status in ['DOWN', 'CRITICAL', 'FAILED']:
            # Send critical alert
            if self.slack_webhook:
                self._send_slack_health_alert(alert_info)
            if self.email_config:
                self._send_email_health_alert(alert_info)
    
    def _send_slack_health_alert(self, alert_info: Dict[str, Any]):
        """Send Slack health monitoring alert"""
        color = "#ff0000" if alert_info['status'] in ['DOWN', 'CRITICAL'] else "#ff9900"
        
        message = {
            "text": f"⚠️ TradeWise AI Health Alert - {alert_info['component']}",
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": "Component",
                            "value": alert_info['component'],
                            "short": True
                        },
                        {
                            "title": "Status",
                            "value": alert_info['status'],
                            "short": True
                        },
                        {
                            "title": "Details",
                            "value": alert_info['details'] or "No additional details",
                            "short": False
                        }
                    ]
                }
            ]
        }
        
        requests.post(self.slack_webhook, json=message, timeout=10)
    
    def _send_email_health_alert(self, alert_info: Dict[str, Any]):
        """Send email health monitoring alert"""
        msg = MIMEMultipart()
        msg['From'] = self.email_config['smtp_user']
        msg['To'] = self.email_config['error_email']
        msg['Subject'] = f"⚠️ TradeWise AI Health Alert - {alert_info['component']} {alert_info['status']}"
        
        body = f"""
System Health Alert - TradeWise AI Platform

Component: {alert_info['component']}
Status: {alert_info['status']}
Timestamp: {alert_info['timestamp']}

Details:
{alert_info['details'] or 'No additional details available'}

Please investigate this issue and take appropriate action.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
        server.starttls()
        server.login(self.email_config['smtp_user'], self.email_config['smtp_password'])
        server.send_message(msg)
        server.quit()

# Global notification manager instance
notification_manager = NotificationManager()

def send_critical_error_alert(error: Exception, context: Dict[str, Any] = None):
    """Global function to send critical error alerts"""
    notification_manager.send_critical_alert(error, context)

def send_health_alert(component: str, status: str, details: str = ""):
    """Global function to send health monitoring alerts"""
    notification_manager.send_system_health_alert(component, status, details)