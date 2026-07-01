#!/usr/bin/env python3
"""
Swing Trading Strategy Component
Implements 7-day swing trading strategy with position sizing and risk management.
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)

class SwingTradingStrategy:
    """7-day swing trading strategy implementation."""
    
    def __init__(self, adaptive_parameters: Dict = None):
        """Initialize swing trading strategy."""
        self.strategy_name = "7-Day Adaptive Swing Strategy"
        self.holding_period_days = 7
        
        # Default parameters - Realistic for 7-day swing trading
        self.max_position_size = 0.1  # 10% of portfolio per position
        self.stop_loss_percentage = 0.03  # 3% stop loss (realistic for 7 days)
        self.take_profit_percentage = 0.02  # 2% take profit (realistic for 7 days)
        self.risk_reward_ratio = 0.67  # 2:3 risk-reward ratio (realistic)
        self.confidence_threshold = 60.0  # Minimum confidence for trades
        
        # Apply adaptive parameters if provided
        if adaptive_parameters:
            self.max_position_size = adaptive_parameters.get('position_size_percentage', self.max_position_size)
            self.stop_loss_percentage = adaptive_parameters.get('stop_loss_percentage', self.stop_loss_percentage)
            self.take_profit_percentage = adaptive_parameters.get('take_profit_percentage', self.take_profit_percentage)
            self.risk_reward_ratio = adaptive_parameters.get('risk_reward_ratio', self.risk_reward_ratio)
            self.confidence_threshold = adaptive_parameters.get('confidence_threshold', self.confidence_threshold)
        
        logger.info(f"7-Day Adaptive Swing Strategy initialized with parameters: SL={self.stop_loss_percentage*100:.1f}%, TP={self.take_profit_percentage*100:.1f}%, Pos={self.max_position_size*100:.1f}%")
    
    def calculate_position_size(self, stock_data: Dict, portfolio_value: float = 100000) -> Dict:
        """Calculate optimal position size based on adaptive risk management."""
        try:
            current_price = stock_data.get('current_price', 0)
            confidence = stock_data.get('confidence', 0)
            
            # Check confidence threshold
            if confidence < self.confidence_threshold:
                return {
                    'position_size': 0,
                    'shares': 0,
                    'investment_amount': 0,
                    'risk_amount': 0,
                    'risk_percentage': 0,
                    'reason': f'Confidence too low: {confidence:.1f}% < {self.confidence_threshold:.1f}%'
                }
            
            # Calculate stop loss and take profit using adaptive parameters
            stop_loss_price = current_price * (1 - self.stop_loss_percentage)
            take_profit_price = current_price * (1 + self.take_profit_percentage)
            
            if current_price <= 0:
                return {
                    'position_size': 0,
                    'shares': 0,
                    'investment_amount': 0,
                    'risk_amount': 0,
                    'risk_percentage': 0,
                    'reason': 'Invalid price data'
                }
            
            # Calculate risk per share
            risk_per_share = current_price - stop_loss_price
            
            # Calculate maximum risk amount (2% of portfolio)
            max_risk_amount = portfolio_value * 0.02
            
            # Calculate position size based on risk
            max_shares_by_risk = int(max_risk_amount / risk_per_share) if risk_per_share > 0 else 0
            
            # Calculate position size based on confidence and max position size
            confidence_multiplier = min(confidence, 1.0)
            max_investment = portfolio_value * self.max_position_size * confidence_multiplier
            max_shares_by_investment = int(max_investment / current_price)
            
            # Use the smaller of the two (risk-based or investment-based)
            optimal_shares = min(max_shares_by_risk, max_shares_by_investment)
            
            # Ensure minimum position size for meaningful impact
            min_shares = max(1, int(portfolio_value * 0.01 / current_price))  # At least 1% of portfolio
            optimal_shares = max(optimal_shares, min_shares)
            
            investment_amount = optimal_shares * current_price
            risk_amount = optimal_shares * risk_per_share
            
            return {
                'position_size': optimal_shares,
                'shares': optimal_shares,
                'investment_amount': investment_amount,
                'risk_amount': risk_amount,
                'risk_percentage': (risk_amount / portfolio_value) * 100,
                'confidence_multiplier': confidence_multiplier,
                'reason': f'Risk-based sizing: {optimal_shares} shares'
            }
            
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            return {
                'position_size': 0,
                'shares': 0,
                'investment_amount': 0,
                'risk_amount': 0,
                'risk_percentage': 0,
                'reason': f'Error: {str(e)}'
            }
    
    def calculate_entry_exit_levels(self, stock_data: Dict) -> Dict:
        """Calculate entry, stop loss, and take profit levels using adaptive parameters."""
        try:
            current_price = stock_data.get('current_price', 0)
            confidence = stock_data.get('confidence', 0)
            
            if current_price <= 0:
                return {
                    'entry_price': 0,
                    'stop_loss': 0,
                    'take_profit': 0,
                    'risk_reward_ratio': 0,
                    'strategy': 'Invalid price data'
                }
            
            # Entry price (current market price)
            entry_price = current_price
            
            # Use adaptive stop loss percentage
            stop_loss = entry_price * (1 - self.stop_loss_percentage)
            
            # Use adaptive take profit percentage
            take_profit = entry_price * (1 + self.take_profit_percentage)
            
            # Calculate risk-reward ratio
            potential_profit = take_profit - entry_price
            potential_loss = entry_price - stop_loss
            risk_reward_ratio = potential_profit / potential_loss if potential_loss > 0 else 0
            
            # Always include potential_profit and potential_loss in the return value
            result = {
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_reward_ratio': risk_reward_ratio,
                'potential_profit': potential_profit,
                'potential_loss': potential_loss,
                'strategy': ''
            }
            
            # Check if risk-reward ratio meets minimum requirement
            if risk_reward_ratio < self.risk_reward_ratio:
                result['strategy'] = f'Risk-reward ratio too low: {risk_reward_ratio:.2f} < {self.risk_reward_ratio:.2f}'
                return result
                
            result['strategy'] = f'Adaptive Swing: SL={self.stop_loss_percentage*100:.1f}%, TP={self.take_profit_percentage*100:.1f}%'
            return result
            
            return {
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_reward_ratio': risk_reward_ratio,
                'potential_profit': take_profit - entry_price,
                'potential_loss': entry_price - stop_loss,
                'strategy': f'Adaptive Swing: SL={self.stop_loss_percentage*100:.1f}%, TP={self.take_profit_percentage*100:.1f}%'
            }
            
        except Exception as e:
            logger.error(f"Error calculating entry/exit levels: {str(e)}")
            return {
                'entry_price': 0,
                'stop_loss': 0,
                'take_profit': 0,
                'risk_reward_ratio': 0,
                'strategy': f'Error: {str(e)}'
            }
    
    def generate_swing_trading_plan(self, stock_data: Dict, portfolio_value: float = 100000) -> Dict:
        """Generate complete swing trading plan for a stock."""
        try:
            symbol = stock_data.get('symbol', 'UNKNOWN')
            current_price = stock_data.get('current_price', 0)
            confidence = stock_data.get('confidence', 0)
            
            # Calculate position sizing
            position_info = self.calculate_position_size(stock_data, portfolio_value)
            
            # Calculate entry/exit levels
            levels_info = self.calculate_entry_exit_levels(stock_data)
            
            # Calculate holding period
            entry_date = datetime.now()
            exit_date = entry_date + timedelta(days=self.holding_period_days)
            
            # Generate trading plan
            trading_plan = {
                'symbol': symbol,
                'company_name': stock_data.get('company_name', ''),
                'strategy_name': self.strategy_name,
                'entry_date': entry_date.isoformat(),
                'expected_exit_date': exit_date.isoformat(),
                'holding_period_days': self.holding_period_days,
                'current_price': current_price,
                'confidence': confidence,
                
                # Position sizing
                'position_size': position_info['shares'],
                'investment_amount': position_info['investment_amount'],
                'risk_amount': position_info['risk_amount'],
                'risk_percentage': position_info['risk_percentage'],
                
                # Entry/Exit levels
                'entry_price': levels_info['entry_price'],
                'stop_loss': levels_info['stop_loss'],
                'take_profit': levels_info['take_profit'],
                'risk_reward_ratio': levels_info['risk_reward_ratio'],
                'potential_profit': levels_info['potential_profit'],
                'potential_loss': levels_info['potential_loss'],
                
                # Strategy details
                'strategy_rules': [
                    f"Hold for maximum {self.holding_period_days} days",
                    f"Stop loss at {self.stop_loss_percentage*100:.1f}% below entry",
                    f"Take profit at {self.take_profit_percentage*100:.1f}% above entry",
                    f"Risk-reward ratio: {self.risk_reward_ratio}:1 minimum",
                    f"Position size: {position_info['shares']} shares (₹{position_info['investment_amount']:,.0f})"
                ],
                
                # Risk management
                'risk_management': [
                    "Set stop loss immediately after entry",
                    "Monitor daily for exit signals",
                    "Consider partial profit booking at 10% gain",
                    "Exit if fundamentals deteriorate",
                    "Exit if news sentiment turns negative"
                ],
                
                # Success criteria
                'success_criteria': [
                    f"Target: {levels_info['take_profit']:.2f} (₹{levels_info['potential_profit']:.2f} profit)",
                    f"Stop loss: {levels_info['stop_loss']:.2f} (₹{levels_info['potential_loss']:.2f} loss)",
                    f"Risk-reward: {levels_info['risk_reward_ratio']:.2f}:1",
                    f"Expected holding: {self.holding_period_days} days"
                ]
            }
            
            logger.info(f"Generated swing trading plan for {symbol}")
            return trading_plan
            
        except Exception as e:
            logger.error(f"Error generating swing trading plan: {str(e)}")
            return {
                'symbol': stock_data.get('symbol', 'UNKNOWN'),
                'error': str(e),
                'strategy_name': self.strategy_name
            }
    
    def validate_swing_opportunity(self, stock_data: Dict) -> Dict:
        """Validate if a stock is suitable for swing trading."""
        try:
            symbol = stock_data.get('symbol', 'UNKNOWN')
            current_price = stock_data.get('current_price', 0)
            confidence = stock_data.get('confidence', 0)
            technical_data = stock_data.get('technical_data', {})
            groq_analysis = stock_data.get('groq_analysis', {})
            
            validation_results = {
                'symbol': symbol,
                'is_suitable': True,
                'score': 0,
                'reasons': [],
                'warnings': [],
                'recommendations': []
            }
            
            # Check confidence level
            if confidence >= 70:
                validation_results['score'] += 30
                validation_results['reasons'].append(f"High confidence: {confidence:.1f}%")
            elif confidence >= 50:
                validation_results['score'] += 20
                validation_results['reasons'].append(f"Medium confidence: {confidence:.1f}%")
            else:
                validation_results['score'] += 10
                validation_results['warnings'].append(f"Low confidence: {confidence:.1f}%")
            
            # Check technical indicators
            rsi = technical_data.get('rsi', 50)
            if 30 <= rsi <= 70:
                validation_results['score'] += 20
                validation_results['reasons'].append(f"RSI in good range: {rsi:.1f}")
            elif rsi < 30:
                validation_results['score'] += 15
                validation_results['reasons'].append(f"RSI oversold: {rsi:.1f} (potential bounce)")
            else:
                validation_results['warnings'].append(f"RSI overbought: {rsi:.1f}")
            
            # Check price momentum
            price_change_5d = technical_data.get('price_change_5d', 0)
            if -5 <= price_change_5d <= 10:
                validation_results['score'] += 15
                validation_results['reasons'].append(f"Reasonable 5-day change: {price_change_5d:.1f}%")
            else:
                validation_results['warnings'].append(f"High volatility: {price_change_5d:.1f}% 5-day change")
            
            # Check Groq analysis
            if groq_analysis and groq_analysis.get('status') == 'success':
                groq_score = groq_analysis.get('overall_score', 0.5)
                if groq_score >= 0.6:
                    validation_results['score'] += 20
                    validation_results['reasons'].append(f"Strong Groq analysis: {groq_score:.2f}")
                else:
                    validation_results['warnings'].append(f"Weak Groq analysis: {groq_score:.2f}")
            
            # Check price level
            if current_price >= 50:  # Avoid penny stocks for swing trading
                validation_results['score'] += 15
                validation_results['reasons'].append(f"Good price level: ₹{current_price:.2f}")
            else:
                validation_results['warnings'].append(f"Low price stock: ₹{current_price:.2f}")
            
            # Determine suitability
            if validation_results['score'] >= 70:
                validation_results['is_suitable'] = True
                validation_results['recommendations'].append("Strong swing trading opportunity")
            elif validation_results['score'] >= 50:
                validation_results['is_suitable'] = True
                validation_results['recommendations'].append("Moderate swing trading opportunity")
            else:
                validation_results['is_suitable'] = False
                validation_results['recommendations'].append("Not suitable for swing trading")
            
            logger.info(f"Validated swing opportunity for {symbol}: Score {validation_results['score']}/100")
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating swing opportunity: {str(e)}")
            return {
                'symbol': stock_data.get('symbol', 'UNKNOWN'),
                'is_suitable': False,
                'score': 0,
                'error': str(e)
            }
    
    def get_strategy_summary(self) -> Dict:
        """Get strategy summary and rules."""
        return {
            'strategy_name': self.strategy_name,
            'holding_period_days': self.holding_period_days,
            'max_position_size': self.max_position_size,
            'stop_loss_percentage': self.stop_loss_percentage,
            'take_profit_percentage': self.take_profit_percentage,
            'risk_reward_ratio': self.risk_reward_ratio,
            'description': f"{self.strategy_name} focuses on short-term price movements over {self.holding_period_days} days",
            'key_rules': [
                f"Hold positions for maximum {self.holding_period_days} days",
                f"Use {self.stop_loss_percentage*100:.1f}% stop loss for risk management",
                f"Target {self.take_profit_percentage*100:.1f}% profit per trade",
                f"Maintain minimum {self.risk_reward_ratio}:1 risk-reward ratio",
                f"Limit position size to {self.max_position_size*100:.1f}% of portfolio",
                "Focus on stocks with strong news catalysts",
                "Exit on negative news or fundamental deterioration"
            ]
        }
