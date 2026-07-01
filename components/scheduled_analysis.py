#!/usr/bin/env python3
"""
Scheduled Analysis Component for Stock Trading App
Handles automatic daily analysis at 7 AM IST on weekdays.
"""

import schedule
import time
import threading
import logging
from datetime import datetime, timezone
import pytz
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ScheduledAnalysis:
    """Handles scheduled analysis tasks."""
    
    def __init__(self, analysis_callback=None):
        """Initialize scheduled analysis.
        
        Args:
            analysis_callback: Function to call for market analysis
        """
        self.analysis_callback = analysis_callback
        self.is_running = False
        self.scheduler_thread = None
        self.ist = pytz.timezone('Asia/Kolkata')
        
        # Schedule daily analysis at 7 AM IST on weekdays
        schedule.every().monday.at("07:00").do(self._run_daily_analysis)
        schedule.every().tuesday.at("07:00").do(self._run_daily_analysis)
        schedule.every().wednesday.at("07:00").do(self._run_daily_analysis)
        schedule.every().thursday.at("07:00").do(self._run_daily_analysis)
        schedule.every().friday.at("07:00").do(self._run_daily_analysis)
        
        logger.info("Scheduled analysis initialized for 7 AM IST on weekdays")
    
    def _run_daily_analysis(self):
        """Run daily market analysis."""
        try:
            current_time = datetime.now(self.ist)
            logger.info(f"Starting scheduled daily analysis at {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
            
            if self.analysis_callback:
                # Run the analysis in a separate thread to avoid blocking
                analysis_thread = threading.Thread(target=self.analysis_callback)
                analysis_thread.daemon = True
                analysis_thread.start()
                logger.info("Scheduled analysis started in background thread")
            else:
                logger.warning("No analysis callback provided")
                
        except Exception as e:
            logger.error(f"Error in scheduled analysis: {str(e)}")
    
    def start_scheduler(self):
        """Start the scheduler in a background thread."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        logger.info("Scheduled analysis started")
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Scheduled analysis stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop."""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(60)
    
    def get_next_analysis_time(self) -> str:
        """Get the next scheduled analysis time."""
        try:
            # Get the next scheduled job
            next_run = schedule.next_run()
            if next_run:
                # Convert to IST
                next_run_ist = next_run.astimezone(self.ist)
                return next_run_ist.strftime('%Y-%m-%d %H:%M:%S IST')
            else:
                return "No scheduled analysis"
        except Exception as e:
            logger.error(f"Error getting next analysis time: {str(e)}")
            return "Error getting schedule"
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status information."""
        return {
            'is_running': self.is_running,
            'next_analysis': self.get_next_analysis_time(),
            'scheduled_days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            'scheduled_time': '07:00 IST'
        }
    
    def run_analysis_now(self):
        """Manually trigger analysis now."""
        try:
            logger.info("Manually triggering analysis")
            self._run_daily_analysis()
        except Exception as e:
            logger.error(f"Error in manual analysis: {str(e)}")
    
    def set_analysis_callback(self, callback):
        """Set the analysis callback function."""
        self.analysis_callback = callback
        logger.info("Analysis callback updated")
