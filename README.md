# Enhanced Swing Trading App - Web Version

A comprehensive stock analysis and trading application with AI-powered recommendations, converted to Streamlit web application.

## Features

### 🤖 AI-Powered Analysis
- **AI Recommendation Engine**: Multi-factor analysis combining technical, fundamental, and sentiment data
- **Groq AI Integration**: Advanced news sentiment analysis
- **Gemini AI Integration**: Comprehensive stock analysis with learning capabilities
- **Learning System**: Continuous improvement through performance tracking

### 📊 Technical Analysis
- **Comprehensive Indicators**: RSI, MACD, Bollinger Bands, Stochastic, Williams %R, CCI, MFI, ATR, OBV
- **Moving Averages**: SMA, EMA with multiple timeframes
- **Trend Analysis**: Short, medium, and long-term trend identification
- **Volume Analysis**: Volume ratios and On-Balance Volume

### 📈 Fundamental Analysis
- **Financial Metrics**: P/E, P/B, P/S ratios, ROE, ROA, Debt/Equity
- **Growth Analysis**: Revenue and earnings growth tracking
- **Profitability**: Profit margins, operating margins analysis
- **Financial Health**: Current ratio, quick ratio, debt analysis

### 📰 News Analysis
- **Multi-Source News**: Yahoo Finance, Economic Times, Money Control
- **Sentiment Analysis**: TextBlob-powered sentiment scoring
- **Stock Extraction**: Automatic stock symbol identification from news
- **Groq AI News**: AI-powered news analysis with sentiment scores

### 👀 Watchlist Management
- **Smart Watchlist**: Add stocks from recommendations
- **Performance Tracking**: Real-time performance monitoring
- **Learning Analysis**: AI-powered learning from watchlist performance
- **Price Updates**: Automatic price updates

### 🎯 Recommendations
- **AI-Generated**: Multi-factor AI recommendations
- **Confidence Scoring**: Confidence levels for each recommendation
- **Target Prices**: AI-calculated target prices and stop losses
- **Detailed Reasoning**: Comprehensive analysis explanations

## Installation

1. **Clone or Download** the application files
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up API Keys** (Optional but Recommended):
   
   ### Option A: Using the Web Interface (Easiest)
   - Run the application first: `streamlit run app.py`
   - Go to the sidebar and enter your API keys in the "🔑 API Configuration" section
   - Click "💾 Save" to permanently save your API keys
   - Keys are automatically loaded on next startup
   - Use "🗑️ Delete" to remove saved keys
   
   ### Option B: Using Environment Variables
   ```bash
   # Windows (Command Prompt)
   set GROQ_API_KEY=your_groq_api_key
   set GEMINI_API_KEY=your_gemini_api_key
   
   # Windows (PowerShell)
   $env:GROQ_API_KEY="your_groq_api_key"
   $env:GEMINI_API_KEY="your_gemini_api_key"
   
   # Linux/Mac
   export GROQ_API_KEY="your_groq_api_key"
   export GEMINI_API_KEY="your_gemini_api_key"
   ```
   
   ### Option C: Using Configuration File
   - Copy `config_template.py` to `config.py`
   - Edit `config.py` and add your actual API keys
   - The application will automatically load these keys

4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## Getting API Keys

