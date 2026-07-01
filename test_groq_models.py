#!/usr/bin/env python3
"""
Test script to verify Groq API works with the correct models from original app.
"""

import os
import sys
sys.path.append('.')

from components.groq_analyzer import GroqNewsAnalyzer

def test_groq_models():
    """Test Groq API with the models from original app."""
    print("🧪 Testing Groq API with models from original app...")
    
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
    
    # Test the models by making a simple request
    print("\n🔍 Testing model fallback system...")
    
    try:
        # This will test the model fallback system
        result = analyzer.fetch_and_analyze_indian_stock_news()
        
        if result.get('status') == 'success':
            print("✅ Groq API test successful!")
            print(f"📊 Analyzed {len(result.get('articles', []))} stocks")
            print(f"🕒 Timestamp: {result.get('timestamp', 'N/A')}")
            return True
        else:
            print(f"❌ Groq API test failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during Groq API test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_groq_models()
    if success:
        print("\n🎉 All tests passed! Groq API is working with the correct models.")
    else:
        print("\n💥 Tests failed. Please check your API key and try again.")
