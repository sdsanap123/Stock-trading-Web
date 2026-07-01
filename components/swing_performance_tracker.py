#!/usr/bin/env python3
"""
Swing Trading Performance Tracker Component
Tracks and analyzes swing trading performance after 7 days and adjusts future recommendations.
"""

import logging
import yfinance as yf
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import json
import os

logger = logging.getLogger(__name__)

class SwingPerformanceTracker:
    """Tracks swing trading performance and adjusts future recommendations."""
    
    def __init__(self, working_capital: float = 100000):
        """Initialize performance tracker."""
        self.working_capital = working_capital
        self.performance_data = []
        self.adaptive_parameters = {
            'stop_loss_percentage': 0.03,  # 3% default (realistic for 7 days)
            'take_profit_percentage': 0.02,  # 2% default (realistic for 7 days)
            'position_size_percentage': 0.1,  # 10% default
            'confidence_threshold': 60.0,  # Minimum confidence for trades
            'risk_reward_ratio': 0.67,  # 2:3 risk-reward ratio (realistic)
            'max_drawdown': 0.05,  # 5% maximum drawdown
            'win_rate_target': 0.6,  # 60% target win rate
            'last_updated': datetime.now().isoformat()
        }
        self.performance_file = "saved_data/swing_performance.json"
        self._load_performance_data()
        
        logger.info(f"Swing Performance Tracker initialized with working capital: ₹{working_capital:,.0f}")
    
    def _load_performance_data(self):
        """Load performance data from file."""
        try:
            if os.path.exists(self.performance_file):
                with open(self.performance_file, 'r') as f:
                    data = json.load(f)
                    self.performance_data = data.get('performance_data', [])
                    self.adaptive_parameters = data.get('adaptive_parameters', self.adaptive_parameters)
                logger.info(f"Loaded {len(self.performance_data)} performance records")
        except Exception as e:
            logger.error(f"Error loading performance data: {str(e)}")
            self.performance_data = []
    
    def _save_performance_data(self):
        """Save performance data to file."""
        try:
            os.makedirs(os.path.dirname(self.performance_file), exist_ok=True)
            data = {
                'performance_data': self.performance_data,
                'adaptive_parameters': self.adaptive_parameters,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.performance_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Performance data saved successfully")
        except Exception as e:
            logger.error(f"Error saving performance data: {str(e)}")
    
    def analyze_swing_performance(self, swing_strategies: List[Dict]) -> Dict:
        """Analyze performance of swing strategies after 7 days."""
        try:
            current_date = datetime.now()
            analysis_results = {
                'total_strategies': len(swing_strategies),
                'completed_strategies': 0,
                'active_strategies': 0,
                'expired_strategies': 0,
                'performance_metrics': {},
                'adjustments_made': [],
                'updated_parameters': {}
            }
            
            for strategy in swing_strategies:
                entry_date = datetime.fromisoformat(strategy.get('entry_date', ''))
                expected_exit_date = datetime.fromisoformat(strategy.get('expected_exit_date', ''))
                days_since_entry = (current_date - entry_date).days
                
                if days_since_entry >= 7:
                    # Analyze completed strategy
                    performance = self._analyze_completed_strategy(strategy)
                    if performance:
                        self.performance_data.append(performance)
                        analysis_results['completed_strategies'] += 1
                elif days_since_entry >= 0:
                    # Check if strategy should be updated
                    if strategy.get('status') == 'ACTIVE':
                        analysis_results['active_strategies'] += 1
                        # Check if stop loss or take profit was hit
                        self._check_strategy_exit_conditions(strategy)
                else:
                    analysis_results['expired_strategies'] += 1
            
            # Calculate performance metrics
            if self.performance_data:
                analysis_results['performance_metrics'] = self._calculate_performance_metrics()
                
                # Adjust parameters based on performance
                adjustments = self._adjust_parameters_based_on_performance()
                analysis_results['adjustments_made'] = adjustments
                analysis_results['updated_parameters'] = self.adaptive_parameters.copy()
            
            # Save updated data
            self._save_performance_data()
            
            logger.info(f"Performance analysis complete: {analysis_results['completed_strategies']} completed, {analysis_results['active_strategies']} active")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing swing performance: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_completed_strategy(self, strategy: Dict) -> Optional[Dict]:
        """Analyze a completed swing strategy."""
        try:
            symbol = strategy.get('symbol', '')
            entry_price = strategy.get('entry_price', 0)
            stop_loss = strategy.get('stop_loss', 0)
            take_profit = strategy.get('take_profit', 0)
            entry_date = datetime.fromisoformat(strategy.get('entry_date', ''))
            expected_exit_date = datetime.fromisoformat(strategy.get('expected_exit_date', ''))
            
            # Get current price
            current_price = self._get_current_price(symbol)
            if current_price <= 0:
                return None
            
            # Calculate performance
            price_change = current_price - entry_price
            price_change_percent = (price_change / entry_price) * 100
            
            # Determine exit reason
            exit_reason = self._determine_exit_reason(current_price, entry_price, stop_loss, take_profit, expected_exit_date)
            
            # Calculate actual returns
            actual_return = price_change_percent
            max_gain = max(0, ((take_profit - entry_price) / entry_price) * 100)
            max_loss = min(0, ((stop_loss - entry_price) / entry_price) * 100)
            
            # Calculate risk metrics
            risk_taken = ((entry_price - stop_loss) / entry_price) * 100
            reward_achieved = actual_return if actual_return > 0 else 0
            actual_risk_reward = reward_achieved / abs(risk_taken) if risk_taken != 0 else 0
            
            performance_record = {
                'symbol': symbol,
                'entry_date': strategy.get('entry_date', ''),
                'exit_date': datetime.now().isoformat(),
                'entry_price': entry_price,
                'exit_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'price_change_percent': price_change_percent,
                'actual_return': actual_return,
                'exit_reason': exit_reason,
                'risk_taken': risk_taken,
                'reward_achieved': reward_achieved,
                'actual_risk_reward': actual_risk_reward,
                'confidence': strategy.get('confidence', 0),
                'position_size': strategy.get('position_size', 0),
                'investment_amount': strategy.get('investment_amount', 0),
                'days_held': (datetime.now() - entry_date).days,
                'strategy_name': strategy.get('strategy_name', ''),
                'created_at': datetime.now().isoformat()
            }
            
            return performance_record
            
        except Exception as e:
            logger.error(f"Error analyzing completed strategy for {strategy.get('symbol', 'unknown')}: {str(e)}")
            return None
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol."""
        try:
            symbol_with_suffix = f"{symbol}.NS"
            ticker = yf.Ticker(symbol_with_suffix)
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                return float(hist['Close'].iloc[-1])
            return 0
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {str(e)}")
            return 0
    
    def _determine_exit_reason(self, current_price: float, entry_price: float, 
                             stop_loss: float, take_profit: float, expected_exit_date: datetime) -> str:
        """Determine why the strategy exited."""
        try:
            # Check if take profit was hit
            if current_price >= take_profit:
                return "TAKE_PROFIT_HIT"
            
            # Check if stop loss was hit
            if current_price <= stop_loss:
                return "STOP_LOSS_HIT"
            
            # Check if 7 days have passed
            if datetime.now() >= expected_exit_date:
                return "TIME_EXPIRED"
            
            # Check if it's still active
            return "STILL_ACTIVE"
            
        except Exception as e:
            logger.error(f"Error determining exit reason: {str(e)}")
            return "UNKNOWN"
    
    def _check_strategy_exit_conditions(self, strategy: Dict):
        """Check if active strategy should be exited."""
        try:
            symbol = strategy.get('symbol', '')
            current_price = self._get_current_price(symbol)
            entry_price = strategy.get('entry_price', 0)
            stop_loss = strategy.get('stop_loss', 0)
            take_profit = strategy.get('take_profit', 0)
            
            if current_price <= 0 or entry_price <= 0:
                return
            
            # Check stop loss
            if current_price <= stop_loss:
                strategy['status'] = 'STOP_LOSS_HIT'
                strategy['exit_price'] = current_price
                strategy['exit_date'] = datetime.now().isoformat()
                logger.info(f"Stop loss hit for {symbol} at ₹{current_price:.2f}")
            
            # Check take profit
            elif current_price >= take_profit:
                strategy['status'] = 'TAKE_PROFIT_HIT'
                strategy['exit_price'] = current_price
                strategy['exit_date'] = datetime.now().isoformat()
                logger.info(f"Take profit hit for {symbol} at ₹{current_price:.2f}")
            
        except Exception as e:
            logger.error(f"Error checking exit conditions for {strategy.get('symbol', 'unknown')}: {str(e)}")
    
    def _calculate_performance_metrics(self) -> Dict:
        """Calculate overall performance metrics."""
        try:
            if not self.performance_data:
                return {}
            
            total_trades = len(self.performance_data)
            winning_trades = len([p for p in self.performance_data if p.get('actual_return', 0) > 0])
            losing_trades = len([p for p in self.performance_data if p.get('actual_return', 0) < 0])
            
            win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
            
            total_return = sum(p.get('actual_return', 0) for p in self.performance_data)
            avg_return = total_return / total_trades if total_trades > 0 else 0
            
            avg_win = sum(p.get('actual_return', 0) for p in self.performance_data if p.get('actual_return', 0) > 0) / winning_trades if winning_trades > 0 else 0
            avg_loss = sum(p.get('actual_return', 0) for p in self.performance_data if p.get('actual_return', 0) < 0) / losing_trades if losing_trades > 0 else 0
            
            profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
            
            # Calculate Sharpe ratio (simplified)
            returns = [p.get('actual_return', 0) for p in self.performance_data]
            sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) != 0 else 0
            
            # Calculate maximum drawdown
            cumulative_returns = np.cumsum(returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdown) * 100 if len(drawdown) > 0 else 0
            
            return {
                'total_trades': total_trades,
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'win_rate': win_rate,
                'total_return': total_return,
                'avg_return': avg_return,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'current_capital': self.working_capital + (total_return / 100) * self.working_capital
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")
            return {}
    
    def _adjust_parameters_based_on_performance(self) -> List[str]:
        """Adjust trading parameters based on performance."""
        try:
            adjustments = []
            metrics = self._calculate_performance_metrics()
            
            if not metrics:
                return adjustments
            
            win_rate = metrics.get('win_rate', 0)
            avg_return = metrics.get('avg_return', 0)
            max_drawdown = abs(metrics.get('max_drawdown', 0))
            profit_factor = metrics.get('profit_factor', 0)
            
            # Adjust stop loss based on win rate (realistic ranges for 7-day trading)
            if win_rate < 50:  # Low win rate
                self.adaptive_parameters['stop_loss_percentage'] = max(0.02, self.adaptive_parameters['stop_loss_percentage'] - 0.005)
                adjustments.append(f"Reduced stop loss to {self.adaptive_parameters['stop_loss_percentage']*100:.1f}% due to low win rate ({win_rate:.1f}%)")
            elif win_rate > 70:  # High win rate
                self.adaptive_parameters['stop_loss_percentage'] = min(0.05, self.adaptive_parameters['stop_loss_percentage'] + 0.005)
                adjustments.append(f"Increased stop loss to {self.adaptive_parameters['stop_loss_percentage']*100:.1f}% due to high win rate ({win_rate:.1f}%)")
            
            # Adjust take profit based on profit factor (realistic ranges for 7-day trading)
            if profit_factor < 1.2:  # Low profit factor
                self.adaptive_parameters['take_profit_percentage'] = max(0.015, self.adaptive_parameters['take_profit_percentage'] - 0.005)
                adjustments.append(f"Reduced take profit to {self.adaptive_parameters['take_profit_percentage']*100:.1f}% due to low profit factor ({profit_factor:.2f})")
            elif profit_factor > 2.0:  # High profit factor
                self.adaptive_parameters['take_profit_percentage'] = min(0.03, self.adaptive_parameters['take_profit_percentage'] + 0.005)
                adjustments.append(f"Increased take profit to {self.adaptive_parameters['take_profit_percentage']*100:.1f}% due to high profit factor ({profit_factor:.2f})")
            
            # Adjust position size based on drawdown
            if max_drawdown > 8:  # High drawdown
                self.adaptive_parameters['position_size_percentage'] = max(0.05, self.adaptive_parameters['position_size_percentage'] - 0.02)
                adjustments.append(f"Reduced position size to {self.adaptive_parameters['position_size_percentage']*100:.1f}% due to high drawdown ({max_drawdown:.1f}%)")
            elif max_drawdown < 3 and win_rate > 60:  # Low drawdown and good win rate
                self.adaptive_parameters['position_size_percentage'] = min(0.15, self.adaptive_parameters['position_size_percentage'] + 0.01)
                adjustments.append(f"Increased position size to {self.adaptive_parameters['position_size_percentage']*100:.1f}% due to low drawdown ({max_drawdown:.1f}%)")
            
            # Adjust confidence threshold
            if win_rate < 55:
                self.adaptive_parameters['confidence_threshold'] = min(75, self.adaptive_parameters['confidence_threshold'] + 5)
                adjustments.append(f"Increased confidence threshold to {self.adaptive_parameters['confidence_threshold']:.1f}% due to low win rate")
            elif win_rate > 70:
                self.adaptive_parameters['confidence_threshold'] = max(50, self.adaptive_parameters['confidence_threshold'] - 5)
                adjustments.append(f"Decreased confidence threshold to {self.adaptive_parameters['confidence_threshold']:.1f}% due to high win rate")
            
            # Update last modified time
            self.adaptive_parameters['last_updated'] = datetime.now().isoformat()
            
            return adjustments
            
        except Exception as e:
            logger.error(f"Error adjusting parameters: {str(e)}")
            return []
    
    def get_adaptive_parameters(self) -> Dict:
        """Get current adaptive parameters."""
        return self.adaptive_parameters.copy()
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary."""
        return {
            'total_trades': len(self.performance_data),
            'performance_metrics': self._calculate_performance_metrics(),
            'adaptive_parameters': self.adaptive_parameters,
            'working_capital': self.working_capital
        }
    
    def reset_parameters(self):
        """Reset parameters to default values."""
        self.adaptive_parameters = {
            'stop_loss_percentage': 0.03,  # 3% realistic for 7 days
            'take_profit_percentage': 0.02,  # 2% realistic for 7 days
            'position_size_percentage': 0.1,
            'confidence_threshold': 60.0,
            'risk_reward_ratio': 0.67,  # 2:3 realistic ratio
            'max_drawdown': 0.05,
            'win_rate_target': 0.6,
            'last_updated': datetime.now().isoformat()
        }
        logger.info("Parameters reset to realistic default values")
