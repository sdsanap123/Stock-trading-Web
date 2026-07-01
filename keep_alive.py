#!/usr/bin/env python3
"""
Keep-alive ping service for Streamlit Cloud apps
Prevents app from sleeping due to inactivity by sending periodic requests
"""

import threading
import time
import requests
import logging
from typing import Optional
from datetime import datetime
import streamlit as st

logger = logging.getLogger(__name__)

class KeepAliveService:
    """Background service to keep Streamlit app awake with periodic pings."""
    
    def __init__(self, ping_interval: int = 300):
        """
        Initialize the keep-alive service.
        
        Args:
            ping_interval: Time between pings in seconds (default: 300 = 5 minutes)
        """
        self.ping_interval = ping_interval
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self._app_url = None  # Lazy loaded
        self.last_ping_time: Optional[datetime] = None
        self.ping_count = 0
        self.failed_pings = 0
    
    @property
    def app_url(self) -> str:
        """Get the current app URL (lazy loaded)."""
        if self._app_url is None:
            self._app_url = self._get_app_url()
        return self._app_url
    
    @app_url.setter
    def app_url(self, value: str):
        """Set the app URL."""
        self._app_url = value
        
    def _get_app_url(self) -> str:
        """Get the current app URL for pinging."""
        try:
            # Try to get URL from environment variables first
            if 'STREAMLIT_APP_URL' in st.secrets:
                return st.secrets['STREAMLIT_APP_URL']
            
            # Fallback to common Streamlit Cloud URL pattern
            import os
            app_name = os.environ.get('STREAMLIT_APP_NAME', '')
            if app_name:
                return f"https://{app_name}.streamlit.app"
            
            # Default placeholder - user should configure this
            logger.warning("No app URL configured. Please set STREAMLIT_APP_URL in secrets.")
            return "https://your-app-name.streamlit.app"
            
        except Exception as e:
            logger.error(f"Error getting app URL: {e}")
            return "https://your-app-name.streamlit.app"
    
    def _ping_app(self) -> bool:
        """Send a ping request to the app."""
        try:
            headers = {
                'User-Agent': 'KeepAlive-Service/1.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = requests.get(
                self.app_url,
                headers=headers,
                timeout=30,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                self.last_ping_time = datetime.now()
                self.ping_count += 1
                logger.info(f"Ping successful #{self.ping_count} at {self.last_ping_time.strftime('%H:%M:%S')}")
                return True
            else:
                self.failed_pings += 1
                logger.warning(f"Ping failed with status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.failed_pings += 1
            logger.error(f"Ping error: {e}")
            return False
        except Exception as e:
            self.failed_pings += 1
            logger.error(f"Unexpected ping error: {e}")
            return False
    
    def _ping_loop(self):
        """Background thread loop for periodic pinging."""
        logger.info(f"Keep-alive service started. Pinging {self.app_url} every {self.ping_interval} seconds")
        
        while self.is_running:
            try:
                success = self._ping_app()
                if not success:
                    logger.warning(f"Ping failed. Total failures: {self.failed_pings}")
                
                # Wait for next ping
                time.sleep(self.ping_interval)
                
            except Exception as e:
                logger.error(f"Error in ping loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying after error
    
    def start(self):
        """Start the keep-alive service."""
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._ping_loop, daemon=True)
            self.thread.start()
            logger.info("Keep-alive service started")
            return True
        return False
    
    def stop(self):
        """Stop the keep-alive service."""
        if self.is_running:
            self.is_running = False
            if self.thread:
                self.thread.join(timeout=5)
            logger.info("Keep-alive service stopped")
            return True
        return False
    
    def get_status(self) -> dict:
        """Get current service status."""
        return {
            'is_running': self.is_running,
            'app_url': self.app_url,
            'ping_interval': self.ping_interval,
            'last_ping_time': self.last_ping_time,
            'ping_count': self.ping_count,
            'failed_pings': self.failed_pings,
            'success_rate': (self.ping_count / (self.ping_count + self.failed_pings) * 100) 
                           if (self.ping_count + self.failed_pings) > 0 else 0
        }
    
    def update_interval(self, new_interval: int):
        """Update the ping interval."""
        if new_interval > 0:
            self.ping_interval = new_interval
            logger.info(f"Ping interval updated to {new_interval} seconds")
            return True
        return False
    
    def update_url(self, new_url: str):
        """Update the app URL."""
        if new_url and new_url.startswith('http'):
            self.app_url = new_url  # This will use the setter
            logger.info(f"App URL updated to {new_url}")
            return True
        return False

# Global instance for the app
_keep_alive_service: Optional[KeepAliveService] = None

def get_keep_alive_service() -> KeepAliveService:
    """Get or create the global keep-alive service instance."""
    global _keep_alive_service
    if _keep_alive_service is None:
        _keep_alive_service = KeepAliveService()
    return _keep_alive_service

def start_keep_alive(ping_interval: int = 300) -> bool:
    """Start the keep-alive service with specified interval."""
    service = get_keep_alive_service()
    service.update_interval(ping_interval)
    return service.start()

def stop_keep_alive() -> bool:
    """Stop the keep-alive service."""
    service = get_keep_alive_service()
    return service.stop()

def get_keep_alive_status() -> dict:
    """Get the current status of the keep-alive service."""
    service = get_keep_alive_service()
    return service.get_status()

def configure_keep_alive(url: str, interval: int) -> bool:
    """Configure the keep-alive service settings."""
    service = get_keep_alive_service()
    url_updated = service.update_url(url)
    interval_updated = service.update_interval(interval)
    return url_updated and interval_updated
