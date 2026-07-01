# Enhanced Swing Trading App - AI Powered

## Overview
A comprehensive stock analysis and trading application with AI-powered recommendations, built with Streamlit. This web application provides real-time stock analysis, technical and fundamental indicators, AI-powered news sentiment analysis, and swing trading strategies for the Indian stock market.

**Purpose**: Stock market analysis and swing trading recommendations  
**Technology**: Python 3.11, Streamlit web application  
**Current State**: ✅ Running and ready to use

## Recent Changes (Oct 24, 2025)
- Configured for Replit environment
- Updated to use port 5000 with 0.0.0.0 host
- Migrated API key storage to use Replit Secrets (environment variables)
- Removed insecure local file-based API key storage
- Added Streamlit configuration for proper hosting
- Set up deployment configuration for autoscale

## Project Architecture

### Main Components
- **app.py**: Main Streamlit web application with UI and orchestration
- **run.py**: Alternative entry point for running the app
- **components/**: Analysis modules
  - `ai_engine.py`: AI recommendation engine with multi-factor analysis
  - `technical_analyzer.py`: Technical indicators (RSI, MACD, Bollinger Bands, etc.)
  - `fundamental_analyzer.py`: Financial metrics and ratios
  - `news_analyzer.py`: News fetching and sentiment analysis
  - `groq_analyzer.py`: Groq AI integration for advanced analysis
  - `gemini_analyzer.py`: Google Gemini AI integration
  - `watchlist_manager.py`: Stock watchlist management
  - `recommendation_learning.py`: Learning system for improving recommendations
  - `swing_strategy.py`: 7-day swing trading strategy
  - `price_monitor.py`: Real-time price monitoring
  - `email_notifications.py`: Alert system
  - `cache_manager.py`: API response caching
  - `data_persistence.py`: Data storage and retrieval

### Key Features
1. **AI-Powered Analysis**
   - Multi-factor AI recommendations
   - Groq AI news sentiment analysis
   - Gemini AI comprehensive stock analysis
   - Continuous learning from performance

2. **Technical Analysis**
   - Comprehensive indicators: RSI, MACD, Bollinger Bands, Stochastic, Williams %R, CCI, MFI, ATR, OBV
   - Moving averages with multiple timeframes
   - Trend analysis (short, medium, long-term)
   - Volume analysis

3. **Fundamental Analysis**
   - Financial metrics: P/E, P/B, P/S ratios, ROE, ROA, Debt/Equity
   - Growth analysis: Revenue and earnings growth
   - Profitability metrics

4. **News Analysis**
   - Multi-source Indian stock market news
   - Sentiment analysis with TextBlob
   - AI-powered news analysis with Groq

5. **Watchlist & Portfolio**
   - Smart watchlist with performance tracking
   - Real-time price updates
   - Learning from watchlist performance

## API Keys & Secrets

### Required Secrets (Optional but Recommended)
Add these secrets in the Replit Secrets panel for enhanced features:

1. **GROQ_API_KEY** (Recommended)
   - Get from: https://console.groq.com/
   - Enables: AI-powered news sentiment analysis, advanced stock insights
   - Models: llama3-70b-8192, mixtral-8x7b-32768 with automatic fallback

2. **GEMINI_API_KEY** (Optional)
   - Get from: https://makersuite.google.com/app/apikey
   - Enables: Comprehensive stock analysis, learning system integration

**Note**: The app works without API keys but with limited AI features.

### How to Add Secrets
1. Click the "Secrets" icon in the left sidebar (🔒)
2. Add `GROQ_API_KEY` with your Groq API key
3. Add `GEMINI_API_KEY` with your Gemini API key (optional)
4. Restart the application to load the secrets

## Running the Application

### In Replit
The application runs automatically via the workflow. Just open the Webview to see the app.

### Locally (if needed)
```bash
streamlit run app.py
```

## Usage Guide

### Tabs Overview
1. **📰 News**: Fetch and analyze market news with sentiment scores
2. **🤖 Groq**: AI-powered news analysis (requires GROQ_API_KEY)
3. **🎯 BUY**: AI-generated stock recommendations with confidence levels
4. **📈 Swing**: 7-day swing trading strategies
5. **👀 Watch**: Manage and track your stock watchlist
6. **🔍 Manual**: Analyze individual stocks
7. **📊 Portfolio**: Portfolio tracking and performance
8. **🔔 Alerts**: Price alerts and notifications

### Quick Start
1. Open the application in the Webview
2. (Optional) Add API keys in Replit Secrets
3. Navigate to "🎯 BUY" tab
4. Click "📊 Analyze Market" in the sidebar
5. View AI-generated recommendations
6. Add stocks to watchlist for tracking

## Data Storage

### Local Storage (Replit)
- **saved_data/**: Stores watchlist, recommendations, and swing strategies
- **data/**: Stores persistent application data
- All data persists across restarts in Replit

### Firebase Sync (Optional)
- Configure `firebase_config.json` for cloud sync
- Syncs watchlist and recommendations across devices

## Deployment

The app is configured for **autoscale deployment** which:
- Scales automatically based on traffic
- Only runs when users access the app
- Suitable for web applications with variable traffic

To deploy, click the "Deploy" button in Replit.

## User Preferences

**Coding Style**: Python with type hints where beneficial  
**Framework**: Streamlit for web UI  
**Data Source**: yfinance for stock data, RSS feeds for news  
**AI Providers**: Groq (primary), Google Gemini (optional)

## Troubleshooting

### "Groq AI not initialized" or "Gemini AI not initialized"
- Add the respective API key to Replit Secrets
- Restart the workflow

### "No news articles found"
- This is normal - the app fetches real-time news
- Try again later or check internet connectivity

### Application not loading
- Check workflow status (should be RUNNING)
- View logs for error messages
- Ensure port 5000 is accessible

## Security Notes

- API keys are stored in Replit Secrets (environment variables)
- Never commit API keys to the repository
- Keys are not exposed in logs or UI
- Use HTTPS in production deployment

## Support

For issues or questions:
1. Check the workflow logs in Replit
2. Verify API keys are set correctly in Secrets
3. Ensure all dependencies are installed (they auto-install)
4. Check network connectivity for news fetching
