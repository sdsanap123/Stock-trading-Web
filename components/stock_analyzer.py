"""
Stock Analysis Module
Handles AI-powered stock analysis including news sentiment and technical/fundamental analysis.
"""
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class StockAnalyzer:
    """Handles AI-powered stock analysis."""
    
    def __init__(self, api_key: str = None):
        """Initialize the stock analyzer."""
        self.news_api_key = api_key
        self.news_cache = {}
    
    def get_news_sentiment(self, symbol: str, days: int = 7) -> Dict:
        """
        Get news sentiment for a stock.
        
        Args:
            symbol: Stock symbol
            days: Number of days of news to analyze
            
        Returns:
            Dict containing sentiment analysis results
        """
        try:
            # Check cache first
            cache_key = f"{symbol}_{days}"
            if cache_key in self.news_cache:
                return self.news_cache[cache_key]
                
            # Get news using yfinance
            stock = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Try to get news from yfinance
            try:
                news = stock.news
                if news:
                    # Simple sentiment analysis (can be enhanced with NLP)
                    positive_keywords = ['buy', 'strong', 'growth', 'profit', 'upgrade', 'beat', 'surge']
                    negative_keywords = ['sell', 'weak', 'loss', 'downgrade', 'miss', 'fall', 'drop']
                    
                    sentiment_scores = []
                    for item in news:
                        title = item.get('title', '').lower()
                        summary = item.get('summary', '').lower()
                        text = f"{title} {summary}"
                        
                        positive = sum(1 for word in positive_keywords if word in text)
                        negative = sum(1 for word in negative_keywords if word in text)
                        
                        if positive > negative:
                            sentiment_scores.append(1)  # Positive
                        elif negative > positive:
                            sentiment_scores.append(-1)  # Negative
                        else:
                            sentiment_scores.append(0)  # Neutral
                    
                    avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0
                    
                    result = {
                        'sentiment_score': avg_sentiment,
                        'sentiment': 'Positive' if avg_sentiment > 0.1 else 
                                   'Negative' if avg_sentiment < -0.1 else 'Neutral',
                        'total_news': len(news),
                        'positive_news': sum(1 for s in sentiment_scores if s > 0),
                        'negative_news': sum(1 for s in sentiment_scores if s < 0),
                        'news_samples': [{
                            'title': item.get('title', ''),
                            'publisher': item.get('publisher', ''),
                            'link': item.get('link', '')
                        } for item in news[:3]]  # Include top 3 news items
                    }
                    
                    # Cache the result
                    self.news_cache[cache_key] = result
                    return result
            except Exception as e:
                logger.warning(f"Could not fetch news from yfinance for {symbol}: {str(e)}")
            
            # Fallback to web scraping if yfinance fails
            return self._scrape_news_sentiment(symbol, days)
            
        except Exception as e:
            logger.error(f"Error in get_news_sentiment for {symbol}: {str(e)}")
            return {
                'sentiment_score': 0,
                'sentiment': 'Neutral',
                'total_news': 0,
                'positive_news': 0,
                'negative_news': 0,
                'news_samples': []
            }
    
    def _scrape_news_sentiment(self, symbol: str, days: int) -> Dict:
        """Fallback method to scrape news from web."""
        # This is a placeholder - in a real app, you'd implement actual web scraping
        # or use a news API like NewsAPI, Alpha Vantage, etc.
        return {
            'sentiment_score': 0,
            'sentiment': 'Neutral',
            'total_news': 0,
            'positive_news': 0,
            'negative_news': 0,
            'news_samples': []
        }
    
    def get_technical_analysis(self, symbol: str) -> Dict:
        """
        Perform technical analysis on a stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict containing technical indicators
        """
        try:
            # Get historical data
            stock = yf.Ticker(symbol)
            hist = stock.history(period="1y")
            
            if hist.empty:
                return {}
            
            # Calculate technical indicators
            close_prices = hist['Close']
            
            # Simple Moving Averages
            sma_20 = close_prices.rolling(window=20).mean().iloc[-1]
            sma_50 = close_prices.rolling(window=50).mean().iloc[-1]
            sma_200 = close_prices.rolling(window=200).mean().iloc[-1]
            
            # RSI
            delta = close_prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            # MACD
            exp1 = close_prices.ewm(span=12, adjust=False).mean()
            exp2 = close_prices.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            macd_hist = macd - signal
            
            # Current price and volume
            current_price = close_prices.iloc[-1]
            volume = hist['Volume'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            
            # Generate signals
            signals = []
            if current_price > sma_20 and current_price > sma_50 and current_price > sma_200:
                signals.append("Price above all key moving averages (Bullish)")
            elif current_price < sma_20 and current_price < sma_50 and current_price < sma_200:
                signals.append("Price below all key moving averages (Bearish)")
                
            if rsi > 70:
                signals.append("RSI indicates overbought conditions")
            elif rsi < 30:
                signals.append("RSI indicates oversold conditions")
                
            if macd_hist.iloc[-1] > 0 and macd_hist.iloc[-2] <= 0:
                signals.append("MACD bullish crossover")
            elif macd_hist.iloc[-1] < 0 and macd_hist.iloc[-2] >= 0:
                signals.append("MACD bearish crossover")
            
            return {
                'sma_20': sma_20,
                'sma_50': sma_50,
                'sma_200': sma_200,
                'rsi': rsi,
                'macd': macd.iloc[-1],
                'signal': signal.iloc[-1],
                'macd_hist': macd_hist.iloc[-1],
                'current_price': current_price,
                'volume': volume,
                'volume_ratio': volume / avg_volume if avg_volume > 0 else 1,
                'signals': signals
            }
            
        except Exception as e:
            logger.error(f"Error in technical analysis for {symbol}: {str(e)}")
            return {}
    
    def get_fundamental_analysis(self, symbol: str) -> Dict:
        """
        Perform fundamental analysis on a stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict containing fundamental metrics
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            if not info:
                return {}
            
            # Get key metrics
            metrics = {
                'company_name': info.get('shortName', symbol),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'profit_margin': info.get('profitMargins'),
                'return_on_equity': info.get('returnOnEquity'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'fifty_day_ma': info.get('fiftyDayAverage'),
                'two_hundred_day_ma': info.get('twoHundredDayAverage')
            }
            
            # Clean up the metrics
            for key, value in metrics.items():
                if isinstance(value, float):
                    metrics[key] = round(value, 4) if value is not None else None
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error in fundamental analysis for {symbol}: {str(e)}")
            return {}
    
    def analyze_stock(self, symbol: str) -> Dict:
        """
        Perform complete analysis of a stock.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dict containing all analysis results
        """
        try:
            # Get all analyses
            news = self.get_news_sentiment(symbol)
            technical = self.get_technical_analysis(symbol)
            fundamental = self.get_fundamental_analysis(symbol)
            
            # Calculate overall score (simple weighted average)
            score = 0
            weight_news = 0.3
            weight_technical = 0.4
            weight_fundamental = 0.3
            
            # News sentiment score (-1 to 1 scaled to 0-100)
            news_score = (news.get('sentiment_score', 0) + 1) * 50 if news else 50
            
            # Technical score based on signals
            tech_signals = technical.get('signals', [])
            tech_score = 50  # Neutral
            for signal in tech_signals:
                if 'bullish' in signal.lower():
                    tech_score += 10
                elif 'bearish' in signal.lower():
                    tech_score -= 10
                elif 'overbought' in signal.lower():
                    tech_score -= 5
                elif 'oversold' in signal.lower():
                    tech_score += 5
            
            # Fundamental score based on key metrics
            fund_score = 50  # Neutral
            pe = fundamental.get('pe_ratio', 0) or 0
            if 0 < pe < 20:  # Good P/E range
                fund_score += 10
            elif pe >= 20:
                fund_score -= 5
                
            roe = fundamental.get('return_on_equity', 0) or 0
            if roe > 0.15:  # Good ROE
                fund_score += 10
                
            profit_margin = fundamental.get('profit_margin', 0) or 0
            if profit_margin > 0.1:  # Good profit margin
                fund_score += 5
            
            # Calculate weighted score
            score = (news_score * weight_news + 
                    tech_score * weight_technical + 
                    fund_score * weight_fundamental)
            
            # Generate recommendation
            if score >= 70:
                recommendation = "STRONG BUY"
            elif score >= 60:
                recommendation = "BUY"
            elif score >= 40:
                recommendation = "HOLD"
            elif score >= 30:
                recommendation = "SELL"
            else:
                recommendation = "STRONG SELL"
            
            # Compile results
            return {
                'symbol': symbol,
                'overall_score': round(score, 1),
                'recommendation': recommendation,
                'news_analysis': news,
                'technical_analysis': technical,
                'fundamental_analysis': fundamental,
                'analysis_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'score_breakdown': {
                    'news_score': round(news_score, 1),
                    'technical_score': tech_score,
                    'fundamental_score': fund_score
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing stock {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'error': f"Analysis failed: {str(e)}"
            }
