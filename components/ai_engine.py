#!/usr/bin/env python3
"""
AI Recommendation Engine Component
AI-powered recommendation engine with learning capabilities.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AIRecommendationEngine:
    """AI-powered recommendation engine with learning capabilities."""
    
    def __init__(self):
        self.learning_data = []
        self.performance_history = []
        self.recommendation_tracker = None
        self.ai_weights = {
            'technical': 0.3,
            'fundamental': 0.25,
            'sentiment': 0.2,
            'catalysts': 0.15,
            'market_conditions': 0.1
        }
        
        # Initialize fundamental analyzer
        try:
            from .fundamental_analyzer import FundamentalAnalyzer
            self.fundamental_analyzer = FundamentalAnalyzer()
            logger.info("Fundamental analyzer initialized successfully")
        except ImportError as e:
            logger.warning(f"Could not import fundamental analyzer: {str(e)}")
            self.fundamental_analyzer = None
        except Exception as e:
            logger.warning(f"Fundamental analyzer initialization failed: {str(e)}")
            self.fundamental_analyzer = None
        
        self.fundamental_ratings = {}
        logger.info("AI Recommendation Engine initialized with learning capabilities")
    
    def set_fundamental_analyzer(self, fundamental_analyzer):
        """Set the fundamental analyzer instance."""
        self.fundamental_analyzer = fundamental_analyzer
        if fundamental_analyzer:
            logger.info("Fundamental analyzer set successfully")
        else:
            logger.warning("Fundamental analyzer set to None")
    
    def generate_ai_recommendation(self, stock_data: Dict, technical_analysis: Dict, 
                                 news_sentiment: float, catalysts: List[str], groq_analysis: Dict = None, 
                                 gemini_analysis: Dict = None, use_fundamental: bool = True) -> Dict:
        """Generate AI-powered recommendation with comprehensive analysis."""
        try:
            # AI scoring based on multiple factors
            ai_score = 0
            
            # Technical analysis weight (30%) - Now using comprehensive indicators
            technical_score = 0
            
            # Momentum Indicators (40% of technical weight)
            momentum_score = 0
            if technical_analysis.get('rsi', 0) != 0:
                rsi = technical_analysis.get('rsi', 50)
                if rsi < 30:  # Oversold - bullish
                    momentum_score += 0.8
                elif rsi < 40:  # Approaching oversold
                    momentum_score += 0.6
                elif rsi > 70:  # Overbought - bearish
                    momentum_score += 0.2
                elif rsi > 60:  # Approaching overbought
                    momentum_score += 0.4
                else:  # Neutral
                    momentum_score += 0.5
            
            if technical_analysis.get('stochastic_k', 0) != 0:
                stoch_k = technical_analysis.get('stochastic_k', 50)
                if stoch_k < 20:  # Oversold
                    momentum_score += 0.3
                elif stoch_k > 80:  # Overbought
                    momentum_score += 0.1
                else:
                    momentum_score += 0.2
            
            if technical_analysis.get('williams_r', 0) != 0:
                williams_r = technical_analysis.get('williams_r', -50)
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
            current_price = technical_analysis.get('current_price', 0)
            
            # Moving Average Analysis
            sma_10 = technical_analysis.get('sma_10', current_price)
            sma_20 = technical_analysis.get('sma_20', current_price)
            sma_50 = technical_analysis.get('sma_50', current_price)
            
            if current_price > sma_10 > sma_20 > sma_50:  # Strong uptrend
                trend_score += 0.8
            elif current_price > sma_10 > sma_20:  # Medium uptrend
                trend_score += 0.6
            elif current_price > sma_20:  # Weak uptrend
                trend_score += 0.4
            elif current_price < sma_10 < sma_20 < sma_50:  # Strong downtrend
                trend_score += 0.2
            elif current_price < sma_10 < sma_20:  # Medium downtrend
                trend_score += 0.3
            elif current_price < sma_20:  # Weak downtrend
                trend_score += 0.35
            else:  # Sideways
                trend_score += 0.5
            
            # MACD Analysis
            macd = technical_analysis.get('macd', 0)
            if macd > 0:  # Bullish MACD
                trend_score += 0.2
            else:  # Bearish MACD
                trend_score += 0.1
            
            trend_score = min(trend_score, 1.0)
            technical_score += trend_score * 0.35
            
            # Volatility Indicators (25% of technical weight)
            volatility_score = 0
            bb_upper = technical_analysis.get('bb_upper', current_price)
            bb_lower = technical_analysis.get('bb_lower', current_price)
            
            if bb_upper > bb_lower and current_price > 0:
                bb_position = (current_price - bb_lower) / (bb_upper - bb_lower)
                if bb_position < 0.2:  # Near lower band - potential bounce
                    volatility_score += 0.8
                elif bb_position > 0.8:  # Near upper band - potential pullback
                    volatility_score += 0.3
                else:  # Middle range
                    volatility_score += 0.5
            
            # ATR Analysis for volatility
            atr = technical_analysis.get('atr', 0)
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
            technical_score = max(0, min(1, technical_score))
            ai_score += technical_score * self.ai_weights['technical']
            
            # Fundamental analysis weight (25%) - Now using REAL fundamental data
            fundamental_score = 0.0
            
            # Try to get real fundamental analysis if available
            if use_fundamental and hasattr(self, 'fundamental_analyzer') and self.fundamental_analyzer:
                try:
                    # Get fundamental data for the stock
                    symbol = stock_data.get('symbol', '')
                    if symbol:
                        # Add .NS suffix for NSE stocks if not present
                        if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                            symbol_with_suffix = f"{symbol}.NS"
                        else:
                            symbol_with_suffix = symbol
                        
                        # Fetch and analyze fundamental data
                        financial_data = self.fundamental_analyzer.get_financial_data(symbol_with_suffix)
                        if financial_data:
                            fundamental_analysis = self.fundamental_analyzer.calculate_fundamental_score(financial_data)
                            fundamental_score = fundamental_analysis.get('score', 0.0)
                            
                            # Add fundamental ratings to reasoning
                            ratings = fundamental_analysis.get('ratings', {})
                            if ratings:
                                self.fundamental_ratings = ratings
                        else:
                            logger.warning(f"No fundamental data available for {symbol_with_suffix}")
                    else:
                        logger.warning("Symbol missing - cannot fetch fundamental data")
                except Exception as e:
                    logger.warning(f"Could not perform fundamental analysis: {str(e)}")
                    fundamental_score = 0.0
            else:
                # Explicitly clear ratings when fundamentals are disabled
                self.fundamental_ratings = {}
                if use_fundamental and not hasattr(self, 'fundamental_analyzer'):
                    logger.warning("Fundamental analyzer not available - fundamental score will stay at 0")
            
            # Ensure fundamental score is between 0 and 1
            fundamental_score = max(0, min(1, fundamental_score))
            ai_score += fundamental_score * self.ai_weights['fundamental']
            
            # Sentiment weight (20%) - Enhanced with Groq AI
            if groq_analysis and groq_analysis.get('source') == 'Groq API':
                # Use Groq AI analysis if available
                groq_sentiment = groq_analysis.get('sentiment_score', 0)
                groq_confidence = groq_analysis.get('confidence', 50) / 100
                
                # Weight Groq AI sentiment by its confidence
                sentiment_score = 0.5 + (groq_sentiment * groq_confidence * 0.5)
                sentiment_score = max(0, min(1, sentiment_score))
                
                # Store Groq AI insights for reasoning
                self.groq_insights = groq_analysis.get('key_insights', [])
                self.groq_source = groq_analysis.get('source', 'Groq API')
            else:
                # Groq AI service unavailable - use traditional sentiment analysis
                sentiment_score = (news_sentiment + 1) / 2  # Convert -1 to 1 range to 0 to 1
                self.groq_insights = []
                self.groq_source = 'Groq API Unavailable'
            
            ai_score += sentiment_score * self.ai_weights['sentiment']
            
            # Catalyst weight (15%)
            catalyst_score = min(len(catalysts) / 3, 1.0)  # Max 3 catalysts
            ai_score += catalyst_score * self.ai_weights['catalysts']
            
            # Market conditions (10%) - Enhanced with trend analysis
            market_score = 0.5  # Base neutral score
            
            # Add trend-based market score
            trend_short = technical_analysis.get('trend_short', 0)
            trend_medium = technical_analysis.get('trend_medium', 0)
            
            if trend_short > 0 and trend_medium > 0:  # Both trends bullish
                market_score += 0.3
            elif trend_short > 0 or trend_medium > 0:  # One trend bullish
                market_score += 0.15
            elif trend_short < 0 and trend_medium < 0:  # Both trends bearish
                market_score -= 0.3
            elif trend_short < 0 or trend_medium < 0:  # One trend bearish
                market_score -= 0.15
            
            market_score = max(0, min(1, market_score))
            ai_score += market_score * self.ai_weights['market_conditions']
            
            # Gemini AI analysis weight (20%) - if available
            if gemini_analysis and gemini_analysis.get('status') == 'success':
                gemini_score = gemini_analysis.get('analysis', {}).get('overall_score', 0.5)
                gemini_confidence = gemini_analysis.get('analysis', {}).get('confidence', 0.5)
                
                # Weight Gemini AI score by its confidence
                weighted_gemini_score = 0.5 + (gemini_score - 0.5) * gemini_confidence
                weighted_gemini_score = max(0, min(1, weighted_gemini_score))
                
                # Add Gemini AI score to overall AI score
                ai_score += weighted_gemini_score * 0.2
                
                # Store Gemini insights for reasoning
                self.gemini_insights = gemini_analysis.get('analysis', {}).get('key_insights', [])
                self.gemini_recommendation = gemini_analysis.get('analysis', {}).get('recommendation', 'HOLD')
            else:
                self.gemini_insights = []
                self.gemini_recommendation = 'HOLD'
            
            # Ensure AI score is between 0 and 1
            ai_score = max(0, min(1, ai_score))
            
            # Determine recommendation based on AI score
            if ai_score >= 0.55:       # Strong bullish signal
                action = 'BUY'
                confidence = min(95, ai_score * 100)
            elif ai_score >= 0.35:     # Neutral / wait
                action = 'HOLD'
                confidence = min(70, ai_score * 80)
            else:                      # Bearish signal
                action = 'SELL'
                confidence = min(95, (1 - ai_score) * 100)

            # Calculate target price and stop loss
            current_price = technical_analysis.get('current_price', 0)
            if current_price > 0:
                if action == 'BUY':
                    # 7-day swing: target upside scaled to score, 8% stop loss
                    target_price = current_price * (1 + (ai_score - 0.55) * 0.35)
                    stop_loss    = current_price * 0.92
                elif action == 'SELL':
                    # Short / exit target: scaled downside, 6% stop above entry
                    target_price = current_price * (1 - (0.35 - ai_score) * 0.40)
                    stop_loss    = current_price * 1.06
                else:  # HOLD
                    target_price = 0
                    stop_loss    = 0
            else:
                target_price = 0
                stop_loss    = 0
            
            # Generate comprehensive reasoning
            reasoning = self._generate_reasoning(
                technical_score, fundamental_score, sentiment_score, 
                catalyst_score, market_score, ai_score, action, confidence,
                technical_analysis, groq_analysis, gemini_analysis,
                use_fundamental=use_fundamental
            )
            
            # Create recommendation result
            recommendation = {
                'action': action,
                'confidence': confidence,
                'target_price': target_price,
                'stop_loss': stop_loss,
                'reasoning': reasoning,
                'ai_score': ai_score,
                'technical_score': technical_score,
                'fundamental_score': fundamental_score,
                'sentiment_score': sentiment_score,
                'catalyst_score': catalyst_score,
                'market_score': market_score,
                'timestamp': datetime.now().isoformat()
            }
            
            # Track recommendation for learning
            if self.recommendation_tracker:
                try:
                    tracking_data = {
                        'symbol': stock_data.get('symbol', ''),
                        'action': action,
                        'confidence': confidence,
                        'target_price': target_price,
                        'stop_loss': stop_loss,
                        'ai_score': ai_score,
                        'technical_data': technical_analysis,
                        'fundamental_data': self.fundamental_ratings,
                        'groq_analysis': groq_analysis,
                        'gemini_analysis': gemini_analysis,
                        'created_at': datetime.now().isoformat()
                    }
                    self.recommendation_tracker.track_recommendation(tracking_data)
                except Exception as e:
                    logger.warning(f"Could not track recommendation: {str(e)}")
            
            logger.info(f"Generated {action} recommendation for {stock_data.get('symbol', 'N/A')} with {confidence:.1f}% confidence")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating AI recommendation: {str(e)}")
            return {
                'action': 'HOLD',
                'confidence': 0,
                'target_price': 0,
                'stop_loss': 0,
                'reasoning': f"Error in analysis: {str(e)}",
                'ai_score': 0,
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_reasoning(self, technical_score: float, fundamental_score: float, 
                          sentiment_score: float, catalyst_score: float, market_score: float,
                          ai_score: float, action: str, confidence: float,
                          technical_analysis: Dict, groq_analysis: Dict = None, 
                          gemini_analysis: Dict = None, use_fundamental: bool = True) -> str:
        """Generate comprehensive reasoning for the recommendation."""
        try:
            reasoning_parts = []
            
            # Overall assessment
            reasoning_parts.append(f"AI Analysis Score: {ai_score:.2f}/1.0")
            reasoning_parts.append(f"Recommendation: {action} (Confidence: {confidence:.1f}%)")
            reasoning_parts.append("")
            
            # Technical Analysis
            reasoning_parts.append("📈 TECHNICAL ANALYSIS:")
            reasoning_parts.append(f"• Technical Score: {technical_score:.2f}/1.0")
            
            # RSI Analysis
            rsi = technical_analysis.get('rsi', 0)
            if rsi > 0:
                if rsi < 30:
                    reasoning_parts.append(f"• RSI: {rsi:.1f} (Oversold - Bullish)")
                elif rsi > 70:
                    reasoning_parts.append(f"• RSI: {rsi:.1f} (Overbought - Bearish)")
                else:
                    reasoning_parts.append(f"• RSI: {rsi:.1f} (Neutral)")
            
            # Moving Averages
            current_price = technical_analysis.get('current_price', 0)
            sma_20 = technical_analysis.get('sma_20', 0)
            sma_50 = technical_analysis.get('sma_50', 0)
            
            if current_price > 0 and sma_20 > 0:
                if current_price > sma_20:
                    reasoning_parts.append(f"• Price above SMA 20: Bullish trend")
                else:
                    reasoning_parts.append(f"• Price below SMA 20: Bearish trend")
            
            if sma_20 > 0 and sma_50 > 0:
                if sma_20 > sma_50:
                    reasoning_parts.append(f"• SMA 20 > SMA 50: Uptrend")
                else:
                    reasoning_parts.append(f"• SMA 20 < SMA 50: Downtrend")
            
            # MACD
            macd = technical_analysis.get('macd', 0)
            if macd > 0:
                reasoning_parts.append(f"• MACD: {macd:.3f} (Bullish)")
            else:
                reasoning_parts.append(f"• MACD: {macd:.3f} (Bearish)")
            
            reasoning_parts.append("")
            
            # Fundamental Analysis
            reasoning_parts.append("📊 FUNDAMENTAL ANALYSIS:")
            reasoning_parts.append(f"• Fundamental Score: {fundamental_score:.2f}/1.0")
            
            if not use_fundamental:
                reasoning_parts.append("• Fundamental analysis disabled for this run")
            elif self.fundamental_ratings:
                for metric, rating in self.fundamental_ratings.items():
                    reasoning_parts.append(f"• {metric}: {rating}")
            else:
                reasoning_parts.append("• No fundamental data available")
            
            reasoning_parts.append("")
            
            # Sentiment Analysis
            reasoning_parts.append("📰 SENTIMENT ANALYSIS:")
            reasoning_parts.append(f"• Sentiment Score: {sentiment_score:.2f}/1.0")
            
            if groq_analysis and groq_analysis.get('source') == 'Groq API':
                reasoning_parts.append(f"• Groq AI Analysis: {self.groq_source}")
                if self.groq_insights:
                    reasoning_parts.append("• Key Insights:")
                    for insight in self.groq_insights[:3]:  # Show top 3 insights
                        reasoning_parts.append(f"  - {insight}")
            else:
                reasoning_parts.append("• Groq AI: Unavailable")
            
            reasoning_parts.append("")
            
            # Gemini AI Analysis
            if gemini_analysis and gemini_analysis.get('status') == 'success':
                reasoning_parts.append("🧠 GEMINI AI ANALYSIS:")
                gemini_analysis_data = gemini_analysis.get('analysis', {})
                reasoning_parts.append(f"• Gemini Recommendation: {self.gemini_recommendation}")
                reasoning_parts.append(f"• Overall Score: {gemini_analysis_data.get('overall_score', 0):.2f}")
                reasoning_parts.append(f"• Confidence: {gemini_analysis_data.get('confidence', 0):.1%}")
                
                if self.gemini_insights:
                    reasoning_parts.append("• Key Insights:")
                    for insight in self.gemini_insights[:3]:  # Show top 3 insights
                        reasoning_parts.append(f"  - {insight}")
                
                reasoning_parts.append("")
            
            # Market Conditions
            reasoning_parts.append("🌍 MARKET CONDITIONS:")
            reasoning_parts.append(f"• Market Score: {market_score:.2f}/1.0")
            reasoning_parts.append(f"• Catalyst Score: {catalyst_score:.2f}/1.0")
            
            # Risk Assessment
            reasoning_parts.append("")
            reasoning_parts.append("⚠️ RISK ASSESSMENT:")
            if confidence >= 80:
                reasoning_parts.append("• High confidence recommendation")
            elif confidence >= 60:
                reasoning_parts.append("• Medium confidence recommendation")
            else:
                reasoning_parts.append("• Low confidence recommendation")
            
            if action == 'BUY':
                reasoning_parts.append("• 7-Day Swing Strategy: Short-term LONG position with 8% stop loss")
                reasoning_parts.append("• Consider position sizing based on risk tolerance")
                reasoning_parts.append("• Monitor daily for exit signals or target achievement")
                reasoning_parts.append("• Set stop loss to limit downside risk")
            elif action == 'SELL':
                reasoning_parts.append("• Bearish signal: Consider SHORT or EXIT any existing position")
                reasoning_parts.append("• 6% stop loss above entry to cap upside risk")
                reasoning_parts.append("• Monitor for reversal signals before acting")
                reasoning_parts.append("• Confirm with volume and broader market trend")
            else:  # HOLD
                reasoning_parts.append("• Neutral signal: No clear directional edge")
                reasoning_parts.append("• Avoid initiating new positions until bias clarifies")
                reasoning_parts.append("• Watch for BUY or SELL trigger conditions")
            
            return "\n".join(reasoning_parts)
            
        except Exception as e:
            logger.error(f"Error generating reasoning: {str(e)}")
            return f"Error generating detailed reasoning: {str(e)}"
    
    def update_weights(self, new_weights: Dict):
        """Update AI weights based on performance."""
        try:
            for key, value in new_weights.items():
                if key in self.ai_weights and 0 <= value <= 1:
                    self.ai_weights[key] = value
            
            logger.info(f"Updated AI weights: {self.ai_weights}")
            
        except Exception as e:
            logger.error(f"Error updating weights: {str(e)}")
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary of recommendations."""
        try:
            if not self.recommendation_tracker:
                return {"error": "Recommendation tracker not available"}
            
            return self.recommendation_tracker.get_performance_summary()
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {str(e)}")
            return {"error": str(e)}
