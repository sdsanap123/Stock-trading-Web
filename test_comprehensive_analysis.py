#!/usr/bin/env python3
"""
Test script to verify comprehensive Groq analysis integration.
"""

import os
import sys
sys.path.append('.')

from components.groq_analyzer import GroqNewsAnalyzer

def test_comprehensive_analysis():
    """Test comprehensive Groq analysis with sample data."""
    print("🧪 Testing Comprehensive Groq Analysis...")
    
    # Check if API key is set
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ GROQ_API_KEY environment variable not set")
        print("Please set your Groq API key:")
        print("export GROQ_API_KEY='your_api_key_here'")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    # Initialize analyzer
    analyzer = GroqNewsAnalyzer()
    
    if not analyzer.initialized:
        print("❌ Groq analyzer not initialized")
        return False
    
    print("✅ Groq analyzer initialized successfully")
    
    # Sample technical data
    technical_data = {
        'current_price': 2500.50,
        'rsi': 45.2,
        'macd': 12.5,
        'stochastic_k': 55.8,
        'williams_r': -44.2,
        'bb_upper': 2600.0,
        'bb_middle': 2500.0,
        'bb_lower': 2400.0,
        'sma_10': 2480.0,
        'sma_20': 2450.0,
        'sma_50': 2400.0,
        'volume_ratio_20': 1.2,
        'price_change_1d': 2.5,
        'price_change_5d': 5.8,
        'price_change_20d': 12.3,
        'trend_short': 0.6,
        'trend_medium': 0.7,
        'trend_long': 0.8,
        'technical_score': 0.65
    }
    
    # Sample fundamental data
    fundamental_data = {
        'pe_ratio': 18.5,
        'pb_ratio': 2.1,
        'roe': 15.2,
        'roa': 8.5,
        'debt_equity': 0.3,
        'current_ratio': 2.5,
        'score': 0.72
    }
    
    # Sample news data
    news_articles = [
        {
            'title': 'Company reports strong quarterly earnings',
            'description': 'The company exceeded expectations with 15% revenue growth',
            'sentiment_score': 0.7
        },
        {
            'title': 'New product launch announced',
            'description': 'Company announces innovative new product line',
            'sentiment_score': 0.8
        }
    ]
    
    # Test comprehensive analysis
    print("\n🔍 Testing comprehensive stock analysis...")
    
    try:
        result = analyzer.get_comprehensive_stock_analysis(
            'RELIANCE', technical_data, fundamental_data, news_articles
        )
        
        if result.get('status') == 'success':
            print("✅ Comprehensive Groq analysis successful!")
            print(f"📊 Overall Score: {result.get('overall_score', 0):.2f}")
            print(f"🎯 Recommendation: {result.get('recommendation', 'N/A')}")
            print(f"🎲 Confidence: {result.get('confidence', 0):.1%}")
            print(f"⚠️ Risk Assessment: {result.get('risk_assessment', 'N/A')}")
            print(f"⏰ Time Horizon: {result.get('time_horizon', 'N/A')}")
            print(f"💰 Price Target: {result.get('price_target', 'N/A')}")
            print(f"🛑 Stop Loss: {result.get('stop_loss', 'N/A')}")
            print(f"📝 Reasoning: {result.get('reasoning', 'N/A')[:100]}...")
            print(f"🔑 Key Factors: {', '.join(result.get('key_factors', []))}")
            return True
        else:
            print(f"❌ Comprehensive analysis failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during comprehensive analysis test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_comprehensive_analysis()
    if success:
        print("\n🎉 Comprehensive analysis test passed! The integration is working correctly.")
    else:
        print("\n💥 Comprehensive analysis test failed. Please check your API key and try again.")
