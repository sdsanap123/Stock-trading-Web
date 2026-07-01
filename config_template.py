#!/usr/bin/env python3
"""
Configuration Template for Enhanced Swing Trading App
Copy this file to config.py and add your actual API keys
"""

# API Configuration
# Get your API keys from the respective services

# Groq API Key - Get from https://console.groq.com/
GROQ_API_KEY = "gsk_your_groq_api_key_here"

# Gemini API Key - Get from https://makersuite.google.com/app/apikey
GEMINI_API_KEY = "AIza_your_gemini_api_key_here"

# Optional: Firebase Configuration (for cloud sync)
FIREBASE_PROJECT_ID = "your_firebase_project_id"
FIREBASE_PRIVATE_KEY = "your_firebase_private_key"
FIREBASE_CLIENT_EMAIL = "your_firebase_client_email"

# Application Settings
CACHE_DURATION_HOURS = 24
MAX_RECOMMENDATIONS = 50
NEWS_SOURCES = [
    'https://feeds.finance.yahoo.com/rss/2.0/headline',
    'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
    'https://www.moneycontrol.com/rss/business.xml'
]

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "enhanced_trading.log"
