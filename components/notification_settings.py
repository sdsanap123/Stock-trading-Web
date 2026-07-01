#!/usr/bin/env python3
"""
Notification Settings Manager Component
Manages user notification preferences and settings.
"""

import logging
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class NotificationChannel(Enum):
    """Available notification channels."""
    EMAIL = "email"
    BROWSER = "browser"
    SMS = "sms"
    TELEGRAM = "telegram"
    DISCORD = "discord"

class AlertFrequency(Enum):
    """Alert frequency options."""
    IMMEDIATE = "immediate"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"

@dataclass
class AlertThresholds:
    """Alert threshold settings."""
    significant_movement_percent: float = 5.0
    target_hit_tolerance: float = 0.5  # 0.5% tolerance for target hits
    stop_loss_tolerance: float = 0.5   # 0.5% tolerance for stop loss hits
    risk_alert_threshold: float = 10.0  # 10% loss triggers risk alert
    max_alerts_per_hour: int = 10
    max_alerts_per_day: int = 50

@dataclass
class ChannelSettings:
    """Settings for a specific notification channel."""
    enabled: bool = False
    priority: str = "medium"  # low, medium, high, critical
    frequency: str = "immediate"
    custom_settings: Dict = None
    
    def __post_init__(self):
        if self.custom_settings is None:
            self.custom_settings = {}

@dataclass
class NotificationPreferences:
    """User notification preferences."""
    # Global settings
    notifications_enabled: bool = True
    quiet_hours_start: str = "22:00"  # 10 PM
    quiet_hours_end: str = "08:00"    # 8 AM
    timezone: str = "Asia/Kolkata"
    
    # Alert type preferences
    target_hit_alerts: bool = True
    stop_loss_alerts: bool = True
    significant_movement_alerts: bool = True
    daily_summary: bool = True
    risk_alerts: bool = True
    swing_plan_updates: bool = True
    news_alerts: bool = False
    
    # Channel settings
    email_settings: ChannelSettings = None
    browser_settings: ChannelSettings = None
    sms_settings: ChannelSettings = None
    telegram_settings: ChannelSettings = None
    discord_settings: ChannelSettings = None
    
    # Thresholds
    thresholds: AlertThresholds = None
    
    # Portfolio settings
    portfolio_alerts: bool = True
    watchlist_alerts: bool = True
    swing_trading_alerts: bool = True
    
    def __post_init__(self):
        if self.email_settings is None:
            self.email_settings = ChannelSettings(enabled=True, priority="high")
        if self.browser_settings is None:
            self.browser_settings = ChannelSettings(enabled=True, priority="medium")
        if self.sms_settings is None:
            self.sms_settings = ChannelSettings(enabled=False, priority="critical")
        if self.telegram_settings is None:
            self.telegram_settings = ChannelSettings(enabled=False, priority="medium")
        if self.discord_settings is None:
            self.discord_settings = ChannelSettings(enabled=False, priority="low")
        if self.thresholds is None:
            self.thresholds = AlertThresholds()

