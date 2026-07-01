#!/usr/bin/env python3
"""
Email Notification Manager Component
Handles email notifications for stock alerts, target hits, and stop losses.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AlertType(Enum):
    """Types of alerts that can be sent."""
    TARGET_HIT = "target_hit"
    STOP_LOSS_HIT = "stop_loss_hit"
    SIGNIFICANT_MOVEMENT = "significant_movement"
    DAILY_SUMMARY = "daily_summary"
    RISK_ALERT = "risk_alert"
    SWING_PLAN_UPDATE = "swing_plan_update"

class AlertPriority(Enum):
    """Priority levels for alerts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class NotificationSettings:
    """User notification preferences."""
    email_enabled: bool = True
    target_hit_alerts: bool = True
    stop_loss_alerts: bool = True
    significant_movement_alerts: bool = True
    daily_summary: bool = True
    risk_alerts: bool = True
    swing_plan_updates: bool = True
    
    # Thresholds
    significant_movement_threshold: float = 5.0  # 5% price movement
    daily_summary_time: str = "18:00"  # 6 PM
    max_alerts_per_hour: int = 10
    
    # Email settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""
    recipient_email: str = ""

class EmailNotificationManager:
    """Manages email notifications for stock trading alerts."""
    
    def __init__(self, settings_file: str = "notification_settings.json"):
        self.settings_file = settings_file
        self.settings = self._load_settings()
        self.alert_history = self._load_alert_history()
        self.last_alert_times = {}  # Track last alert time per stock to prevent spam
        
        logger.info("EmailNotificationManager initialized")
    
    def _load_settings(self) -> NotificationSettings:
        """Load notification settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    return NotificationSettings(**data)
            else:
                # Create default settings
                default_settings = NotificationSettings()
                self._save_settings(default_settings)
                return default_settings
        except Exception as e:
            logger.error(f"Error loading notification settings: {str(e)}")
            return NotificationSettings()
    
    def _save_settings(self, settings: NotificationSettings):
        """Save notification settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings.__dict__, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving notification settings: {str(e)}")
    
    def _load_alert_history(self) -> List[Dict]:
        """Load alert history from file."""
        try:
            history_file = "alert_history.json"
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading alert history: {str(e)}")
            return []
    
    def _save_alert_history(self):
        """Save alert history to file."""
        try:
            history_file = "alert_history.json"
            with open(history_file, 'w') as f:
                json.dump(self.alert_history, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving alert history: {str(e)}")
    
    def update_settings(self, **kwargs) -> bool:
        """Update notification settings."""
        try:
            for key, value in kwargs.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)
            
            self._save_settings(self.settings)
            logger.info("Notification settings updated")
            return True
        except Exception as e:
            logger.error(f"Error updating settings: {str(e)}")
            return False
    
    def test_email_connection(self) -> Dict:
        """Test email connection and authentication."""
        try:
            if not self.settings.sender_email or not self.settings.sender_password:
                return {
                    'success': False,
                    'message': 'Email credentials not configured'
                }
            
            # Test SMTP connection
            server = smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port)
            server.starttls()
            server.login(self.settings.sender_email, self.settings.sender_password)
            server.quit()
            
            return {
                'success': True,
                'message': 'Email connection successful'
            }
        except Exception as e:
            logger.error(f"Email connection test failed: {str(e)}")
            return {
                'success': False,
                'message': f'Email connection failed: {str(e)}'
            }
    
    def _can_send_alert(self, symbol: str, alert_type: AlertType) -> bool:
        """Check if we can send an alert (rate limiting)."""
        try:
            current_time = datetime.now()
            alert_key = f"{symbol}_{alert_type.value}"
            
            # Check if we've sent this alert recently (within 1 hour for same type)
            if alert_key in self.last_alert_times:
                last_alert = self.last_alert_times[alert_key]
                if (current_time - last_alert).total_seconds() < 3600:  # 1 hour
                    return False
            
            # Check total alerts per hour
            recent_alerts = [
                alert for alert in self.alert_history
                if (current_time - datetime.fromisoformat(alert['timestamp'])).total_seconds() < 3600
            ]
            
            if len(recent_alerts) >= self.settings.max_alerts_per_hour:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking alert rate limit: {str(e)}")
            return True  # Allow alert if check fails
    
    def _create_email_template(self, alert_type: AlertType, stock_data: Dict, 
                             additional_data: Dict = None) -> tuple:
        """Create email subject and body based on alert type."""
        symbol = stock_data.get('symbol', 'UNKNOWN')
        current_price = stock_data.get('current_price', 0)
        company_name = stock_data.get('company_name', '')
        
        # Base subject prefix
        subject_prefix = "🚨 Stock Alert"
        
        if alert_type == AlertType.TARGET_HIT:
            target_price = stock_data.get('target_price', 0)
            profit_percent = ((current_price - stock_data.get('entry_price', current_price)) / stock_data.get('entry_price', 1)) * 100
            
            subject = f"{subject_prefix}: {symbol} Target Hit! 🎯"
            body = f"""
            <h2>🎯 Target Price Hit!</h2>
            <p><strong>Stock:</strong> {symbol} - {company_name}</p>
            <p><strong>Current Price:</strong> ₹{current_price:.2f}</p>
            <p><strong>Target Price:</strong> ₹{target_price:.2f}</p>
            <p><strong>Profit:</strong> {profit_percent:.2f}%</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h3>📊 Trading Details:</h3>
            <ul>
                <li><strong>Entry Price:</strong> ₹{stock_data.get('entry_price', 0):.2f}</li>
                <li><strong>Stop Loss:</strong> ₹{stock_data.get('stop_loss', 0):.2f}</li>
                <li><strong>Position Size:</strong> {stock_data.get('position_size', 0)} shares</li>
                <li><strong>Investment:</strong> ₹{stock_data.get('investment_amount', 0):,.0f}</li>
            </ul>
            
            <p><strong>Action Required:</strong> Consider taking profits or adjusting stop loss to protect gains.</p>
            """
            
        elif alert_type == AlertType.STOP_LOSS_HIT:
            stop_loss = stock_data.get('stop_loss', 0)
            loss_percent = ((current_price - stock_data.get('entry_price', current_price)) / stock_data.get('entry_price', 1)) * 100
            
            subject = f"{subject_prefix}: {symbol} Stop Loss Hit! 🛑"
            body = f"""
            <h2>🛑 Stop Loss Hit!</h2>
            <p><strong>Stock:</strong> {symbol} - {company_name}</p>
            <p><strong>Current Price:</strong> ₹{current_price:.2f}</p>
            <p><strong>Stop Loss:</strong> ₹{stop_loss:.2f}</p>
            <p><strong>Loss:</strong> {loss_percent:.2f}%</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h3>📊 Trading Details:</h3>
            <ul>
                <li><strong>Entry Price:</strong> ₹{stock_data.get('entry_price', 0):.2f}</li>
                <li><strong>Target Price:</strong> ₹{stock_data.get('target_price', 0):.2f}</li>
                <li><strong>Position Size:</strong> {stock_data.get('position_size', 0)} shares</li>
                <li><strong>Investment:</strong> ₹{stock_data.get('investment_amount', 0):,.0f}</li>
            </ul>
            
            <p><strong>Action Required:</strong> Consider exiting position to limit further losses.</p>
            """
            
        elif alert_type == AlertType.SIGNIFICANT_MOVEMENT:
            movement_percent = additional_data.get('movement_percent', 0)
            direction = "📈 Up" if movement_percent > 0 else "📉 Down"
            
            subject = f"{subject_prefix}: {symbol} Significant Movement {direction}"
            body = f"""
            <h2>📊 Significant Price Movement</h2>
            <p><strong>Stock:</strong> {symbol} - {company_name}</p>
            <p><strong>Current Price:</strong> ₹{current_price:.2f}</p>
            <p><strong>Movement:</strong> {movement_percent:.2f}% {direction}</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h3>📊 Current Levels:</h3>
            <ul>
                <li><strong>Entry Price:</strong> ₹{stock_data.get('entry_price', 0):.2f}</li>
                <li><strong>Target Price:</strong> ₹{stock_data.get('target_price', 0):.2f}</li>
                <li><strong>Stop Loss:</strong> ₹{stock_data.get('stop_loss', 0):.2f}</li>
            </ul>
            
            <p><strong>Note:</strong> This movement exceeds your {self.settings.significant_movement_threshold}% threshold.</p>
            """
            
        elif alert_type == AlertType.DAILY_SUMMARY:
            subject = f"📊 Daily Trading Summary - {datetime.now().strftime('%Y-%m-%d')}"
            body = f"""
            <h2>📊 Daily Trading Summary</h2>
            <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
            
            <h3>📈 Portfolio Overview:</h3>
            {additional_data.get('portfolio_summary', 'No data available')}
            
            <h3>🎯 Active Positions:</h3>
            {additional_data.get('active_positions', 'No active positions')}
            
            <h3>📰 Market News:</h3>
            {additional_data.get('market_news', 'No news available')}
            
            <p><em>This is an automated daily summary from your Stock Trading App.</em></p>
            """
            
        elif alert_type == AlertType.RISK_ALERT:
            risk_reason = additional_data.get('risk_reason', 'Unknown risk detected')
            subject = f"{subject_prefix}: {symbol} Risk Alert! ⚠️"
            body = f"""
            <h2>⚠️ Risk Alert</h2>
            <p><strong>Stock:</strong> {symbol} - {company_name}</p>
            <p><strong>Current Price:</strong> ₹{current_price:.2f}</p>
            <p><strong>Risk Reason:</strong> {risk_reason}</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h3>📊 Current Position:</h3>
            <ul>
                <li><strong>Entry Price:</strong> ₹{stock_data.get('entry_price', 0):.2f}</li>
                <li><strong>Target Price:</strong> ₹{stock_data.get('target_price', 0):.2f}</li>
                <li><strong>Stop Loss:</strong> ₹{stock_data.get('stop_loss', 0):.2f}</li>
                <li><strong>Position Size:</strong> {stock_data.get('position_size', 0)} shares</li>
            </ul>
            
            <p><strong>Action Required:</strong> Review position and consider risk management actions.</p>
            """
            
        else:  # SWING_PLAN_UPDATE
            subject = f"📈 Swing Plan Update: {symbol}"
            body = f"""
            <h2>📈 Swing Trading Plan Update</h2>
            <p><strong>Stock:</strong> {symbol} - {company_name}</p>
            <p><strong>Current Price:</strong> ₹{current_price:.2f}</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h3>📊 Updated Plan:</h3>
            {additional_data.get('plan_details', 'No plan details available')}
            
            <p><em>This is an automated update from your Swing Trading Strategy.</em></p>
            """
        
        return subject, body
    
    def send_alert(self, alert_type: AlertType, stock_data: Dict, 
                   additional_data: Dict = None, priority: AlertPriority = AlertPriority.MEDIUM) -> bool:
        """Send email alert for stock event."""
        try:
            # Check if email notifications are enabled
            if not self.settings.email_enabled:
                logger.info("Email notifications disabled")
                return False
            
            # Check if this specific alert type is enabled
            alert_enabled = getattr(self.settings, f"{alert_type.value}_alerts", True)
            if not alert_enabled:
                logger.info(f"{alert_type.value} alerts disabled")
                return False
            
            # Check rate limiting
            symbol = stock_data.get('symbol', 'UNKNOWN')
            if not self._can_send_alert(symbol, alert_type):
                logger.info(f"Rate limit reached for {symbol} {alert_type.value}")
                return False
            
            # Create email content
            subject, body = self._create_email_template(alert_type, stock_data, additional_data)
            
            # Send email
            success = self._send_email(subject, body, priority)
            
            if success:
                # Record alert in history
                alert_record = {
                    'timestamp': datetime.now().isoformat(),
                    'alert_type': alert_type.value,
                    'symbol': symbol,
                    'priority': priority.value,
                    'subject': subject
                }
                self.alert_history.append(alert_record)
                self._save_alert_history()
                
                # Update last alert time
                alert_key = f"{symbol}_{alert_type.value}"
                self.last_alert_times[alert_key] = datetime.now()
                
                logger.info(f"Alert sent successfully: {alert_type.value} for {symbol}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending alert: {str(e)}")
            return False
    
    def _send_email(self, subject: str, body: str, priority: AlertPriority = AlertPriority.MEDIUM) -> bool:
        """Send email using SMTP."""
        try:
            if not self.settings.sender_email or not self.settings.sender_password:
                logger.error("Email credentials not configured")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.settings.sender_email
            msg['To'] = self.settings.recipient_email
            msg['Subject'] = subject
            
            # Add priority header
            priority_headers = {
                AlertPriority.LOW: "3",
                AlertPriority.MEDIUM: "3",
                AlertPriority.HIGH: "2",
                AlertPriority.CRITICAL: "1"
            }
            msg['X-Priority'] = priority_headers.get(priority, "3")
            
            # Create HTML body
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                    .alert-box {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                    .success-box {{ background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                    .error-box {{ background: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 Stock Trading App</h1>
                        <p>Automated Trading Alert</p>
                    </div>
                    <div class="content">
                        {body}
                    </div>
                    <div class="footer">
                        <p>This is an automated message from your Stock Trading App.</p>
                        <p>To manage your notification preferences, please log into the app.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.settings.smtp_server, self.settings.smtp_port)
            server.starttls()
            server.login(self.settings.sender_email, self.settings.sender_password)
            
            text = msg.as_string()
            server.sendmail(self.settings.sender_email, self.settings.recipient_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """Get recent alert history."""
        try:
            # Sort by timestamp (newest first) and limit results
            sorted_history = sorted(
                self.alert_history, 
                key=lambda x: x['timestamp'], 
                reverse=True
            )
            return sorted_history[:limit]
        except Exception as e:
            logger.error(f"Error getting alert history: {str(e)}")
            return []
    
    def clear_alert_history(self) -> bool:
        """Clear alert history."""
        try:
            self.alert_history = []
            self._save_alert_history()
            logger.info("Alert history cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing alert history: {str(e)}")
            return False
