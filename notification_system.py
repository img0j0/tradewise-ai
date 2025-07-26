"""
Email Notification System - Phase 5
Handles email notifications for plan upgrades/downgrades and alert triggers
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class EmailNotificationService:
    """Service for sending email notifications"""
    
    def __init__(self):
        # Email configuration - using environment variables for security
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_address = os.getenv('NOTIFICATION_EMAIL', 'tradewise.founder@gmail.com')
        self.email_password = os.getenv('NOTIFICATION_EMAIL_PASSWORD', '')
        self.from_name = "TradeWise AI"
        
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send an email notification"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.email_address}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text version if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                if self.email_password:
                    server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent successfully to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_upgrade_notification(self, user_email: str, user_name: str, old_plan: str, new_plan: str, amount: float = None) -> bool:
        """Send plan upgrade notification email"""
        
        # Email subject
        subject = f"Welcome to TradeWise AI {new_plan}! Your upgrade is complete"
        
        # HTML email template
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Upgrade Confirmation</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f5f5f7; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                .header {{ background: linear-gradient(135deg, #1d3557, #457b9d); color: white; padding: 32px 24px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; font-weight: 700; }}
                .header .crown {{ font-size: 48px; margin-bottom: 16px; }}
                .content {{ padding: 32px 24px; }}
                .welcome-box {{ background: #f9fafb; border-left: 4px solid #10b981; padding: 20px; margin: 24px 0; border-radius: 8px; }}
                .features {{ background: #f8fafc; padding: 24px; border-radius: 12px; margin: 24px 0; }}
                .features h3 {{ color: #1d3557; margin-bottom: 16px; }}
                .feature-list {{ list-style: none; padding: 0; margin: 0; }}
                .feature-item {{ display: flex; align-items: center; padding: 8px 0; color: #374151; }}
                .feature-item::before {{ content: '✓'; color: #10b981; font-weight: bold; margin-right: 12px; }}
                .cta-button {{ display: inline-block; background: linear-gradient(135deg, #1d3557, #457b9d); color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 24px 0; text-align: center; }}
                .footer {{ background: #f9fafb; padding: 24px; text-align: center; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; }}
                .upgrade-details {{ background: white; border: 2px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .plan-change {{ font-size: 18px; text-align: center; margin: 16px 0; }}
                .plan-old {{ color: #6b7280; text-decoration: line-through; }}
                .plan-new {{ color: #1d3557; font-weight: 700; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="crown">👑</div>
                    <h1>Upgrade Successful!</h1>
                    <p>Welcome to TradeWise AI {new_plan}</p>
                </div>
                
                <div class="content">
                    <div class="welcome-box">
                        <h2 style="margin-top: 0; color: #1d3557;">Hi {user_name},</h2>
                        <p>Thank you for upgrading to <strong>TradeWise AI {new_plan}</strong>! Your account has been successfully upgraded and you now have access to all premium features.</p>
                    </div>
                    
                    <div class="upgrade-details">
                        <div class="plan-change">
                            <span class="plan-old">{old_plan}</span> → <span class="plan-new">{new_plan}</span>
                        </div>
                        {f'<p style="text-align: center; color: #6b7280;">Billing: ${amount:.2f}/month</p>' if amount else ''}
                        <p style="text-align: center; color: #6b7280;">Upgrade Date: {datetime.now().strftime('%B %d, %Y')}</p>
                    </div>
                    
                    <div class="features">
                        <h3>🚀 Your Premium Features Are Now Active:</h3>
                        <ul class="feature-list">
                            <li class="feature-item">Advanced AI-powered stock analysis</li>
                            <li class="feature-item">Unlimited portfolio backtesting</li>
                            <li class="feature-item">Comprehensive peer comparisons</li>
                            <li class="feature-item">Smart alerts and notifications</li>
                            <li class="feature-item">Real-time market intelligence</li>
                            <li class="feature-item">Priority customer support</li>
                            <li class="feature-item">Early access to new features</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="https://{os.getenv('REPLIT_DEV_DOMAIN', 'tradewise-ai.replit.app')}" class="cta-button">
                            Start Using Your Premium Features →
                        </a>
                    </div>
                    
                    <p style="margin-top: 32px; color: #6b7280;">
                        Questions? Reply to this email or contact us at 
                        <a href="mailto:tradewise.founder@gmail.com" style="color: #1d3557;">tradewise.founder@gmail.com</a>
                    </p>
                </div>
                
                <div class="footer">
                    <p><strong>TradeWise AI</strong> - Professional Stock Analysis Platform</p>
                    <p>by SignalStackDev | tradewise.founder@gmail.com | 631-810-9473</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Text version
        text_content = f"""
        Welcome to TradeWise AI {new_plan}!
        
        Hi {user_name},
        
        Thank you for upgrading to TradeWise AI {new_plan}! Your account has been successfully upgraded.
        
        Plan Change: {old_plan} → {new_plan}
        {f'Billing: ${amount:.2f}/month' if amount else ''}
        Upgrade Date: {datetime.now().strftime('%B %d, %Y')}
        
        Your Premium Features Are Now Active:
        ✓ Advanced AI-powered stock analysis
        ✓ Unlimited portfolio backtesting
        ✓ Comprehensive peer comparisons  
        ✓ Smart alerts and notifications
        ✓ Real-time market intelligence
        ✓ Priority customer support
        ✓ Early access to new features
        
        Start using your premium features: https://{os.getenv('REPLIT_DEV_DOMAIN', 'tradewise-ai.replit.app')}
        
        Questions? Contact us at tradewise.founder@gmail.com
        
        TradeWise AI Team
        """
        
        return self.send_email(user_email, subject, html_content, text_content)
    
    def send_downgrade_notification(self, user_email: str, user_name: str, old_plan: str, new_plan: str) -> bool:
        """Send plan downgrade notification email"""
        
        subject = f"TradeWise AI Plan Updated to {new_plan}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Plan Change Confirmation</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f5f5f7; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                .header {{ background: linear-gradient(135deg, #6b7280, #9ca3af); color: white; padding: 32px 24px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; }}
                .content {{ padding: 32px 24px; }}
                .info-box {{ background: #f3f4f6; border-left: 4px solid #6b7280; padding: 20px; margin: 24px 0; border-radius: 8px; }}
                .footer {{ background: #f9fafb; padding: 24px; text-align: center; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; }}
                .cta-button {{ display: inline-block; background: #1d3557; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 16px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Plan Change Confirmation</h1>
                    <p>Your TradeWise AI plan has been updated</p>
                </div>
                
                <div class="content">
                    <div class="info-box">
                        <h2 style="margin-top: 0; color: #374151;">Hi {user_name},</h2>
                        <p>Your TradeWise AI plan has been successfully changed from <strong>{old_plan}</strong> to <strong>{new_plan}</strong>.</p>
                        <p>Change Date: {datetime.now().strftime('%B %d, %Y')}</p>
                    </div>
                    
                    <p>Thank you for using TradeWise AI! You can still access our core stock analysis features and upgrade again anytime.</p>
                    
                    <div style="text-align: center;">
                        <a href="https://{os.getenv('REPLIT_DEV_DOMAIN', 'tradewise-ai.replit.app')}" class="cta-button">
                            Continue Using TradeWise AI
                        </a>
                    </div>
                    
                    <p style="margin-top: 32px; color: #6b7280;">
                        Questions? Contact us at 
                        <a href="mailto:tradewise.founder@gmail.com" style="color: #1d3557;">tradewise.founder@gmail.com</a>
                    </p>
                </div>
                
                <div class="footer">
                    <p><strong>TradeWise AI</strong> - Professional Stock Analysis Platform</p>
                    <p>by SignalStackDev | tradewise.founder@gmail.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)
    
    def send_alert_notification(self, user_email: str, user_name: str, alert_data: Dict) -> bool:
        """Send alert trigger notification email"""
        
        symbol = alert_data.get('symbol', 'Stock')
        alert_type = alert_data.get('type', 'Price')
        current_value = alert_data.get('current_value', 'N/A')
        target_value = alert_data.get('target_value', 'N/A')
        message = alert_data.get('message', 'Alert condition met')
        
        subject = f"🚨 TradeWise AI Alert: {symbol} {alert_type} Alert Triggered"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Alert Triggered</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f5f5f7; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; }}
                .header {{ background: linear-gradient(135deg, #f59e0b, #d97706); color: white; padding: 32px 24px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; }}
                .alert-icon {{ font-size: 48px; margin-bottom: 16px; }}
                .content {{ padding: 32px 24px; }}
                .alert-box {{ background: #fef3c7; border: 2px solid #f59e0b; border-radius: 8px; padding: 20px; margin: 24px 0; }}
                .alert-details {{ background: #f9fafb; padding: 20px; border-radius: 8px; margin: 16px 0; }}
                .footer {{ background: #f9fafb; padding: 24px; text-align: center; color: #6b7280; font-size: 14px; border-top: 1px solid #e5e7eb; }}
                .cta-button {{ display: inline-block; background: #1d3557; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 16px 0; }}
                .symbol {{ font-size: 20px; font-weight: 700; color: #1d3557; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="alert-icon">🚨</div>
                    <h1>Alert Triggered!</h1>
                    <p class="symbol">{symbol}</p>
                </div>
                
                <div class="content">
                    <div class="alert-box">
                        <h2 style="margin-top: 0; color: #92400e;">Hi {user_name},</h2>
                        <p><strong>Your {alert_type.lower()} alert for {symbol} has been triggered!</strong></p>
                        <p>{message}</p>
                    </div>
                    
                    <div class="alert-details">
                        <h3 style="color: #374151; margin-bottom: 12px;">Alert Details:</h3>
                        <p><strong>Symbol:</strong> {symbol}</p>
                        <p><strong>Alert Type:</strong> {alert_type}</p>
                        <p><strong>Target Value:</strong> {target_value}</p>
                        <p><strong>Current Value:</strong> {current_value}</p>
                        <p><strong>Triggered:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p UTC')}</p>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="https://{os.getenv('REPLIT_DEV_DOMAIN', 'tradewise-ai.replit.app')}/search?q={symbol}" class="cta-button">
                            Analyze {symbol} Now →
                        </a>
                    </div>
                    
                    <p style="margin-top: 24px; color: #6b7280; font-size: 14px;">
                        <strong>Next Steps:</strong> Consider reviewing your position and market conditions. 
                        Use our AI analysis tools to get comprehensive insights.
                    </p>
                </div>
                
                <div class="footer">
                    <p><strong>TradeWise AI</strong> - Smart Alert System</p>
                    <p>Manage your alerts: <a href="https://{os.getenv('REPLIT_DEV_DOMAIN', 'tradewise-ai.replit.app')}/alerts">View All Alerts</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_content)

# Global notification service instance
notification_service = EmailNotificationService()

def send_upgrade_email(user_email: str, user_name: str, old_plan: str, new_plan: str, amount: float = None) -> bool:
    """Convenience function to send upgrade notification"""
    return notification_service.send_upgrade_notification(user_email, user_name, old_plan, new_plan, amount)

def send_downgrade_email(user_email: str, user_name: str, old_plan: str, new_plan: str) -> bool:
    """Convenience function to send downgrade notification"""
    return notification_service.send_downgrade_notification(user_email, user_name, old_plan, new_plan)

def send_alert_email(user_email: str, user_name: str, alert_data: Dict) -> bool:
    """Convenience function to send alert notification"""
    return notification_service.send_alert_notification(user_email, user_name, alert_data)