class NotificationSettingsManager:
    """Manages notification settings and preferences."""
    
    def __init__(self, settings_file: str = "notification_preferences.json"):
        self.settings_file = settings_file
        self.preferences = self._load_preferences()
        self.default_templates = self._load_default_templates()
        
        logger.info("NotificationSettingsManager initialized")
    
    def _load_preferences(self) -> NotificationPreferences:
        """Load notification preferences from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    return self._dict_to_preferences(data)
            else:
                # Create default preferences
                default_prefs = NotificationPreferences()
                self._save_preferences(default_prefs)
                return default_prefs
        except Exception as e:
            logger.error(f"Error loading notification preferences: {str(e)}")
            return NotificationPreferences()
    
    def _save_preferences(self, preferences: NotificationPreferences):
        """Save notification preferences to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self._preferences_to_dict(preferences), f, indent=4)
        except Exception as e:
            logger.error(f"Error saving notification preferences: {str(e)}")
    
    def _preferences_to_dict(self, preferences: NotificationPreferences) -> Dict:
        """Convert preferences to dictionary for JSON serialization."""
        try:
            data = asdict(preferences)
            return data
        except Exception as e:
            logger.error(f"Error converting preferences to dict: {str(e)}")
            return {}
    
    def _dict_to_preferences(self, data: Dict) -> NotificationPreferences:
        """Convert dictionary to preferences object."""
        try:
            # Handle nested objects
            if 'email_settings' in data and isinstance(data['email_settings'], dict):
                data['email_settings'] = ChannelSettings(**data['email_settings'])
            
            if 'browser_settings' in data and isinstance(data['browser_settings'], dict):
                data['browser_settings'] = ChannelSettings(**data['browser_settings'])
            
            if 'sms_settings' in data and isinstance(data['sms_settings'], dict):
                data['sms_settings'] = ChannelSettings(**data['sms_settings'])
            
            if 'telegram_settings' in data and isinstance(data['telegram_settings'], dict):
                data['telegram_settings'] = ChannelSettings(**data['telegram_settings'])
            
            if 'discord_settings' in data and isinstance(data['discord_settings'], dict):
                data['discord_settings'] = ChannelSettings(**data['discord_settings'])
            
            if 'thresholds' in data and isinstance(data['thresholds'], dict):
                data['thresholds'] = AlertThresholds(**data['thresholds'])
            
            return NotificationPreferences(**data)
        except Exception as e:
            logger.error(f"Error converting dict to preferences: {str(e)}")
            return NotificationPreferences()
    
    def _load_default_templates(self) -> Dict:
        """Load default email templates."""
        return {
            'target_hit': {
                'subject': '🎯 Target Price Hit: {symbol}',
                'priority': 'high',
                'template': 'target_hit_template.html'
            },
            'stop_loss_hit': {
                'subject': '🛑 Stop Loss Hit: {symbol}',
                'priority': 'critical',
                'template': 'stop_loss_template.html'
            },
            'significant_movement': {
                'subject': '📊 Significant Movement: {symbol}',
                'priority': 'medium',
                'template': 'movement_template.html'
            },
            'daily_summary': {
                'subject': '📊 Daily Trading Summary - {date}',
                'priority': 'low',
                'template': 'daily_summary_template.html'
            },
            'risk_alert': {
                'subject': '⚠️ Risk Alert: {symbol}',
                'priority': 'critical',
                'template': 'risk_alert_template.html'
            },
            'swing_plan_update': {
                'subject': '📈 Swing Plan Update: {symbol}',
                'priority': 'medium',
                'template': 'swing_update_template.html'
            }
        }
    
    def update_preferences(self, **kwargs) -> bool:
        """Update notification preferences."""
        try:
            for key, value in kwargs.items():
                if hasattr(self.preferences, key):
                    setattr(self.preferences, key, value)
            
            self._save_preferences(self.preferences)
            logger.info("Notification preferences updated")
            return True
        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")
            return False
    
    def update_channel_settings(self, channel: NotificationChannel, **kwargs) -> bool:
        """Update settings for a specific notification channel."""
        try:
            channel_attr = f"{channel.value}_settings"
            if hasattr(self.preferences, channel_attr):
                channel_settings = getattr(self.preferences, channel_attr)
                
                for key, value in kwargs.items():
                    if hasattr(channel_settings, key):
                        setattr(channel_settings, key, value)
                
                self._save_preferences(self.preferences)
                logger.info(f"Updated {channel.value} channel settings")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating channel settings: {str(e)}")
            return False
    
    def update_thresholds(self, **kwargs) -> bool:
        """Update alert thresholds."""
        try:
            for key, value in kwargs.items():
                if hasattr(self.preferences.thresholds, key):
                    setattr(self.preferences.thresholds, key, value)
            
            self._save_preferences(self.preferences)
            logger.info("Alert thresholds updated")
            return True
        except Exception as e:
            logger.error(f"Error updating thresholds: {str(e)}")
            return False
    
    def is_alert_enabled(self, alert_type: str) -> bool:
        """Check if a specific alert type is enabled."""
        try:
            alert_attr = f"{alert_type}_alerts"
            return getattr(self.preferences, alert_attr, False)
        except Exception as e:
            logger.error(f"Error checking alert status: {str(e)}")
            return False
    
    def is_channel_enabled(self, channel: NotificationChannel) -> bool:
        """Check if a notification channel is enabled."""
        try:
            channel_attr = f"{channel.value}_settings"
            channel_settings = getattr(self.preferences, channel_attr)
            return channel_settings.enabled
        except Exception as e:
            logger.error(f"Error checking channel status: {str(e)}")
            return False
    
    def get_channel_priority(self, channel: NotificationChannel) -> str:
        """Get priority for a notification channel."""
        try:
            channel_attr = f"{channel.value}_settings"
            channel_settings = getattr(self.preferences, channel_attr)
            return channel_settings.priority
        except Exception as e:
            logger.error(f"Error getting channel priority: {str(e)}")
            return "medium"
    
    def is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours."""
        try:
            from datetime import datetime, time
            
            current_time = datetime.now().time()
            quiet_start = time.fromisoformat(self.preferences.quiet_hours_start)
            quiet_end = time.fromisoformat(self.preferences.quiet_hours_end)
            
            if quiet_start <= quiet_end:
                # Same day quiet hours (e.g., 22:00 to 08:00)
                return quiet_start <= current_time <= quiet_end
            else:
                # Overnight quiet hours (e.g., 22:00 to 08:00)
                return current_time >= quiet_start or current_time <= quiet_end
        except Exception as e:
            logger.error(f"Error checking quiet hours: {str(e)}")
            return False
    
    def should_send_alert(self, alert_type: str, priority: str = "medium") -> bool:
        """Check if an alert should be sent based on preferences."""
        try:
            # Check if notifications are globally enabled
            if not self.preferences.notifications_enabled:
                return False
            
            # Check if specific alert type is enabled
            if not self.is_alert_enabled(alert_type):
                return False
            
            # Check quiet hours for non-critical alerts
            if priority != "critical" and self.is_quiet_hours():
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking if alert should be sent: {str(e)}")
            return False
    
    def get_enabled_channels(self) -> List[NotificationChannel]:
        """Get list of enabled notification channels."""
        enabled_channels = []
        
        for channel in NotificationChannel:
            if self.is_channel_enabled(channel):
                enabled_channels.append(channel)
        
        return enabled_channels
    
    def get_alert_template(self, alert_type: str) -> Dict:
        """Get template configuration for an alert type."""
        try:
            return self.default_templates.get(alert_type, {
                'subject': f'Stock Alert: {alert_type}',
                'priority': 'medium',
                'template': 'default_template.html'
            })
        except Exception as e:
            logger.error(f"Error getting alert template: {str(e)}")
            return {}
    
    def export_settings(self) -> Dict:
        """Export current settings as dictionary."""
        try:
            return self._preferences_to_dict(self.preferences)
        except Exception as e:
            logger.error(f"Error exporting settings: {str(e)}")
            return {}
    
    def import_settings(self, settings_data: Dict) -> bool:
        """Import settings from dictionary."""
        try:
            self.preferences = self._dict_to_preferences(settings_data)
            self._save_preferences(self.preferences)
            logger.info("Settings imported successfully")
            return True
        except Exception as e:
            logger.error(f"Error importing settings: {str(e)}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to defaults."""
        try:
            self.preferences = NotificationPreferences()
            self._save_preferences(self.preferences)
            logger.info("Settings reset to defaults")
            return True
        except Exception as e:
            logger.error(f"Error resetting settings: {str(e)}")
            return False
    
    def get_settings_summary(self) -> Dict:
        """Get a summary of current settings."""
        try:
            return {
                'notifications_enabled': self.preferences.notifications_enabled,
                'enabled_alerts': {
                    'target_hit': self.preferences.target_hit_alerts,
                    'stop_loss': self.preferences.stop_loss_alerts,
                    'significant_movement': self.preferences.significant_movement_alerts,
                    'daily_summary': self.preferences.daily_summary,
                    'risk_alerts': self.preferences.risk_alerts,
                    'swing_plan_updates': self.preferences.swing_plan_updates
                },
                'enabled_channels': [channel.value for channel in self.get_enabled_channels()],
                'quiet_hours': f"{self.preferences.quiet_hours_start} - {self.preferences.quiet_hours_end}",
                'thresholds': {
                    'significant_movement': self.preferences.thresholds.significant_movement_percent,
                    'max_alerts_per_hour': self.preferences.thresholds.max_alerts_per_hour,
                    'risk_alert_threshold': self.preferences.thresholds.risk_alert_threshold
                }
            }
        except Exception as e:
            logger.error(f"Error getting settings summary: {str(e)}")
            return {}
