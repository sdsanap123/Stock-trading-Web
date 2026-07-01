#!/usr/bin/env python3
"""
Technical Analyzer Component
Technical analysis for stocks with comprehensive indicators.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Technical analysis for stocks."""
    
    def __init__(self):
        logger.info("Technical Analyzer initialized")
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator."""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1] if not rsi.empty else 50
        except:
            return 50
    
    def calculate_macd(self, prices: pd.Series) -> float:
        """Calculate MACD indicator."""
        try:
            ema_12 = prices.ewm(span=12).mean()
            ema_26 = prices.ewm(span=26).mean()
            macd = ema_12 - ema_26
            return macd.iloc[-1] if not macd.empty else 0
        except:
            return 0
    
    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands."""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper_band = sma + (std * 2)
            lower_band = sma - (std * 2)
            
            return (
                upper_band.iloc[-1] if not upper_band.empty else 0,
                sma.iloc[-1] if not sma.empty else 0,
                lower_band.iloc[-1] if not lower_band.empty else 0
            )
        except:
            return 0, 0, 0
    
    def calculate_sma(self, prices: pd.Series, period: int) -> float:
        """Calculate Simple Moving Average."""
        try:
            return prices.rolling(window=period).mean().iloc[-1] if len(prices) >= period else prices.iloc[-1]
        except:
            return prices.iloc[-1] if not prices.empty else 0
    
    def calculate_ema(self, prices: pd.Series, period: int) -> float:
        """Calculate Exponential Moving Average."""
        try:
            return prices.ewm(span=period).mean().iloc[-1] if len(prices) >= period else prices.iloc[-1]
        except:
            return prices.iloc[-1] if not prices.empty else 0
    
    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Tuple[float, float]:
        """Calculate Stochastic Oscillator."""
        try:
            lowest_low = low.rolling(window=period).min()
            highest_high = high.rolling(window=period).max()
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            d_percent = k_percent.rolling(window=3).mean()
            return k_percent.iloc[-1] if not k_percent.empty else 50, d_percent.iloc[-1] if not d_percent.empty else 50
        except:
            return 50, 50
    
    def calculate_williams_r(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
        """Calculate Williams %R."""
        try:
            highest_high = high.rolling(window=period).max()
            lowest_low = low.rolling(window=period).min()
            williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
            return williams_r.iloc[-1] if not williams_r.empty else -50
        except:
            return -50
    
    def calculate_cci(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 20) -> float:
        """Calculate Commodity Channel Index."""
        try:
            typical_price = (high + low + close) / 3
            sma_tp = typical_price.rolling(window=period).mean()
            mean_deviation = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
            cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
            return cci.iloc[-1] if not cci.empty else 0
        except:
            return 0
    
    def calculate_mfi(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, period: int = 14) -> float:
        """Calculate Money Flow Index."""
        try:
            typical_price = (high + low + close) / 3
            money_flow = typical_price * volume
            positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(window=period).sum()
            negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(window=period).sum()
            mfi = 100 - (100 / (1 + positive_flow / negative_flow))
            return mfi.iloc[-1] if not mfi.empty else 50
        except:
            return 50
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
        """Calculate Average True Range."""
        try:
            high_low = high - low
            high_close = np.abs(high - close.shift(1))
            low_close = np.abs(low - close.shift(1))
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            atr = true_range.rolling(window=period).mean()
            return atr.iloc[-1] if not atr.empty else 0
        except:
            return 0
    
    def calculate_obv(self, close: pd.Series, volume: pd.Series) -> float:
        """Calculate On Balance Volume."""
        try:
            price_change = close.diff()
            obv = (volume * np.sign(price_change)).cumsum()
            return obv.iloc[-1] if not obv.empty else 0
        except:
            return 0

    def _calculate_technical_score(self, indicators: Dict) -> float:
        """Calculate overall technical score based on indicators."""
        try:
            technical_score = 0
            
            # Momentum Indicators (40% of technical weight)
            momentum_score = 0
            rsi = indicators.get('rsi', 50)
            if rsi < 30:  # Oversold - bullish
                momentum_score += 0.8
            elif rsi < 40:  # Approaching oversold
                momentum_score += 0.6
            elif rsi > 70:  # Overbought - bearish
                momentum_score += 0.2
            elif rsi > 60:  # Approaching overbought
                momentum_score += 0.4
            else:  # Neutral zone
                momentum_score += 0.5
            
            # Stochastic
            stoch_k = indicators.get('stoch_k', 50)
            if stoch_k < 20:  # Oversold
                momentum_score += 0.3
            elif stoch_k > 80:  # Overbought
                momentum_score += 0.1
            else:
                momentum_score += 0.2
            
            # Williams %R
            williams_r = indicators.get('williams_r', -50)
            if williams_r < -80:  # Oversold
                momentum_score += 0.3
            elif williams_r > -20:  # Overbought
                momentum_score += 0.1
            else:
                momentum_score += 0.2
            
            momentum_score = min(momentum_score, 1.0)
            technical_score += momentum_score * 0.4
            
            # Trend Indicators (35% of technical weight)
            trend_score = 0
            current_price = indicators.get('current_price', 0)
            sma_10 = indicators.get('sma_10', current_price)
            sma_20 = indicators.get('sma_20', current_price)
            sma_50 = indicators.get('sma_50', current_price)
            
            # Moving Average Analysis
            if current_price > sma_10 > sma_20:  # Strong uptrend
                trend_score += 0.8
            elif current_price > sma_10:  # Weak uptrend
                trend_score += 0.6
            elif current_price < sma_10 < sma_20:  # Strong downtrend
                trend_score += 0.2
            elif current_price < sma_10:  # Weak downtrend
                trend_score += 0.4
            else:  # Sideways
                trend_score += 0.5
            
            # MACD Analysis
            macd = indicators.get('macd', 0)
            if macd > 0:  # Bullish MACD
                trend_score += 0.2
            else:  # Bearish MACD
                trend_score += 0.1
            
            trend_score = min(trend_score, 1.0)
            technical_score += trend_score * 0.35
            
            # Volatility Indicators (25% of technical weight)
            volatility_score = 0
            bb_upper = indicators.get('bb_upper', current_price)
            bb_lower = indicators.get('bb_lower', current_price)
            
            if bb_upper > bb_lower and current_price > 0:
                bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
                if bb_position < 0.2:  # Near lower band - potential bounce
                    volatility_score += 0.8
                elif bb_position > 0.8:  # Near upper band - potential pullback
                    volatility_score += 0.3
                else:  # Middle range
                    volatility_score += 0.5
            
            # ATR Analysis
            atr = indicators.get('atr', 0)
            if atr > 0 and current_price > 0:
                atr_ratio = atr / current_price
                if atr_ratio < 0.02:  # Low volatility - stable
                    volatility_score += 0.3
                elif atr_ratio > 0.05:  # High volatility - risky
                    volatility_score += 0.2
                else:  # Normal volatility
                    volatility_score += 0.3
            
            volatility_score = min(volatility_score, 1.0)
            technical_score += volatility_score * 0.25
            
            # Ensure technical score is between 0 and 1
            return max(0, min(1, technical_score))
            
        except Exception as e:
            logger.error(f"Error calculating technical score: {str(e)}")
            return 0.5  # Return neutral score on error

    def analyze_stock(self, symbol: str, period: str = '3mo') -> Dict:
        """Perform comprehensive technical analysis on stock."""
        try:
            # Fetch stock data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return {}
            
            # Calculate all technical indicators
            rsi = self.calculate_rsi(hist['Close'])
            macd = self.calculate_macd(hist['Close'])
            bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(hist['Close'])
            
            # Moving Averages
            sma_10 = self.calculate_sma(hist['Close'], 10)
            sma_20 = self.calculate_sma(hist['Close'], 20)
            sma_50 = self.calculate_sma(hist['Close'], 50)
            ema_12 = self.calculate_ema(hist['Close'], 12)
            ema_26 = self.calculate_ema(hist['Close'], 26)
            
            # Momentum Indicators
            stoch_k, stoch_d = self.calculate_stochastic(hist['High'], hist['Low'], hist['Close'])
            williams_r = self.calculate_williams_r(hist['High'], hist['Low'], hist['Close'])
            cci = self.calculate_cci(hist['High'], hist['Low'], hist['Close'])
            mfi = self.calculate_mfi(hist['High'], hist['Low'], hist['Close'], hist['Volume'])
            
            # Volatility Indicators
            atr = self.calculate_atr(hist['High'], hist['Low'], hist['Close'])
            obv = self.calculate_obv(hist['Close'], hist['Volume'])
            
            # Volume Analysis
            avg_volume_5 = hist['Volume'].rolling(window=5).mean().iloc[-1]
            avg_volume_20 = hist['Volume'].rolling(window=20).mean().iloc[-1]
            current_volume = hist['Volume'].iloc[-1]
            volume_ratio_5 = current_volume / avg_volume_5 if avg_volume_5 > 0 else 1
            volume_ratio_20 = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1
            
            # Price Analysis
            current_price = hist['Close'].iloc[-1]
            price_change_1d = hist['Close'].pct_change().iloc[-1] * 100
            price_change_5d = hist['Close'].pct_change(periods=5).iloc[-1] * 100
            price_change_20d = hist['Close'].pct_change(periods=20).iloc[-1] * 100
            
            # Trend Analysis
            trend_short = 1 if current_price > sma_10 > sma_20 else -1 if current_price < sma_10 < sma_20 else 0
            trend_medium = 1 if sma_20 > sma_50 else -1 if sma_20 < sma_50 else 0
            trend_long = 1 if current_price > sma_50 else -1 if current_price < sma_50 else 0
            
            # Calculate overall technical score
            technical_score = self._calculate_technical_score({
                'rsi': rsi, 'macd': macd, 'current_price': current_price,
                'sma_10': sma_10, 'sma_20': sma_20, 'sma_50': sma_50,
                'bb_upper': bb_upper, 'bb_lower': bb_lower, 'atr': atr,
                'williams_r': williams_r, 'stoch_k': stoch_k, 'stoch_d': stoch_d
            })
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                
                # Momentum Indicators
                'rsi': rsi,
                'stochastic_k': stoch_k,
                'stochastic_d': stoch_d,
                'williams_r': williams_r,
                'cci': cci,
                'mfi': mfi,
                
                # Trend Indicators
                'macd': macd,
                'sma_10': sma_10,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'ema_12': ema_12,
                'ema_26': ema_26,
                
                # Volatility Indicators
                'bb_upper': bb_upper,
                'bb_middle': bb_middle,
                'bb_lower': bb_lower,
                'atr': atr,
                
                # Volume Indicators
                'obv': obv,
                'volume_ratio_5': volume_ratio_5,
                'volume_ratio_20': volume_ratio_20,
                'current_volume': current_volume,
                'avg_volume_5': avg_volume_5,
                'avg_volume_20': avg_volume_20,
                
                # Price Analysis
                'price_change_1d': price_change_1d,
                'price_change_5d': price_change_5d,
                'price_change_20d': price_change_20d,
                
                # Trend Analysis
                'trend_short': trend_short,
                'trend_medium': trend_medium,
                'trend_long': trend_long,
                
                # Overall Score
                'technical_score': technical_score,
                
                # Additional metrics
                'volume_ratio': volume_ratio_20,  # For compatibility
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing stock {symbol}: {str(e)}")
            return {}
