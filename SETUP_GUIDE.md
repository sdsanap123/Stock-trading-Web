# 🚀 Quick Setup Guide - Enhanced Swing Trading App

## ⚡ Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
streamlit run app.py
```

### 3. Open in Browser
Go to: `http://localhost:8501`

### 4. Add Your Groq API Key (Optional but Recommended)
1. In the sidebar, find "🔑 API Configuration"
2. Enter your Groq API key in the "Groq API Key" field
3. Click outside the field to save
4. You'll see "✅ Groq API key set!" confirmation

## 🔑 Getting Your Groq API Key

### Step 1: Sign Up
1. Go to [Groq Console](https://console.groq.com/)
2. Click "Sign Up" and create your account
3. Verify your email if required

### Step 2: Create API Key
1. Once logged in, go to "API Keys" in the sidebar
2. Click "Create API Key"
3. Give it a name (e.g., "Stock Trading App")
4. Copy the generated key (starts with `gsk_`)

### Step 3: Add to App
1. Paste the key in the web interface
2. Or set as environment variable:
   ```bash
   # Windows
   set GROQ_API_KEY=your_key_here
   
   # Linux/Mac
   export GROQ_API_KEY=your_key_here
   ```

## 🎯 What You Get with Groq AI

### Without Groq API Key:
- ✅ Basic news fetching
- ✅ Technical analysis
- ✅ Fundamental analysis
- ✅ Manual stock analysis
- ❌ AI-powered news sentiment
- ❌ Advanced stock insights

### With Groq API Key:
- ✅ Everything above PLUS:
- ✅ **Real-time AI news analysis**
- ✅ **Advanced sentiment scoring**
- ✅ **Stock-specific insights**
- ✅ **Price impact predictions**
- ✅ **Key factor identification**
- ✅ **Confidence levels**
- ✅ **Smart model fallback** (tries multiple models automatically)
- ✅ **High-performance models** (llama3-70b, mixtral-8x7b, etc.)

## 🧪 Test the Features

### 1. Test Basic Features (No API Key Needed)
- Go to "📰 News Analysis" tab
- Click "📰 Fetch Latest News"
- Go to "🎯 AI Recommendations" tab
- Click "🔍 Generate AI Recommendations"

### 2. Test Groq AI Features (API Key Required)
- Go to "🤖 Groq News Analysis" tab
- Click "🔍 Fetch Groq News Analysis"
- View AI-powered sentiment analysis
- See detailed insights and predictions

## 🛠️ Troubleshooting

### "Groq AI not initialized" Error
- Make sure you've entered your API key in the sidebar
- Check that the key starts with `gsk_`
- Verify the key is valid at [Groq Console](https://console.groq.com/)

### "No news articles found" Error
- This is normal - the app fetches real news
- Try again later or check your internet connection

### Application Won't Start
- Make sure Python is installed
- Run: `pip install -r requirements.txt`
- Check for any error messages in the terminal

## 📱 Features Overview

| Feature | No API Key | With Groq API |
|---------|------------|---------------|
| News Fetching | ✅ | ✅ |
| Technical Analysis | ✅ | ✅ |
| Fundamental Analysis | ✅ | ✅ |
| AI Recommendations | ✅ | ✅ |
| **Groq News Analysis** | ❌ | ✅ |
| **AI Sentiment Analysis** | ❌ | ✅ |
| **Stock Insights** | ❌ | ✅ |
| **Price Predictions** | ❌ | ✅ |

## 💾 API Key Management

### Saving Your API Keys
- **One-Time Setup**: Enter your API key once and save it
- **Automatic Loading**: Keys are loaded automatically on startup
- **Secure Storage**: Keys are stored locally in encrypted files
- **Easy Management**: Save, update, or delete keys anytime

### Key Management Features
- **💾 Save Button**: Permanently save your API key
- **🗑️ Delete Button**: Remove saved API key
- **Auto-Load**: Saved keys are loaded automatically
- **Visual Feedback**: Clear status messages for all actions

## 🎉 You're Ready!

The application is now ready to use. Start with basic features and add your Groq API key when you're ready for advanced AI analysis!

### Next Steps:
1. **Explore the tabs** - Each tab has different functionality
2. **Try manual analysis** - Enter a stock symbol to analyze
3. **Add stocks to watchlist** - Track your favorite stocks
4. **Get Groq API key** - For advanced AI features
5. **Save your API key** - Click "💾 Save" to remember it

Happy trading! 📈