### 🔑 Groq API Key (Recommended)
1. Go to [Groq Console](https://console.groq.com/)
2. Sign up or log in to your account
3. Navigate to "API Keys" section
4. Create a new API key
5. Copy the key (starts with `gsk_`)
6. **Benefits**: 
   - Real-time AI-powered news analysis
   - Advanced sentiment analysis
   - Stock-specific insights
   - High-speed inference
   - **Smart Model Fallback**: Automatically tries multiple models if one is unavailable
   - **Model Options**: Uses llama3-70b-8192, mixtral-8x7b-32768, and other available models

### 🔑 Gemini API Key (Optional)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key (starts with `AIza`)
5. **Benefits**:
   - Comprehensive stock analysis
   - Learning system integration
   - Advanced reasoning capabilities

## Usage

### 1. News Analysis Tab
- Click "📰 Fetch Latest News" to get recent market news
- Click "🔍 Analyze Sentiment" to analyze news sentiment
- View detailed news articles with sentiment scores

### 2. Groq News Analysis Tab
- Click "🔍 Fetch Groq News Analysis" for AI-powered news analysis
- **Real-time AI Analysis**: Get live sentiment analysis of Indian stock news
- **Sentiment Scores**: View detailed sentiment scores (-1.0 to 1.0)
- **Impact Levels**: See HIGH/MEDIUM/LOW impact assessments
- **Key Factors**: Identify the most important factors affecting each stock
- **Price Impact**: Get UPWARD/DOWNWARD/NEUTRAL price predictions
- **Confidence Levels**: See AI confidence in each analysis
- **Stock Coverage**: Focus on major NSE-listed stocks across all sectors

### 3. AI Recommendations Tab
- Click "🔍 Generate AI Recommendations" to analyze market
- Filter recommendations by action (BUY/SELL/HOLD)
- Set minimum confidence levels
- Sort by confidence, symbol, or price
- View detailed analysis for each recommendation

### 4. Watchlist Tab
- Add stocks from recommendations to watchlist
- Click "🧠 Learn from Performance" for AI learning analysis
- Update prices and track performance
- Remove stocks from watchlist

### 5. Manual Analysis Tab
- Enter stock symbol for individual analysis
- Get comprehensive AI analysis
- Add analyzed stocks to watchlist

## Configuration

### API Keys (Optional)
- **Groq API**: For advanced news sentiment analysis
- **Gemini API**: For comprehensive AI analysis

### Customization
- Modify `components/` files to customize analysis logic
- Update `app.py` for UI modifications
- Adjust weights in AI engine for different analysis emphasis

## Architecture

### Components
- `ai_engine.py`: AI recommendation engine
- `technical_analyzer.py`: Technical analysis calculations
- `fundamental_analyzer.py`: Fundamental analysis
- `news_analyzer.py`: News fetching and sentiment analysis
- `groq_analyzer.py`: Groq AI integration
- `gemini_analyzer.py`: Gemini AI integration
- `watchlist_manager.py`: Watchlist management
- `recommendation_learning.py`: Learning system
- `firebase_integration.py`: Firebase sync (optional)

### Data Flow
1. **News Fetching** → **Sentiment Analysis** → **Stock Extraction**
2. **Technical Analysis** → **Fundamental Analysis** → **AI Analysis**
3. **Recommendation Generation** → **Watchlist Management** → **Learning**

## Features Comparison with Desktop Version

| Feature | Desktop Version | Web Version | Status |
|---------|----------------|-------------|---------|
| AI Recommendations | ✅ | ✅ | ✅ Complete |
| Technical Analysis | ✅ | ✅ | ✅ Complete |
| Fundamental Analysis | ✅ | ✅ | ✅ Complete |
| News Analysis | ✅ | ✅ | ✅ Complete |
| Groq AI Integration | ✅ | ✅ | ✅ Complete |
| Gemini AI Integration | ✅ | ✅ | ✅ Complete |
| Watchlist Management | ✅ | ✅ | ✅ Complete |
| Learning System | ✅ | ✅ | ✅ Complete |
| Manual Analysis | ✅ | ✅ | ✅ Complete |
| Real-time Updates | ✅ | ✅ | ✅ Complete |
| Caching | ✅ | ✅ | ✅ Complete |
| Firebase Sync | ✅ | ✅ | ✅ Complete |

## Deployment

### Local Development
```bash
streamlit run app.py
```

### Cloud Deployment
- **Streamlit Cloud**: Direct deployment from GitHub
- **Heroku**: Use Procfile and requirements.txt
- **AWS/GCP**: Container deployment with Docker
- **Railway**: Simple deployment with GitHub integration

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Performance

- **Real-time Analysis**: Fast technical and fundamental calculations
- **Caching**: Intelligent caching for API responses
- **Responsive UI**: Optimized for desktop and mobile
- **Scalable**: Handles multiple concurrent users

## Support

For issues or questions:
1. Check the logs in the application
2. Verify API keys are set correctly
3. Ensure all dependencies are installed
4. Check network connectivity for news fetching

## License

This application is for educational and research purposes. Please ensure compliance with financial regulations in your jurisdiction.
