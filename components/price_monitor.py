#!/usr/bin/env python3
"""
Price Monitor Component
Real-time price monitoring with automatic alert triggers.
"""

import logging
import time
import threading
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import yfinance as yf
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MonitorStatus(Enum):
    """Status of price monitoring."""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"

@dataclass
class PriceAlert:
    """Price alert configuration."""
    symbol: str
    current_price: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    entry_price: Optional[float] = None
    significant_movement_threshold: float = 5.0
    last_alert_price: Optional[float] = None
    alert_count: int = 0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class PriceMonitor:
    """Real-time price monitoring with automatic alert triggers."""
    
    def __init__(self, notification_callback: Optional[Callable] = None):
        self.notification_callback = notification_callback
        self.monitored_stocks: Dict[str, PriceAlert] = {}
        self.status = MonitorStatus.STOPPED
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.check_interval = 60  # Check every 60 seconds
        self.last_check_time = None
        
        logger.info("PriceMonitor initialized")
    
    def add_stock_to_monitor(self, stock_data: Dict) -> bool:
        """Add a stock to monitoring list."""
        try:
            symbol = stock_data.get('symbol')
            if not symbol:
                logger.error("Symbol is required for monitoring")
                return False
            
            # Create price alert configuration
            price_alert = PriceAlert(
                symbol=symbol,
                current_price=stock_data.get('current_price', 0),
                target_price=stock_data.get('target_price'),
                stop_loss=stock_data.get('stop_loss'),
                entry_price=stock_data.get('entry_price', stock_data.get('current_price', 0)),
                significant_movement_threshold=stock_data.get('significant_movement_threshold', 5.0)
            )
            
            self.monitored_stocks[symbol] = price_alert
            logger.info(f"Added {symbol} to price monitoring")
            return True
            
        except Exception as e:
            logger.error(f"Error adding stock to monitor: {str(e)}")
            return False
    
    def remove_stock_from_monitor(self, symbol: str) -> bool:
        """Remove a stock from monitoring list."""
        try:
            if symbol in self.monitored_stocks:
                del self.monitored_stocks[symbol]
                logger.info(f"Removed {symbol} from price monitoring")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing stock from monitor: {str(e)}")
            return False
    
    def update_stock_targets(self, symbol: str, target_price: Optional[float] = None, 
                           stop_loss: Optional[float] = None) -> bool:
        """Update target price and stop loss for a monitored stock."""
        try:
            if symbol in self.monitored_stocks:
                if target_price is not None:
                    self.monitored_stocks[symbol].target_price = target_price
                if stop_loss is not None:
                    self.monitored_stocks[symbol].stop_loss = stop_loss
                
                logger.info(f"Updated targets for {symbol}: Target={target_price}, Stop Loss={stop_loss}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating stock targets: {str(e)}")
            return False
    
    def start_monitoring(self, check_interval: int = 60) -> bool:
        """Start price monitoring in background thread."""
        try:
            if self.status == MonitorStatus.RUNNING:
                logger.warning("Price monitoring is already running")
                return True
            
            if not self.monitored_stocks:
                logger.warning("No stocks to monitor")
                return False
            
            self.check_interval = check_interval
            self.stop_event.clear()
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            self.status = MonitorStatus.RUNNING
            logger.info(f"Price monitoring started with {len(self.monitored_stocks)} stocks")
            return True
            
        except Exception as e:
            logger.error(f"Error starting price monitoring: {str(e)}")
            self.status = MonitorStatus.ERROR
            return False
    
    def stop_monitoring(self) -> bool:
        """Stop price monitoring."""
        try:
            if self.status != MonitorStatus.RUNNING:
                logger.warning("Price monitoring is not running")
                return True
            
            self.stop_event.set()
            
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5)
            
            self.status = MonitorStatus.STOPPED
            logger.info("Price monitoring stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping price monitoring: {str(e)}")
            return False
    
    def pause_monitoring(self) -> bool:
        """Pause price monitoring."""
        try:
            if self.status == MonitorStatus.RUNNING:
                self.status = MonitorStatus.PAUSED
                logger.info("Price monitoring paused")
                return True
            return False
        except Exception as e:
            logger.error(f"Error pausing price monitoring: {str(e)}")
            return False
    
    def resume_monitoring(self) -> bool:
        """Resume price monitoring."""
        try:
            if self.status == MonitorStatus.PAUSED:
                self.status = MonitorStatus.RUNNING
                logger.info("Price monitoring resumed")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resuming price monitoring: {str(e)}")
            return False
    
    def _monitor_loop(self):
        """Main monitoring loop running in background thread."""
        logger.info("Price monitoring loop started")
        
        while not self.stop_event.is_set():
            try:
                if self.status == MonitorStatus.RUNNING:
                    self._check_all_stocks()
                
                # Wait for next check
                self.stop_event.wait(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(10)  # Wait 10 seconds before retrying
        
        logger.info("Price monitoring loop stopped")
    
    def _check_all_stocks(self):
        """Check prices for all monitored stocks."""
        try:
            self.last_check_time = datetime.now()
            
            for symbol, price_alert in self.monitored_stocks.items():
                try:
                    self._check_stock_price(symbol, price_alert)
                except Exception as e:
                    logger.error(f"Error checking price for {symbol}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error checking all stocks: {str(e)}")
    
    def _check_stock_price(self, symbol: str, price_alert: PriceAlert):
        """Check price for a single stock and trigger alerts if needed."""
        try:
            # Get current price
            current_price = self._get_current_price(symbol)
            if current_price is None:
                return
            
            # Update current price
            old_price = price_alert.current_price
            price_alert.current_price = current_price
            
            # Check for alerts
            alerts_triggered = []
            
            # Check target price hit
            if (price_alert.target_price and 
                current_price >= price_alert.target_price and 
                old_price < price_alert.target_price):
                alerts_triggered.append('target_hit')
            
            # Check stop loss hit
            if (price_alert.stop_loss and 
                current_price <= price_alert.stop_loss and 
                old_price > price_alert.stop_loss):
                alerts_triggered.append('stop_loss_hit')
            
            # Check significant movement
            if price_alert.last_alert_price:
                movement_percent = abs((current_price - price_alert.last_alert_price) / price_alert.last_alert_price) * 100
                if movement_percent >= price_alert.significant_movement_threshold:
                    alerts_triggered.append('significant_movement')
            
            # Trigger alerts
            for alert_type in alerts_triggered:
                self._trigger_alert(symbol, price_alert, alert_type, current_price)
            
            # Update last alert price if any alert was triggered
            if alerts_triggered:
                price_alert.last_alert_price = current_price
                price_alert.alert_count += 1
            
        except Exception as e:
            logger.error(f"Error checking stock price for {symbol}: {str(e)}")
    
    def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol."""
        try:
            symbol_with_suffix = f"{symbol}.NS"
            ticker = yf.Ticker(symbol_with_suffix)
            hist = ticker.history(period="1d", interval="1m")
            
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
            else:
                logger.warning(f"No price data available for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {str(e)}")
            return None
    
    def _trigger_alert(self, symbol: str, price_alert: PriceAlert, alert_type: str, current_price: float):
        """Trigger an alert for a stock."""
        try:
            # Prepare stock data for notification
            stock_data = {
                'symbol': symbol,
                'current_price': current_price,
                'target_price': price_alert.target_price,
                'stop_loss': price_alert.stop_loss,
                'entry_price': price_alert.entry_price,
                'position_size': 0,  # Will be filled by caller
                'investment_amount': 0,  # Will be filled by caller
                'company_name': ''  # Will be filled by caller
            }
            
            # Prepare additional data based on alert type
            additional_data = {}
            
            if alert_type == 'significant_movement':
                if price_alert.last_alert_price:
                    movement_percent = ((current_price - price_alert.last_alert_price) / price_alert.last_alert_price) * 100
                    additional_data['movement_percent'] = movement_percent
            
            # Call notification callback if available
            if self.notification_callback:
                self.notification_callback(alert_type, stock_data, additional_data)
            
            logger.info(f"Alert triggered: {alert_type} for {symbol} at ₹{current_price:.2f}")
            
        except Exception as e:
            logger.error(f"Error triggering alert for {symbol}: {str(e)}")
    
    def get_monitoring_status(self) -> Dict:
        """Get current monitoring status."""
        return {
            'status': self.status.value,
            'monitored_stocks_count': len(self.monitored_stocks),
            'check_interval': self.check_interval,
            'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
            'monitored_stocks': list(self.monitored_stocks.keys())
        }
    
    def get_stock_status(self, symbol: str) -> Optional[Dict]:
        """Get monitoring status for a specific stock."""
        try:
            if symbol not in self.monitored_stocks:
                return None
            
            price_alert = self.monitored_stocks[symbol]
            return {
                'symbol': symbol,
                'current_price': price_alert.current_price,
                'target_price': price_alert.target_price,
                'stop_loss': price_alert.stop_loss,
                'entry_price': price_alert.entry_price,
                'significant_movement_threshold': price_alert.significant_movement_threshold,
                'last_alert_price': price_alert.last_alert_price,
                'alert_count': price_alert.alert_count,
                'created_at': price_alert.created_at.isoformat(),
                'is_target_hit': price_alert.target_price and price_alert.current_price >= price_alert.target_price,
                'is_stop_loss_hit': price_alert.stop_loss and price_alert.current_price <= price_alert.stop_loss
            }
        except Exception as e:
            logger.error(f"Error getting stock status for {symbol}: {str(e)}")
            return None
    
    def force_price_check(self, symbol: str) -> Optional[float]:
        """Force a price check for a specific stock."""
        try:
            if symbol not in self.monitored_stocks:
                logger.warning(f"Stock {symbol} is not being monitored")
                return None
            
            price_alert = self.monitored_stocks[symbol]
            current_price = self._get_current_price(symbol)
            
            if current_price is not None:
                old_price = price_alert.current_price
                price_alert.current_price = current_price
                
                # Check for alerts
                self._check_stock_price(symbol, price_alert)
                
                logger.info(f"Force price check for {symbol}: ₹{old_price:.2f} → ₹{current_price:.2f}")
            
            return current_price
            
        except Exception as e:
            logger.error(f"Error in force price check for {symbol}: {str(e)}")
            return None
