#!/usr/bin/env python3
"""
Enhanced Swing Trading App - Streamlit Web Version
A comprehensive stock analysis and trading application with AI-powered recommendations.
"""

import os
import re
import json
import time
import base64
import random
import logging
import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
import requests
import plotly.express as px
from streamlit_extras.metric_cards import style_metric_cards
import plotly.figure_factory as ff
from pathlib import Path
from dotenv import load_dotenv
from keep_alive import get_keep_alive_service, start_keep_alive, stop_keep_alive, get_keep_alive_status, configure_keep_alive

# Configure logging
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Configure console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# Configure file handler with UTF-8 encoding
file_handler = logging.FileHandler('trading_app.log', encoding='utf-8')
file_handler.setFormatter(log_formatter)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

import feedparser
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Import custom components
from components.data_persistence import DataPersistenceManager
from components.technical_analyzer import TechnicalAnalyzer
from components.news_analyzer import NewsAnalyzer
from components.ai_engine import AIRecommendationEngine
from components.groq_analyzer import GroqNewsAnalyzer
from components.gemini_analyzer import GeminiAIAnalyzer
from components.fundamental_analyzer import FundamentalAnalyzer
from components.expandable_ui import ExpandableUI
from utils.stock_utils import get_stock_data, find_stock_symbol, load_equity_data
from components.watchlist_manager import WatchlistManager
from components.recommendation_learning import RecommendationTracker
from components.firebase_integration import FirebaseSync
from components.cache_manager import CacheManager
from components.swing_strategy import SwingTradingStrategy
from components.email_notifications import EmailNotificationManager, AlertType, AlertPriority
from components.price_monitor import PriceMonitor
from components.notification_settings import NotificationSettingsManager, NotificationChannel
from components.data_persistence import DataPersistenceManager
from components.expandable_ui import ExpandableUI
from components.scheduled_analysis import ScheduledAnalysis
from components.swing_performance_tracker import SwingPerformanceTracker
from components.enhanced_portfolio import render_enhanced_portfolio

# Page configuration
st.set_page_config(
    page_title="Enhanced Swing Trading App",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f4e79, #2e8b57);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-card {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2e8b57;
        color: #000000;
    }
    .metric-card h3,
    .metric-card p {
        color: #000000;
    }
    
    .sentiment-positive {
        color: #28a745;
        font-weight: bold;
    }
    
    .sentiment-negative {
        color: #dc3545;
        font-weight: bold;
    }
    
    .sentiment-neutral {
        color: #ffc107;
        font-weight: bold;
    }
    
    .recommendation-buy {
        color: #28a745;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .recommendation-sell {
        color: #dc3545;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .recommendation-hold {
        color: #ffc107;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .news-card {
        background-color: #2d2d2d;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #1f4e79;
    }
    
    .groq-card {
        background-color: #2d2d2d;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #2e8b57;
    }
    
    .government-highlight {
        background-color: #3d2d2d;
        border-left: 4px solid #ffd700;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
    }
    
    /* Compact UI optimizations */
    .main-header {
        font-size: 1.8rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Compact tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.3rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 0.2rem 0.6rem;
        font-size: 0.85rem;
        min-height: 2rem;
    }
    
    /* Compact sidebar */
    .css-1d391kg {
        padding-top: 0.5rem;
    }
    
    /* Compact metrics */
    .metric-card {
        padding: 0.5rem !important;
        margin: 0.2rem 0 !important;
    }
    
    /* Compact expandable content */
    .expandable-row {
        margin: 0.1rem 0;
        padding: 0.2rem;
    }
    
    /* Reduce spacing */
    .element-container {
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class StockData:
    """Data class for stock information."""
    symbol: str
    name: str
    current_price: float
    change: float
    change_percent: float
    volume: int
    market_cap: float

class StreamlitTradingApp:
    """Main Streamlit Trading Application."""
    
    def __init__(self):
        """Initialize the application."""
        self.initialize_session_state()
        self.initialize_components()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state."""
        # First, initialize the data persistence
        if 'data_persistence' not in st.session_state:
            st.session_state.data_persistence = DataPersistenceManager()
        
        # Initialize cache manager
        if 'cache_manager' not in st.session_state:
            st.session_state.cache_manager = CacheManager()
            
        # Initialize basic session state variables
        session_vars = {
            'recommendations': [],
            'news_articles': [],
            'groq_news_data': {},
            'watchlist': [],
            'portfolio': [],
            'analysis_in_progress': False,
            'fundamental_analysis_disabled': False,
            'last_analysis_time': None,
            'show_saved_recommendations': False,
            'saved_groq_key': self.load_saved_api_key('groq'),
            'saved_gemini_key': self.load_saved_api_key('gemini'),
            'keep_alive_enabled': False,
            'keep_alive_interval': 300,  # 5 minutes default
            'keep_alive_url': '',
            'learning_available': False,
            'components_initialized': False,
            'api_keys_initialized': False,
            'scheduler_started': False
        }
        
        # Set default values if not already set
        for key, default_value in session_vars.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
        
        # Load watchlist from database if available and watchlist is empty
        if not st.session_state.watchlist:
            try:
                saved_watchlist = st.session_state.data_persistence.get_watchlist()
                if saved_watchlist:
                    st.session_state.watchlist = saved_watchlist
                    logger.info(f"Loaded {len(saved_watchlist)} items from saved watchlist")
            except Exception as e:
                logger.error(f"Error loading watchlist: {str(e)}")
        
        # Load recommendations if we don't have any in the current session
        if not st.session_state.recommendations:
            try:
                available_dates = st.session_state.data_persistence.get_available_dates()
                if available_dates:
                    latest_date = max(available_dates)
                    latest_recommendations = st.session_state.data_persistence.get_recommendations_by_date(latest_date)
                    if latest_recommendations:
                        # Convert any string values to their appropriate types
                        for rec in latest_recommendations:
                            # Ensure confidence is a number
                            if 'confidence' in rec and isinstance(rec['confidence'], str):
                                try:
                                    rec['confidence'] = float(rec['confidence'])
                                except (ValueError, TypeError):
                                    rec['confidence'] = 0.0
                        
                        # Remove duplicates based on symbol
                        unique_recommendations = {}
                        for rec in latest_recommendations:
                            symbol = rec.get('symbol')
                            if symbol:  # Only add if symbol exists
                                unique_recommendations[symbol] = rec
                        
                        st.session_state.recommendations = list(unique_recommendations.values())
                        logger.info(f"Loaded {len(st.session_state.recommendations)} unique recommendations from {latest_date}")
            except Exception as e:
                logger.error(f"Error loading recommendations: {str(e)}")
                st.session_state.recommendations = []  # Ensure we have an empty list on error
        
        if 'swing_performance_tracker' not in st.session_state:
            st.session_state.swing_performance_tracker = SwingPerformanceTracker(working_capital=100000)
        if 'swing_strategy' not in st.session_state:
            # Initialize swing strategy with adaptive parameters
            adaptive_params = st.session_state.swing_performance_tracker.get_adaptive_parameters()
            st.session_state.swing_strategy = SwingTradingStrategy(adaptive_parameters=adaptive_params)
        if 'email_notifications' not in st.session_state:
            st.session_state.email_notifications = EmailNotificationManager()
        if 'price_monitor' not in st.session_state:
            st.session_state.price_monitor = PriceMonitor(self._notification_callback)
        if 'notification_settings' not in st.session_state:
            st.session_state.notification_settings = NotificationSettingsManager()
        if 'scheduled_analysis' not in st.session_state:
            st.session_state.scheduled_analysis = ScheduledAnalysis(self.analyze_market)
        
    def initialize_components(self):
        """Initialize all analysis components."""
        try:
            # Initialize or reuse AI components from session state
            if 'ai_engine' not in st.session_state:
                st.session_state.ai_engine = AIRecommendationEngine()
            self.ai_engine = st.session_state.ai_engine

            if 'technical_analyzer' not in st.session_state:
                st.session_state.technical_analyzer = TechnicalAnalyzer()
            self.technical_analyzer = st.session_state.technical_analyzer

            if 'news_analyzer' not in st.session_state:
                st.session_state.news_analyzer = NewsAnalyzer()
            self.news_analyzer = st.session_state.news_analyzer

            if 'groq_analyzer' not in st.session_state:
                st.session_state.groq_analyzer = GroqNewsAnalyzer()
            self.groq_analyzer = st.session_state.groq_analyzer

            if 'gemini_analyzer' not in st.session_state:
                st.session_state.gemini_analyzer = GeminiAIAnalyzer()
            self.gemini_analyzer = st.session_state.gemini_analyzer

            if 'fundamental_analyzer' not in st.session_state:
                st.session_state.fundamental_analyzer = FundamentalAnalyzer()
            self.fundamental_analyzer = st.session_state.fundamental_analyzer

            # Initialize or reuse Firebase integration
            if 'firebase_sync' not in st.session_state:
                try:
                    st.session_state.firebase_sync = FirebaseSync('firebase_config.json')
                    st.session_state.firebase_available = st.session_state.firebase_sync.initialized
                    
                    # Set user ID for Firebase if not already set
                    if st.session_state.firebase_sync.initialized and 'user_id' not in st.session_state:
                        # Generate a unique user ID
                        import hashlib
                        import time
                        user_string = f"watchlist_user_{int(time.time())}_{hash(str(st.session_state))}"
                        user_id = hashlib.md5(user_string.encode()).hexdigest()[:16]
                        st.session_state.user_id = user_id
                        st.session_state.firebase_sync.set_user_id(user_id)
                        logger.info(f"Generated Firebase user ID: {user_id}")
                        
                except:
                    st.session_state.firebase_sync = None
                    st.session_state.firebase_available = False
            self.firebase_sync = st.session_state.firebase_sync

            if 'watchlist_manager' not in st.session_state:
                st.session_state.watchlist_manager = WatchlistManager(self.firebase_sync)
            self.watchlist_manager = st.session_state.watchlist_manager

            # Initialize or reuse learning system
            if 'recommendation_tracker' not in st.session_state:
                try:
                    st.session_state.recommendation_tracker = RecommendationTracker()
                    st.session_state.learning_available = True
                except:
                    st.session_state.recommendation_tracker = None
                    st.session_state.learning_available = False
            self.recommendation_tracker = st.session_state.recommendation_tracker

            # Initialize API keys in analyzers (only once per session)
            if not st.session_state.get('api_keys_initialized', False):
                self._initialize_api_keys()
                st.session_state.api_keys_initialized = True
            
            # Start scheduled analysis only once per session
            self.scheduled_analysis = st.session_state.get('scheduled_analysis')
            if self.scheduled_analysis and not st.session_state.get('scheduler_started', False):
                self.scheduled_analysis.start_scheduler()
                st.session_state.scheduler_started = True
                logger.info("Scheduled analysis started")
            
            # Log overall initialization only on first successful setup
            if not st.session_state.get('components_initialized', False):
                logger.info("All components initialized successfully")
                st.session_state.components_initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing components: {str(e)}")
            st.error(f"Error initializing components: {str(e)}")


    
    def _initialize_api_keys(self):
        """Initialize API keys in analyzers from saved settings."""
        try:
            # Load and set Groq API key
            groq_key = self.load_saved_api_key('groq')
            if groq_key:
                self.groq_analyzer.api_key = groq_key
                self.groq_analyzer.initialized = True
                logger.info("Groq API key loaded and initialized")
            else:
                self.groq_analyzer.initialized = False
                logger.warning("Groq API key not found")
            
            # Load and set Gemini API key
            gemini_key = self.load_saved_api_key('gemini')
            if gemini_key:
                self.gemini_analyzer.api_key = gemini_key
                self.gemini_analyzer.initialized = True
                logger.info("Gemini API key loaded and initialized")
            else:
                self.gemini_analyzer.initialized = False
                logger.warning("Gemini API key not found")
                
        except Exception as e:
            logger.error(f"Error initializing API keys: {str(e)}")
    
    def _auto_save_recommendations(self):
        """Automatically save recommendations."""
        try:
            if st.session_state.get('recommendations'):
                data_persistence = st.session_state.data_persistence
                data_persistence.save_recommendations(st.session_state.recommendations)
                logger.info(f"Auto-saved {len(st.session_state.recommendations)} recommendations")
        except Exception as e:
            logger.error(f"Error auto-saving recommendations: {str(e)}")
    
    def _auto_save_buy_recommendations(self):
        """Automatically save only BUY recommendations date-wise."""
        try:
            if st.session_state.get('recommendations'):
                data_persistence = st.session_state.data_persistence
                current_date = datetime.now().strftime("%Y-%m-%d")
                
                # Save BUY recommendations specifically
                success = data_persistence.save_buy_recommendations(st.session_state.recommendations, current_date)
                
                if success:
                    # Count BUY recommendations
                    buy_count = 0
                    for rec in st.session_state.recommendations:
                        recommendation = rec.get('recommendation', '').upper()
                        action = rec.get('action', '').upper()
                        if recommendation == 'BUY' or action == 'BUY':
                            buy_count += 1
                    
                    logger.info(f"Auto-saved {buy_count} BUY recommendations for {current_date}")
                    return True
                else:
                    logger.error("Failed to save BUY recommendations")
                    return False
            else:
                logger.info("No recommendations to save")
                return True
        except Exception as e:
            logger.error(f"Error auto-saving BUY recommendations: {str(e)}")
            return False
    
    def _auto_save_buy_recommendations_for_manual(self, recommendations: List[Dict]):
        """Save BUY recommendations from manual analysis."""
        try:
            if recommendations:
                data_persistence = st.session_state.data_persistence
                current_date = datetime.now().strftime("%Y-%m-%d")
                
                # Save BUY recommendations specifically
                success = data_persistence.save_buy_recommendations(recommendations, current_date)
                
                if success:
                    logger.info(f"Auto-saved {len(recommendations)} BUY recommendation(s) from manual analysis for {current_date}")
                    return True
                else:
                    logger.error("Failed to save manual BUY recommendations")
                    return False
            else:
                logger.info("No manual recommendations to save")
                return True
        except Exception as e:
            logger.error(f"Error auto-saving manual BUY recommendations: {str(e)}")
            return False
    
    def _auto_save_watchlist(self):
        """Automatically save watchlist."""
        try:
            # Always persist the current watchlist (including empty) so
            # clears and deletions are saved across sessions
            if 'watchlist' in st.session_state:
                data_persistence = st.session_state.data_persistence
                data_persistence.save_watchlist(st.session_state.watchlist)
                logger.info(f"Auto-saved {len(st.session_state.watchlist)} watchlist items")
        except Exception as e:
            logger.error(f"Error auto-saving watchlist: {str(e)}")
    
    def _auto_save_swing_strategies(self):
        """Automatically save swing strategies."""
        try:
            if st.session_state.get('recommendations'):
                swing_strategies = []
                for rec in st.session_state.recommendations:
                    swing_plan = rec.get('swing_plan', {})
                    if swing_plan:
                        swing_strategies.append(swing_plan)
                
                if swing_strategies:
                    data_persistence = st.session_state.data_persistence
                    data_persistence.save_swing_strategies(swing_strategies)
                    logger.info(f"Auto-saved {len(swing_strategies)} swing strategies")
        except Exception as e:
            logger.error(f"Error auto-saving swing strategies: {str(e)}")
    
    def _auto_save_news(self):
        """Automatically save news articles."""
        try:
            if st.session_state.get('news_articles'):
                data_persistence = st.session_state.data_persistence
                news_data = []
                for article in st.session_state.news_articles:
                    news_data.append({
                        'symbol': 'NEWS',
                        'company_name': article.get('title', 'News Article'),
                        'current_price': 0,
                        'recommendation': 'INFO',
                        'confidence': 0,
                        'target_price': 0,
                        'stop_loss': 0,
                        'reasoning': article.get('description', ''),
                        'technical_data': {},
                        'fundamental_data': {},
                        'groq_analysis': {},
                        'gemini_analysis': {},
                        'swing_plan': {},
                        'swing_validation': {},
                        'news_article': article
                    })
                data_persistence.save_recommendations(news_data)
                logger.info(f"Auto-saved {len(news_data)} news articles")
        except Exception as e:
            logger.error(f"Error auto-saving news: {str(e)}")
    
    def load_saved_api_key(self, key_type: str) -> str:
        """Load saved API key from session state or environment variables (Replit Secrets)."""
        try:
            # First check session state (for current session)
            if key_type == 'groq':
                session_key = st.session_state.get('saved_groq_key', '')
                if session_key:
                    return session_key
            elif key_type == 'gemini':
                session_key = st.session_state.get('saved_gemini_key', '')
                if session_key:
                    return session_key
            
            # Check environment variables (Replit Secrets)
            if key_type == 'groq':
                env_key = os.getenv('GROQ_API_KEY', '')
                if env_key:
                    return env_key
            elif key_type == 'gemini':
                env_key = os.getenv('GEMINI_API_KEY', '')
                if env_key:
                    return env_key
            
            # Try Streamlit secrets (for deployment)
            try:
                if key_type == 'groq':
                    return st.secrets.get('GROQ_API_KEY', '')
                elif key_type == 'gemini':
                    return st.secrets.get('GEMINI_API_KEY', '')
            except:
                pass
                
        except Exception as e:
            logger.warning(f"Could not load saved {key_type} API key: {str(e)}")
        return ""
    
    def save_api_key(self, key_type: str, api_key: str) -> bool:
        """Save API key to session state only. For permanent storage, use Replit Secrets."""
        try:
            # Save to session state for current session
            if key_type == 'groq':
                st.session_state.saved_groq_key = api_key
            elif key_type == 'gemini':
                st.session_state.saved_gemini_key = api_key
            
            logger.info(f"Saved {key_type} API key to session state")
            return True
        except Exception as e:
            logger.error(f"Could not save {key_type} API key: {str(e)}")
            return False
    
    def delete_saved_api_key(self, key_type: str) -> bool:
        """Clear saved API key from session state."""
        try:
            # Clear from session state
            if key_type == 'groq':
                st.session_state.saved_groq_key = ""
            elif key_type == 'gemini':
                st.session_state.saved_gemini_key = ""
            
            logger.info(f"Cleared {key_type} API key from session state")
            return True
        except Exception as e:
            logger.error(f"Could not clear {key_type} API key: {str(e)}")
            return False
    
    def _notification_callback(self, alert_type: str, stock_data: Dict, additional_data: Dict = None):
        """Callback function for price monitor alerts."""
        try:
            # Convert alert type string to AlertType enum
            alert_type_mapping = {
                'target_hit': AlertType.TARGET_HIT,
                'stop_loss_hit': AlertType.STOP_LOSS_HIT,
                'significant_movement': AlertType.SIGNIFICANT_MOVEMENT,
                'daily_summary': AlertType.DAILY_SUMMARY,
                'risk_alert': AlertType.RISK_ALERT,
                'swing_plan_update': AlertType.SWING_PLAN_UPDATE
            }
            
            alert_type_enum = alert_type_mapping.get(alert_type, AlertType.SIGNIFICANT_MOVEMENT)
            
            # Determine priority based on alert type
            priority_mapping = {
                AlertType.STOP_LOSS_HIT: AlertPriority.CRITICAL,
                AlertType.RISK_ALERT: AlertPriority.CRITICAL,
                AlertType.TARGET_HIT: AlertPriority.HIGH,
                AlertType.SIGNIFICANT_MOVEMENT: AlertPriority.MEDIUM,
                AlertType.SWING_PLAN_UPDATE: AlertPriority.MEDIUM,
                AlertType.DAILY_SUMMARY: AlertPriority.LOW
            }
            
            priority = priority_mapping.get(alert_type_enum, AlertPriority.MEDIUM)
            
            # Send email notification
            email_manager = st.session_state.email_notifications
            success = email_manager.send_alert(alert_type_enum, stock_data, additional_data, priority)
            
            if success:
                logger.info(f"Notification sent successfully: {alert_type} for {stock_data.get('symbol')}")
            else:
                logger.warning(f"Failed to send notification: {alert_type} for {stock_data.get('symbol')}")
                
        except Exception as e:
            logger.error(f"Error in notification callback: {str(e)}")
    
    def run(self):
        """Run the main application."""
        # Header
        st.markdown('<h1 class="main-header">🚀 Enhanced Swing Trading App - AI Powered</h1>', unsafe_allow_html=True)
        
        # Sidebar
        self.create_sidebar()
        
        # Main content - Compact tab layout
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "📰 News", 
            "🤖 Groq", 
            "🎯 BUY", 
            "📈 Swing", 
            "👀 Watch", 
            "🔍 Manual",
            "📊 Portfolio",
            "🔔 Alerts"
        ])
        
        with tab1:
            self.news_analysis_tab()
        
        with tab2:
            self.groq_news_analysis_tab()
        
        with tab3:
            self.recommendations_tab()
        
        with tab4:
            self.swing_trading_tab()
        
        with tab5:
            self.watchlist_tab()
        
        with tab6:
            self.manual_analysis_tab()
        
        with tab7:
            self.portfolio_tab()
        
        with tab8:
            self.notifications_tab()

    def portfolio_tab(self):
        """Portfolio tab - show enhanced portfolio UI."""
        render_enhanced_portfolio()

    def notifications_tab(self):
        """Alert tab for triggering email/SMS notifications when swing plans hit targets."""
        st.header("🔔 Alerts & Notifications")
        st.info("Choose a saved swing plan below and trigger alerts when it hits target or stop loss.")

        # Load all saved swing strategies (date-wise dict) and flatten into a list
        all_strategies_by_date = st.session_state.data_persistence.get_all_swing_strategies()
        saved_strategies: List[Dict] = []

        if all_strategies_by_date:
            for date_str, strategies in all_strategies_by_date.items():
                if not isinstance(strategies, list):
                    continue
                for strategy in strategies:
                    if isinstance(strategy, dict):
                        strategy.setdefault('saved_date', date_str)
                        saved_strategies.append(strategy)

        if not saved_strategies:
            st.warning("No saved swing strategies yet. Generate at least one recommendation to save a plan.")
            return

        summary = st.multiselect(
            "Select strategies to monitor",
            [f"{s.get('symbol', 'UNKNOWN')} - {s.get('strategy_name', 'Swing Plan')}" for s in saved_strategies],
            default=[]
        )

        if not summary:
            st.markdown("*Select one or more strategies to enable alert actions.*")
            return

        selected_plan = saved_strategies[0]
        if summary:
            index = 0
            for i, s in enumerate(saved_strategies):
                label = f"{s.get('symbol','UNKNOWN')} - {s.get('strategy_name','Swing Plan')}"
                if label == summary[0]:
                    index = i
                    break
            selected_plan = saved_strategies[index]

        st.write(f"**Primary Strategy:** {selected_plan.get('symbol', 'UNKNOWN')} - {selected_plan.get('strategy_name','Swing Plan')}")
        st.write(f"• Entry: ₹{selected_plan.get('entry_price', 0):.2f}")
        st.write(f"• Stop Loss: ₹{selected_plan.get('stop_loss', 0):.2f}")
        st.write(f"• Target: ₹{selected_plan.get('take_profit', 0):.2f}")

        alert_type = st.radio(
            "Alert type",
            [AlertType.TARGET_HIT, AlertType.STOP_LOSS_HIT],
            format_func=lambda a: a.name.replace("_", " ").title()
        )

        notify_email = st.checkbox("Send Email", value=True)
        notify_sms = st.checkbox("Send SMS", value=False)
        additional_note = st.text_area("Optional note", value="", max_chars=200)

        if st.button("🚨 Trigger Alert"):
            stock_data = {
                'symbol': selected_plan.get('symbol', 'UNKNOWN'),
                'company_name': selected_plan.get('company_name', ''),
                'current_price': selected_plan.get('current_price', 0),
                'entry_price': selected_plan.get('entry_price', 0),
                'target_price': selected_plan.get('take_profit', 0),
                'stop_loss': selected_plan.get('stop_loss', 0),
                'investment_amount': selected_plan.get('investment_amount', 0),
                'position_size': selected_plan.get('position_size', 0),
                'confidence': selected_plan.get('confidence', 0),
                'reasoning': additional_note
            }

            sent = False
            if notify_email:
                sent = st.session_state.email_notifications.send_alert(
                    alert_type,
                    stock_data,
                    {'plan_details': selected_plan.get('strategy_rules', [])},
                    priority=AlertPriority.HIGH
                )

            if notify_sms:
                sent = self.send_sms_alert(stock_data, alert_type, additional_note) or sent

            if sent:
                st.success("Alert triggered successfully.")
            else:
                st.error("Failed to send alert. Check settings & enabled channels.")

    def send_sms_alert(self, stock_data: Dict, alert_type: AlertType, note: str = "") -> bool:
        """Simulated SMS alert using logging."""
        symbol = stock_data.get('symbol', 'UNKNOWN')
        current_price = stock_data.get('current_price', 0)
        message = (
            f"Alert: {symbol} {alert_type.name.replace('_',' ').title()} at ₹{current_price:.2f}. {note}"
        )
        logger.info(f"SMS alert sent: {message}")
        st.info("SMS alert queued (simulation).")
        return True
    
    def manual_analysis_tab(self):
        """Manual tab where users can lookup by name/symbol and run analysis."""
        st.header("🔍 Manual Stock Search & Analysis")
        st.caption("Enter a symbol or company name below to run the same AI + news analysis that drives the BUY tab.")

        search_query = st.text_input(
            "Stock symbol or company name",
            value=st.session_state.get('manual_search_query', ''),
            help="You can type NSE symbols (e.g. RELIANCE) or company names (e.g. Reliance Industries)",
            key="manual_search_input"
        ).strip()

        matches = []
        selected_symbol = None
        if search_query:
            st.session_state.manual_search_query = search_query
            equity_df = load_equity_data()
            if not equity_df.empty:
                mask = (
                    equity_df['SYMBOL'].str.contains(search_query, case=False, na=False) |
                    equity_df['NAME OF COMPANY'].str.contains(search_query, case=False, na=False)
                )
                matches = equity_df[mask].head(10)
                if not matches.empty:
                    display_rows = matches[['SYMBOL', 'NAME OF COMPANY']].copy()
                    display_rows['INFO'] = display_rows['SYMBOL'] + ' — ' + display_rows['NAME OF COMPANY']
                    st.dataframe(display_rows[['INFO']], width='stretch')

                    options = display_rows['INFO'].tolist()
                    selected_option = st.selectbox("Pick a match (optional)", options, key="manual_match_select")
                    if selected_option:
                        selected_symbol = selected_option.split(' — ')[0]
                else:
                    st.info("No exact matches found in EQUITY_L.csv. You can still try analyzing the raw input symbol/name.")
            else:
                st.warning("Equity database could not be loaded, fallback to direct symbol entry.")

        if st.button("📊 Search & Analyze", key="manual_search_btn"):
            target_symbol = selected_symbol or search_query
            if not target_symbol:
                st.error("Please enter a symbol or company name first.")
            else:
                self.analyze_manual_stock(target_symbol)

        if st.session_state.get('manual_analysis_result'):
            st.markdown("---")
            self.display_manual_analysis_result()
    
    def create_sidebar(self):
        """Create the sidebar with controls."""
        # Compact sidebar - only show essential controls
        with st.sidebar:
            # Always show essential controls
            st.markdown("### 🚀 Quick Actions")
            
            # Market Analysis Button
            if st.button("📊 Analyze Market", key="analyze_market_btn", type="primary"):
                if not st.session_state.get('analysis_in_progress', False):
                    st.session_state.analysis_in_progress = True
                    self.analyze_market()
            
            # Show analysis status
            if st.session_state.get('analysis_in_progress', False):
                st.info("🔄 Analysis in progress...")
            
            # Show last analysis time
            if st.session_state.get('last_analysis_time'):
                st.caption(f"Last: {st.session_state.last_analysis_time[11:16]}")
            
            # Always show API Keys section
            st.markdown("---")
            st.markdown("### 🔑 API Keys")
            
            # Groq API Key
            groq_key = st.text_input(
                "Groq API Key",
                value=st.session_state.saved_groq_key,
                type="password",
                help="Enter your Groq API key",
                placeholder="gsk_..."
            )
            
            # Groq API Key Actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save", key="save_groq"):
                    if groq_key and groq_key != st.session_state.saved_groq_key:
                        if self.save_api_key('groq', groq_key):
                            st.session_state.saved_groq_key = groq_key
                            # Reinitialize Groq analyzer with new key
                            self.groq_analyzer.api_key = groq_key
                            self.groq_analyzer.initialized = True
                            st.success("✅ Saved and initialized!")
                        else:
                            st.error("❌ Failed to save")
                    else:
                        st.info("ℹ️ No changes to save")
            
            with col2:
                if st.button("🗑️ Delete", key="delete_groq"):
                    if self.delete_saved_api_key('groq'):
                        st.session_state.saved_groq_key = ""
                        # Deinitialize Groq analyzer
                        self.groq_analyzer.api_key = ""
                        self.groq_analyzer.initialized = False
                        st.success("✅ Groq API key deleted!")
                    else:
                        st.error("❌ Failed to delete Groq API key")
            
            # Gemini API Key
            gemini_key = st.text_input(
                "Gemini API Key",
                value=st.session_state.saved_gemini_key,
                type="password",
                help="Enter your Gemini API key",
                placeholder="AIza..."
            )
            
            # Gemini API Key Actions
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save", key="save_gemini"):
                    if gemini_key and gemini_key != st.session_state.saved_gemini_key:
                        if self.save_api_key('gemini', gemini_key):
                            st.session_state.saved_gemini_key = gemini_key
                            # Reinitialize Gemini analyzer with new key
                            self.gemini_analyzer.api_key = gemini_key
                            self.gemini_analyzer.initialized = True
                            st.success("✅ Saved and initialized!")
                        else:
                            st.error("❌ Failed to save")
                    else:
                        st.info("ℹ️ No changes to save")
            
            with col2:
                if st.button("🗑️ Delete", key="delete_gemini"):
                    if self.delete_saved_api_key('gemini'):
                        st.session_state.saved_gemini_key = ""
                        # Deinitialize Gemini analyzer
                        self.gemini_analyzer.api_key = ""
                        self.gemini_analyzer.initialized = False
                        st.success("✅ Gemini API key deleted!")
                    else:
                        st.error("❌ Failed to delete Gemini API key")
            
            # Update analyzers
            if groq_key:
                self.groq_analyzer.api_key = groq_key
                self.groq_analyzer.initialized = True
                if groq_key == st.session_state.saved_groq_key:
                    st.success("✅ Groq API key loaded from saved settings!")
                else:
                    st.success("✅ Groq API key set! (Click Save to remember)")
            else:
                if hasattr(self, 'groq_analyzer'):
                    self.groq_analyzer.initialized = False
                    st.info("ℹ️ Enter Groq API key to enable AI analysis")
            
            if gemini_key:
                self.gemini_analyzer.api_key = gemini_key
                self.gemini_analyzer.initialized = True
                if gemini_key == st.session_state.saved_gemini_key:
                    st.success("✅ Gemini API key loaded from saved settings!")
                else:
                    st.success("✅ Gemini API key set! (Click Save to remember)")
            else:
                if hasattr(self, 'gemini_analyzer'):
                    self.gemini_analyzer.initialized = False
                    st.info("ℹ️ Enter Gemini API key to enable comprehensive AI analysis")
        
        st.sidebar.markdown("---")
        
        # Market Analysis Section
        st.sidebar.header("📊 Market Analysis")
        
        if st.sidebar.button("🔍 Analyze Market", type="primary", width='stretch'):
            self.analyze_market()
        
        if st.sidebar.button("📰 Fetch News", width='stretch'):
            self.fetch_news()
        
        if st.sidebar.button("🤖 Fetch Groq Analysis", width='stretch'):
            self.fetch_groq_news_analysis()
        
        # Status
        st.sidebar.header("📈 Status")
        if st.session_state.last_analysis_time:
            st.sidebar.success(f"Last Analysis: {st.session_state.last_analysis_time}")
        else:
            st.sidebar.info("No analysis performed yet")
        
        # Keep Alive Settings
        st.sidebar.header("🔌 Keep Alive")
        with st.sidebar.expander("Settings"):
            # Toggle for enabling/disabling keep-alive
            keep_alive_enabled = st.toggle(
                "Enable Keep-Alive",
                value=st.session_state.keep_alive_enabled,
                key="keep_alive_toggle"
            )
            
            # Get the current app URL from secrets or use default
            default_url = st.secrets.get("STREAMLIT_APP_URL", "https://your-app-name.streamlit.app")
            
            # Input for app URL
            keep_alive_url = st.text_input(
                "App URL",
                value=st.session_state.keep_alive_url or default_url,
                key="keep_alive_url_input"
            )
            
            # Input for ping interval (in minutes)
            keep_alive_interval = st.number_input(
                "Ping Interval (minutes)",
                min_value=1,
                max_value=60,
                value=st.session_state.keep_alive_interval // 60,  # Convert seconds to minutes for display
                key="keep_alive_interval_input"
            )
            
            # Save settings button
            if st.button("💾 Save Keep-Alive Settings"):
                st.session_state.keep_alive_enabled = keep_alive_enabled
                st.session_state.keep_alive_url = keep_alive_url
                st.session_state.keep_alive_interval = keep_alive_interval * 60  # Convert to seconds
                
                # Configure the keep-alive service
                configure_keep_alive(
                    url=keep_alive_url,
                    interval=keep_alive_interval * 60
                )
                
                # Start or stop the service based on the toggle
                if keep_alive_enabled:
                    if start_keep_alive(ping_interval=keep_alive_interval * 60):
                        st.success("✅ Keep-alive service started!")
                    else:
                        st.error("❌ Failed to start keep-alive service")
                else:
                    if stop_keep_alive():
                        st.success("✅ Keep-alive service stopped")
                    else:
                        st.info("ℹ️ Keep-alive service is not running")
            
            # Show current status
            status = get_keep_alive_status()
            st.caption("Keep-Alive Status:")
            if status['is_running']:
                st.success(f"🟢 Active - Pinging every {status['ping_interval']//60} minutes")
                if status['last_ping_time']:
                    st.caption(f"Last ping: {status['last_ping_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.caption(f"Success rate: {status['success_rate']:.1f}% ({status['ping_count']} pings)")
            else:
                st.info("⚪ Inactive")
        
        # Quick Stats
        st.sidebar.header("📊 Quick Stats")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Recommendations", len(st.session_state.recommendations))
        with col2:
            st.metric("Watchlist Items", len(st.session_state.watchlist))
        
        # API Status
        st.sidebar.header("📊 API Status")
        
        # Groq AI Status
        if hasattr(self, 'groq_analyzer') and self.groq_analyzer.initialized:
            st.sidebar.success("🤖 Groq AI: Active")
        else:
            st.sidebar.warning("🤖 Groq AI: Inactive")
            st.sidebar.caption("Add API key in Configuration section")
        
        # Gemini AI Status
        if hasattr(self, 'gemini_analyzer') and self.gemini_analyzer.initialized:
            st.sidebar.success("🧠 Gemini AI: Active")
        else:
            st.sidebar.warning("🧠 Gemini AI: Inactive")
            st.sidebar.caption("Add API key in Configuration section")
        
        # Learning System Status
        if st.session_state.learning_available:
            st.sidebar.success("📚 Learning System: Active")
        else:
            st.sidebar.warning("📚 Learning System: Unavailable")
        
        # Firebase Status
        if st.session_state.firebase_available:
            st.sidebar.success("☁️ Firebase Sync: Active")
        else:
            st.sidebar.warning("☁️ Firebase Sync: Unavailable")
        
        # Cache Statistics
        st.sidebar.header("💾 Cache Statistics")
        cache_manager = st.session_state.cache_manager
        cache_stats = cache_manager.get_cache_stats()
        
        if cache_stats:
            st.sidebar.metric("Cached Articles", cache_stats.get('articles_cache_size', 0))
            st.sidebar.metric("Cached Stocks", cache_stats.get('stocks_cache_size', 0))
            st.sidebar.metric("Cached Analysis", cache_stats.get('analysis_cache_size', 0))
            
            st.sidebar.caption("Cache Duration: 7 days")
            
            if st.sidebar.button("🗑️ Clear Cache"):
                cache_manager.clear_cache('all')
                st.sidebar.success("Cache cleared!")
                st.rerun()
    
    def news_analysis_tab(self):
        """News Analysis tab with company database integration."""
        st.header("📰 News Analysis & Company Lookup")
        
        # Create tabs for different functionalities
        tab1, tab2 = st.tabs(["📰 News Analysis", "🏢 Company Lookup"])
        
        with tab1:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                if st.button("📰 Fetch Latest News", type="primary", key="fetch_news_btn"):
                    self.fetch_news()
            
            with col2:
                if st.button("🔍 Analyze Sentiment", key="analyze_sentiment_btn"):
                    self.analyze_sentiment()
            
            # News is automatically saved when fetched
            
            # Display news articles in rows
            if st.session_state.news_articles:
                st.subheader(f"📰 Latest News ({len(st.session_state.news_articles)} articles)")
                
                # Header row
                col1, col2, col3, col4, col5 = st.columns([3, 1.5, 1, 1, 0.8])
                with col1:
                    st.markdown("**Headline**")
                with col2:
                    st.markdown("**Source**")
                with col3:
                    st.markdown("**Published**")
                with col4:
                    st.markdown("**Sentiment**")
                with col5:
                    st.markdown("**Details**")
                
                st.markdown("---")
                
                # Display each article in a row
                for i, article in enumerate(st.session_state.news_articles[:10]):
                    ExpandableUI.display_news_row(article, i)
            else:
                st.info("No news articles available. Click 'Fetch Latest News' to get started.")
        
        with tab2:
            st.subheader("🔍 Company Lookup")
            
            # Search for companies
            search_term = st.text_input("Search by company name or symbol")
            
            if search_term:
                # Search for companies matching the search term
                results = self.news_analyzer.search_companies(search_term, limit=10)
                
                if results:
                    st.success(f"Found {len(results)} matching companies")
                    
                    # Display results in a table
                    for company in results:
                        with st.expander(f"{company['symbol']} - {company['name']}"):
                            col1, col2 = st.columns([1, 3])
                            with col1:
                                st.metric("Symbol", company['symbol'])
                                st.metric("Industry", company.get('industry', 'N/A'))
                            with col2:
                                st.metric("Company Name", company['name'])
                                st.metric("Sector", company.get('sector', 'N/A'))
                else:
                    st.warning("No companies found matching your search")
            
            # Stock symbol validation
            st.subheader("🔎 Validate Stock Symbol")
            symbol_to_check = st.text_input("Enter a stock symbol to validate")
            
            if symbol_to_check:
                is_valid = self.news_analyzer.is_valid_stock_symbol(symbol_to_check)
                if is_valid:
                    st.success(f"✅ {symbol_to_check} is a valid stock symbol")
                    
                    # Show company details if valid
                    company_info = self.news_analyzer.get_company_info(symbol_to_check)
                    if company_info:
                        st.json(company_info)
                else:
                    st.error(f"❌ {symbol_to_check} is not a valid stock symbol")
    
    def groq_news_analysis_tab(self):
        """Groq News Analysis tab."""
        st.header("🤖 Groq AI News Analysis with Sentiment")
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            if st.button("🔍 Fetch Groq News Analysis", type="primary", key="fetch_groq_analysis_btn"):
                self.fetch_groq_news_analysis()
        
        with col2:
            if st.button("📰 Fetch Indian News", key="fetch_indian_news_btn"):
                self.fetch_news()
        
        with col3:
            if st.button("🔄 Refresh Display", key="refresh_display_btn"):
                st.rerun()
        
        with col4:
            if st.button("📡 Test RSS Feeds", key="test_rss_feeds_btn"):
                self.test_rss_feeds()
        
        # Display Groq news analysis
        if st.session_state.groq_news_data:
            st.subheader(f"🤖 Groq AI Analysis ({len(st.session_state.groq_news_data)} stocks)")
            
            for news_item in st.session_state.groq_news_data:
                self.display_groq_news_card(news_item)
        else:
            st.info("No Groq AI analysis available. Click 'Fetch Groq News Analysis' to get started.")
    
    def display_groq_news_card(self, news_item: Dict):
        """Display a Groq news analysis card."""
        symbol = news_item.get('symbol', 'N/A')
        company_name = news_item.get('company_name', 'Unknown Company')
        sentiment_label = news_item.get('sentiment_label', 'NEUTRAL')
        sentiment_score = news_item.get('sentiment_score', 0)
        confidence = news_item.get('confidence', 0)
        impact_level = news_item.get('impact_level', 'LOW')
        price_impact = news_item.get('price_impact', 'NEUTRAL')
        news_summary = news_item.get('news_summary', 'No summary available')
        key_factors = news_item.get('key_factors', [])
        news_type = news_item.get('news_type', 'OTHER')
        
        # Sentiment color and emoji based on news type
        sentiment_class = f"sentiment-{sentiment_label.lower()}"
        
        # Different emojis based on news type
        if news_type == "GOVERNMENT":
            sentiment_emoji = "🏛️" if sentiment_label == "POSITIVE" else "🏛️" if sentiment_label == "NEGATIVE" else "🏛️"
        elif news_type == "EARNINGS":
            sentiment_emoji = "💰" if sentiment_label == "POSITIVE" else "💸" if sentiment_label == "NEGATIVE" else "💰"
        elif news_type == "DEAL":
            sentiment_emoji = "🤝" if sentiment_label == "POSITIVE" else "🤝" if sentiment_label == "NEGATIVE" else "🤝"
        elif news_type == "REGULATORY":
            sentiment_emoji = "📋" if sentiment_label == "POSITIVE" else "📋" if sentiment_label == "NEGATIVE" else "📋"
        else:
            sentiment_emoji = "📈" if sentiment_label == "POSITIVE" else "📉" if sentiment_label == "NEGATIVE" else "➡️"
        
        # Create card
        with st.container():
            # Special styling for government news
            card_class = "groq-card government-highlight" if news_type == "GOVERNMENT" else "groq-card"
            title_emoji = "🏛️" if news_type == "GOVERNMENT" else "📈"
            
            st.markdown(f"""
            <div class="{card_class}">
                <h3>{title_emoji} {symbol} - {company_name}</h3>
                <p><span class="{sentiment_class}">{sentiment_emoji} {sentiment_label}</span> 
                (Score: {sentiment_score:.2f}, Confidence: {confidence:.1%})</p>
                <p><strong>News Type:</strong> {news_type}</p>
                <p><strong>Impact:</strong> {impact_level} | <strong>Price Impact:</strong> {price_impact}</p>
                <p><strong>Summary:</strong> {news_summary}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if key_factors:
                st.markdown("**🔑 Key Factors:**")
                for factor in key_factors[:5]:
                    st.markdown(f"• {factor}")
            
            st.markdown("---")
    
    def recommendations_tab(self):
        """BUY Recommendations tab."""
        st.header("🎯 BUY Recommendations Only")
        st.info("This tab shows only BUY recommendations with more lenient criteria for swing trading opportunities.")
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            if st.button("🔍 Generate BUY Recommendations", type="primary", key="generate_buy_recs_btn"):
                self.analyze_market()
        
        with col2:
            if st.button("🔄 Refresh", key="refresh_recs_btn"):
                st.rerun()

        disabled = st.session_state.fundamental_analysis_disabled
        toggle_label = "Enable fundamental analysis" if disabled else "Disable fundamental analysis"
        toggle_help = (
            "Enable fundamentals so recommendations also consider valuation, growth and health metrics."
            if disabled else
            "Disable fundamental analysis so only news sentiment and technical signals influence the recommendations."
        )

        with col3:
            if st.button(toggle_label, key="toggle_fundamental_btn", help=toggle_help):
                st.session_state.fundamental_analysis_disabled = not disabled

        with col4:
            status_value = "Disabled" if disabled else "Enabled"
            status_delta = "Using news & technical signals" if disabled else "Including fundamentals"
            st.metric("Fundamental Analysis", status_value, delta=status_delta)

        st.caption("When disabled, the recommendation engine ignores valuation/financial health data and relies on sentiment + technical indicators only.")
        
        # Recommendations are automatically saved when generated
        
        # Display recommendations
        if st.session_state.recommendations:
            recs      = st.session_state.recommendations
            buy_recs  = [r for r in recs if r.get('recommendation') == 'BUY']
            sell_recs = [r for r in recs if r.get('recommendation') == 'SELL']

            st.subheader(
                f"🎯 Signals: 📈 {len(buy_recs)} BUY  |  📉 {len(sell_recs)} SELL"
            )

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📈 BUY Signals", len(buy_recs))
            with col2:
                st.metric("📉 SELL Signals", len(sell_recs))
            with col3:
                avg_conf = sum(r.get('confidence', 0) for r in recs) / max(len(recs), 1)
                st.metric("Avg Confidence", f"{avg_conf:.1f}%")
            with col4:
                st.metric("Actions", "View Saved")
                if st.button("📊 View Saved", key="view_saved_recs"):
                    st.session_state.show_saved_recommendations = not st.session_state.get('show_saved_recommendations', False)

            # Signal-type filter
            signal_filter = st.radio(
                "Show signals:",
                ["All", "📈 BUY only", "📉 SELL only"],
                horizontal=True,
                key="signal_type_filter"
            )
            
            # Show saved recommendations if toggled
            if st.session_state.get('show_saved_recommendations', False):
                self.display_saved_recommendations()
                return

            st.markdown("---")

            # Header row with consistent alignment and tooltips
            col1, col2, col3, col4, col5, col6, col7 = st.columns([1.5, 1, 1, 1, 1, 0.8, 0.8])
            with col1:
                st.markdown("**Stock**")
            with col2:
                st.markdown("**Price (₹)**")
            with col3:
                st.markdown("**Confidence**")
            with col4:
                st.markdown("**Target (₹)**")
            with col5:
                st.markdown("**Stop Loss**")
            with col6:
                st.markdown("**Details**")
            with col7:
                st.markdown("**Actions**")

            st.markdown("<hr style='margin: 0.5rem 0;'/>", unsafe_allow_html=True)

            # Apply filter then sort by confidence descending
            if signal_filter == "📈 BUY only":
                filtered_recs = buy_recs
            elif signal_filter == "📉 SELL only":
                filtered_recs = sell_recs
            else:
                filtered_recs = recs

            sorted_recommendations = sorted(
                filtered_recs,
                key=lambda x: x.get('confidence', 0),
                reverse=True
            )

            # Display recommendations in rows (sorted by confidence)
            for i, rec in enumerate(sorted_recommendations):
                ExpandableUI.display_recommendation_row(rec, i)
                
                # Check if add to watchlist button was clicked
                if st.session_state.get(f"add_to_watchlist_{i}", False):
                    self.add_to_watchlist(rec)
                    st.session_state[f"add_to_watchlist_{i}"] = False
                    st.rerun()
        else:
            st.info("No BUY or SELL signals yet. Click 'Generate Recommendations' to get started.")
    
    def display_recommendation_card(self, rec: Dict, index: int):
        """Display a recommendation card with colour-coded styling for BUY / SELL / HOLD."""
        symbol          = rec.get('symbol', 'N/A')
        recommendation  = rec.get('recommendation', 'HOLD')
        confidence      = rec.get('confidence', 0)
        current_price   = rec.get('current_price', 0)
        target_price    = rec.get('target_price', 0)
        stop_loss       = rec.get('stop_loss', 0)
        reasoning       = rec.get('reasoning', 'No reasoning provided')
        swing_plan      = rec.get('swing_plan', {})

        # Visual cues per signal type
        if recommendation == 'BUY':
            rec_emoji   = '📈'
            border_col  = '#28a745'
            label_col   = '#28a745'
            direction   = 'LONG'
        elif recommendation == 'SELL':
            rec_emoji   = '📉'
            border_col  = '#dc3545'
            label_col   = '#dc3545'
            direction   = 'SHORT'
        else:
            rec_emoji   = '➡️'
            border_col  = '#ffc107'
            label_col   = '#ffc107'
            direction   = 'HOLD'

        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                if recommendation == 'SELL':
                    price_row = (
                        f"<strong>Entry (Short):</strong> ₹{current_price:.2f} | "
                        f"<strong>Target:</strong> ₹{target_price:.2f} | "
                        f"<strong>Stop (Cover):</strong> ₹{stop_loss:.2f}"
                    )
                elif recommendation == 'BUY':
                    price_row = (
                        f"<strong>Current:</strong> ₹{current_price:.2f} | "
                        f"<strong>Target:</strong> ₹{target_price:.2f} | "
                        f"<strong>Stop Loss:</strong> ₹{stop_loss:.2f}"
                    )
                else:
                    price_row = f"<strong>Current:</strong> ₹{current_price:.2f} &nbsp;|&nbsp; No active trade targets"

                st.markdown(f"""
                <div style="background:#1e1e1e; padding:0.8rem; border-radius:0.5rem;
                            border-left:4px solid {border_col}; margin-bottom:0.4rem;">
                    <h3 style="margin:0; color:#f0f0f0;">{rec_emoji} {symbol}</h3>
                    <p style="margin:0.3rem 0;">
                        <span style="color:{label_col}; font-weight:bold; font-size:1.1rem;">
                            {recommendation} ({direction})
                        </span>
                        &nbsp;&mdash;&nbsp;Confidence: <strong>{confidence:.1f}%</strong>
                    </p>
                    <p style="margin:0; color:#cccccc; font-size:0.9rem;">{price_row}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button('📊 Details', key=f'details_{index}'):
                    self.show_recommendation_details(rec)

            with col3:
                if st.button('👀 Add to Watchlist', key=f'watchlist_{index}'):
                    self.add_to_watchlist(rec)

            # Reasoning
            with st.expander(f'💭 Reasoning for {symbol}'):
                st.markdown(reasoning)
            
            st.markdown("---")
    
    def display_buy_recommendation_card(self, rec: Dict, index: int, show_swing_plans: bool = True):
        """Display a BUY recommendation card with swing trading details."""
        symbol = rec.get('symbol', 'N/A')
        confidence = rec.get('confidence', 0)
        current_price = rec.get('current_price', 0)
        target_price = rec.get('target_price', 0)
        stop_loss = rec.get('stop_loss', 0)
        reasoning = rec.get('reasoning', 'No reasoning provided')
        swing_plan = rec.get('swing_plan', {})
        swing_validation = rec.get('swing_validation', {})
        
        # Create card
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                # Main recommendation info
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📈 {symbol} - BUY RECOMMENDATION</h3>
                    <p><span class="recommendation-buy">BUY</span> 
                    (Confidence: {confidence:.1f}%)</p>
                    <p><strong>Current:</strong> ₹{current_price:.2f} | 
                    <strong>Target:</strong> ₹{target_price:.2f} | 
                    <strong>Stop Loss:</strong> ₹{stop_loss:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Swing trading validation score
                if swing_validation:
                    score = swing_validation.get('score', 0)
                    is_suitable = swing_validation.get('is_suitable', False)
                    score_color = "green" if score >= 70 else "orange" if score >= 50 else "red"
                    
                    st.markdown(f"""
                    <div style="background-color: #2d2d2d; padding: 0.5rem; border-radius: 0.5rem; margin: 0.5rem 0;">
                        <p><strong>Swing Trading Score:</strong> <span style="color: {score_color}">{score}/100</span></p>
                        <p><strong>Suitable for Swing:</strong> {'✅ Yes' if is_suitable else '❌ No'}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"📊 Details", key=f"details_{index}"):
                    self.show_recommendation_details(rec)
            
            with col3:
                if st.button(f"👀 Add to Watchlist", key=f"watchlist_{index}"):
                    self.add_to_watchlist(rec)
            
            # Swing trading plan (if available and requested)
            if show_swing_plans and swing_plan:
                with st.expander(f"📈 7-Day Swing Trading Plan for {symbol}"):
                    self.display_swing_plan(swing_plan)
            
            # Reasoning
            with st.expander(f"💭 Reasoning for {symbol}"):
                st.markdown(reasoning)
            
            st.markdown("---")
    
    def display_swing_plan(self, swing_plan: Dict):
        """Display swing trading plan details."""
        try:
            # Display stock information header
            symbol = swing_plan.get('symbol', 'UNKNOWN')
            company_name = swing_plan.get('company_name', '')
            confidence = swing_plan.get('confidence', 0)
            
            # Create header with stock info
            if company_name:
                st.markdown(f"### 📈 {symbol} - {company_name}")
            else:
                st.markdown(f"### 📈 {symbol}")
            
            # Confidence indicator
            if confidence >= 80:
                st.success(f"🎯 High Confidence: {confidence:.1f}%")
            elif confidence >= 60:
                st.warning(f"⚠️ Medium Confidence: {confidence:.1f}%")
            else:
                st.info(f"ℹ️ Confidence: {confidence:.1f}%")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Position Details:**")
                st.write(f"• Investment Amount: ₹{swing_plan.get('investment_amount', 0):,.0f}")
                st.write(f"• Position Size: {swing_plan.get('position_size', 0)} shares")
                st.write(f"• Risk Amount: ₹{swing_plan.get('risk_amount', 0):,.0f}")
                st.write(f"• Risk Percentage: {swing_plan.get('risk_percentage', 0):.1f}%")
                
                st.markdown("**🎯 Entry/Exit Levels:**")
                st.write(f"• Entry Price: ₹{swing_plan.get('entry_price', 0):.2f}")
                st.write(f"• Stop Loss: ₹{swing_plan.get('stop_loss', 0):.2f}")
                st.write(f"• Take Profit: ₹{swing_plan.get('take_profit', 0):.2f}")
                st.write(f"• Risk-Reward Ratio: {swing_plan.get('risk_reward_ratio', 0):.2f}:1")
            
            with col2:
                st.markdown("**📅 Timeline:**")
                st.write(f"• Entry Date: {swing_plan.get('entry_date', 'N/A')[:10]}")
                st.write(f"• Expected Exit: {swing_plan.get('expected_exit_date', 'N/A')[:10]}")
                st.write(f"• Holding Period: {swing_plan.get('holding_period_days', 7)} days")
                
                st.markdown("**💰 Potential Returns:**")
                st.write(f"• Potential Profit: ₹{swing_plan.get('potential_profit', 0):.2f}")
                st.write(f"• Potential Loss: ₹{swing_plan.get('potential_loss', 0):.2f}")
                st.write(f"• Profit Percentage: {((swing_plan.get('potential_profit', 0) / swing_plan.get('investment_amount', 1)) * 100):.1f}%")
            
            # Strategy rules
            st.markdown("**📋 Strategy Rules:**")
            rules = swing_plan.get('strategy_rules', [])
            for rule in rules:
                st.write(f"• {rule}")
            
            # Risk management
            st.markdown("**⚠️ Risk Management:**")
            risk_mgmt = swing_plan.get('risk_management', [])
            for risk in risk_mgmt:
                st.write(f"• {risk}")
            
                
        except Exception as e:
            st.error(f"Error displaying swing plan: {str(e)}")
    
    def display_saved_swing_strategies(self):
        """Display saved swing strategies."""
        st.header("📈 Saved Swing Trading Plans")
        
        # Get all saved swing strategies (date-wise dict) and flatten into a list
        all_strategies_by_date = st.session_state.data_persistence.get_all_swing_strategies()
        
        if all_strategies_by_date:
            saved_strategies = []
            for date_str, strategies in all_strategies_by_date.items():
                if not isinstance(strategies, list):
                    continue
                for strategy in strategies:
                    # Attach date for potential future use
                    if isinstance(strategy, dict):
                        strategy.setdefault('saved_date', date_str)
                        saved_strategies.append(strategy)
        else:
            saved_strategies = []

        if saved_strategies:
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Strategies", len(saved_strategies))
            
            with col2:
                high_confidence = len([s for s in saved_strategies if s.get('confidence', 0) >= 80])
                st.metric("High Confidence", high_confidence)
            
            with col3:
                avg_risk_reward = sum(s.get('risk_reward_ratio', 0) for s in saved_strategies) / len(saved_strategies) if saved_strategies else 0
                st.metric("Avg Risk-Reward", f"{avg_risk_reward:.2f}:1")
            
            with col4:
                # Calculate days to expiry
                current_date = datetime.now()
                total_days = 0
                for strategy in saved_strategies:
                    try:
                        exit_date = datetime.fromisoformat(strategy.get('expected_exit_date', '').replace('Z', '+00:00'))
                        days_remaining = (exit_date - current_date).days
                        total_days += max(0, days_remaining)
                    except:
                        total_days += 7  # Default 7 days
                avg_days = total_days / len(saved_strategies) if saved_strategies else 0
                st.metric("Avg Days Left", f"{avg_days:.0f}")
            
            st.info(f"Showing {len(saved_strategies)} saved strategies.")
            
            st.markdown("---")
            
            # Header row with consistent alignment (includes Created date)
            col1, col_date, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.5, 1, 1, 1, 1, 0.8, 1, 0.8, 0.8])
            with col1:
                st.markdown("**Stock**")
            with col_date:
                st.markdown("**Created**")
            with col2:
                st.markdown("**Entry (₹)**")
            with col3:
                st.markdown("**Take Profit (₹)**")
            with col4:
                st.markdown("**Stop Loss (₹)**")
            with col5:
                st.markdown("**Days**")
            with col6:
                st.markdown("**Status**")
            with col7:
                st.markdown("**Details**")
            with col8:
                st.markdown("**Delete**")
            
            st.markdown("<hr style='margin: 0.5rem 0;'/>", unsafe_allow_html=True)
            
            # Display saved swing strategies in rows
            current_date = datetime.now()
            for i, strategy in enumerate(saved_strategies):
                # Get the values with proper fallbacks
                symbol = strategy.get('symbol', 'UNKNOWN')
                company_name = strategy.get('company_name', '')
                created_at = strategy.get('created_at', '')
                saved_date = strategy.get('saved_date', '')
                
                # Calculate days remaining (7-day validity from creation)
                try:
                    if created_at:
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        days_remaining = 7 - (current_date - created_date).days
                        days_remaining = max(0, min(7, days_remaining))  # Clamp between 0 and 7
                    else:
                        days_remaining = 7  # Default to 7 days if no creation date
                except Exception as e:
                    logger.warning(f"Error calculating days remaining for {symbol}: {str(e)}")
                    days_remaining = 7
                
                current_price = strategy.get('current_price', 0)
                
                # Get entry/exit levels with proper fallbacks
                entry_price = strategy.get('entry_price', current_price)
                take_profit = strategy.get('take_profit', 0)
                stop_loss = strategy.get('stop_loss', 0)
                
                # If we have a 'levels' dictionary, use those values
                if 'levels' in strategy and isinstance(strategy['levels'], dict):
                    entry_price = strategy['levels'].get('entry_price', entry_price)
                    take_profit = strategy['levels'].get('take_profit', take_profit)
                    stop_loss = strategy['levels'].get('stop_loss', stop_loss)
                
                # Ensure we have valid values
                entry_price = entry_price or current_price

                # Derive a compact created date string
                created_date_str = ""
                try:
                    if created_at:
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        created_date_str = created_date.strftime("%Y-%m-%d")
                    elif saved_date:
                        created_date_str = str(saved_date)
                except Exception:
                    created_date_str = saved_date or ""

                # Display strategy details (compact row)
                col1, col_date, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.5, 1, 1, 1, 1, 0.8, 1, 0.8, 0.8])
                with col1:
                    st.markdown(f"<span style='font-size:0.8rem;'>{symbol} - {company_name}</span>", unsafe_allow_html=True)
                with col_date:
                    st.markdown(f"<span style='font-size:0.8rem;'>{created_date_str}</span>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<span style='font-size:0.8rem;'>₹{entry_price:.2f}</span>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<span style='font-size:0.8rem;'>₹{take_profit:.2f}</span>", unsafe_allow_html=True)
                with col4:
                    st.markdown(f"<span style='font-size:0.8rem;'>₹{stop_loss:.2f}</span>", unsafe_allow_html=True)
                with col5:
                    st.markdown(f"<span style='font-size:0.8rem;'>{days_remaining} days</span>", unsafe_allow_html=True)
                with col6:
                    st.markdown("<span style='font-size:0.8rem;'>Saved</span>", unsafe_allow_html=True)
                with col7:
                    if st.button("📊", key=f"details_{i}"):
                        self.display_swing_plan(strategy)
                with col8:
                    if st.button("🗑️", key=f"delete_{i}"):
                        st.session_state.data_persistence.delete_swing_strategy(strategy)
                        st.success(f"Deleted {symbol} strategy!")
                        st.rerun()

                st.markdown("<hr style='margin: 0.2rem 0;'/>", unsafe_allow_html=True)
    
    def swing_trading_tab(self):
        """Swing Trading Plans tab."""
        st.header("📈 7-Day Swing Trading Plans")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.button("🔄 Refresh Strategies", type="primary", key="refresh_strategies_btn"):
                if st.session_state.get('recommendations'):
                    st.rerun()
                else:
                    st.warning("No recommendations to refresh. Run market analysis first.")
        
        with col2:
            if st.button("📊 Analyze Performance", type="secondary", key="analyze_swing_performance_btn"):
                self.analyze_swing_performance()
        
        with col3:
            if st.button("📅 View All Dates", key="view_all_swing"):
                st.session_state.show_all_swing_dates = not st.session_state.get('show_all_swing_dates', False)

        # Toggle between today's strategies and all dates view
        if st.session_state.get('show_all_swing_dates', False):
            self.display_saved_swing_strategies()
            return
        
        # Display current adaptive parameters
        self.display_current_adaptive_parameters()
        
        # Get today's date in YYYY-MM-DD format
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get all swing strategies for today
        swing_strategies = []
        seen_symbols = set()
        
        # 1. Get strategies from current recommendations
        if st.session_state.get('recommendations'):
            for rec in st.session_state.recommendations:
                if 'swing_plan' in rec:
                    symbol = rec.get('symbol')
                    if symbol and symbol not in seen_symbols:
                        swing_plan = rec['swing_plan']
                        # Add basic info if missing
                        if 'symbol' not in swing_plan:
                            swing_plan['symbol'] = symbol
                        if 'company_name' not in swing_plan and 'company_name' in rec:
                            swing_plan['company_name'] = rec['company_name']
                        if 'current_price' not in swing_plan and 'current_price' in rec:
                            swing_plan['current_price'] = rec['current_price']
                        
                        swing_strategies.append(swing_plan)
                        seen_symbols.add(symbol)
        
        # 2. Get any additional saved strategies for today
        saved_strategies = st.session_state.data_persistence.get_swing_strategies_by_date(today)
        if saved_strategies:
            for strategy in saved_strategies:
                symbol = strategy.get('symbol')
                if symbol and symbol not in seen_symbols:
                    swing_strategies.append(strategy)
                    seen_symbols.add(symbol)
        
        if swing_strategies:
            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Strategies", len(swing_strategies))
            
            with col2:
                high_confidence = len([s for s in swing_strategies if s.get('confidence', 0) >= 80])
                st.metric("High Confidence", high_confidence)
            
            with col3:
                avg_risk_reward = sum(s.get('risk_reward_ratio', 0) for s in swing_strategies) / len(swing_strategies) if swing_strategies else 0
                st.metric("Avg Risk-Reward", f"{avg_risk_reward:.2f}:1")
            
            with col4:
                # Calculate days to expiry
                current_date = datetime.now()
                total_days = 0
                for strategy in swing_strategies:
                    try:
                        exit_date = datetime.fromisoformat(strategy.get('expected_exit_date', '').replace('Z', '+00:00'))
                        days_remaining = (exit_date - current_date).days
                        total_days += max(0, days_remaining)
                    except:
                        total_days += 7  # Default 7 days
                avg_days = total_days / len(swing_strategies) if swing_strategies else 0
                st.metric("Avg Days Left", f"{avg_days:.0f}")
            
            st.info(f"Showing {len(swing_strategies)} strategies for {today}. Click 'View All Dates' to see strategies from other dates.")
            
            st.markdown("---")
            
            # Header row with consistent alignment (includes Created date)
            col1, col_date, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.5, 1, 1, 1, 1, 0.8, 1, 0.8, 0.8])
            with col1:
                st.markdown("**Stock**")
            with col_date:
                st.markdown("**Created**")
            with col2:
                st.markdown("**Entry (₹)**")
            with col3:
                st.markdown("**Take Profit (₹)**")
            with col4:
                st.markdown("**Stop Loss (₹)**")
            with col5:
                st.markdown("**Days**")
            with col6:
                st.markdown("**Status**")
            with col7:
                st.markdown("**Details**")
            with col8:
                st.markdown("**Delete**")
            
            st.markdown("<hr style='margin: 0.5rem 0;'/>", unsafe_allow_html=True)
            
            # Display swing strategies in rows
            current_date = datetime.now()
            for i, strategy in enumerate(swing_strategies):
                # Get the values with proper fallbacks
                symbol = strategy.get('symbol', 'UNKNOWN')
                company_name = strategy.get('company_name', '')
                created_at = strategy.get('created_at', '')
                
                try:
                    if created_at:
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        days_remaining = 7 - (current_date - created_date).days
                        days_remaining = max(0, min(7, days_remaining))  # Clamp between 0 and 7
                    else:
                        days_remaining = 7  # Default to 7 days if no creation date
                except Exception as e:
                    logger.warning(f"Error calculating days remaining for {symbol}: {str(e)}")
                    days_remaining = 7
                
                current_price = strategy.get('current_price', 0)
                
                # Get entry/exit levels with proper fallbacks
                entry_price = strategy.get('entry_price', current_price)
                take_profit = strategy.get('take_profit', 0)
                stop_loss = strategy.get('stop_loss', 0)
                
                # If we have a 'levels' dictionary, use those values
                if 'levels' in strategy and isinstance(strategy['levels'], dict):
                    entry_price = strategy['levels'].get('entry_price', entry_price)
                    take_profit = strategy['levels'].get('take_profit', take_profit)
                    stop_loss = strategy['levels'].get('stop_loss', stop_loss)
                
                # Ensure we have valid values
                entry_price = entry_price or current_price

                # Derive a compact created date string
                created_date_str = ""
                try:
                    if created_at:
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        created_date_str = created_date.strftime("%Y-%m-%d")
                    else:
                        created_date_str = today
                except Exception:
                    created_date_str = today

                # Display strategy details - compact row for today's view
                col1, col_date, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.5, 1, 1, 1, 1, 0.8, 1, 0.8, 0.8])
                with col1:
                    st.markdown(f"<span style='font-size:0.8rem;'>{symbol} - {company_name}</span>", unsafe_allow_html=True)
                with col_date:
                    st.markdown(f"<span style='font-size:0.8rem;'>{created_date_str}</span>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<span style='font-size:0.8rem;'>₹{entry_price:.2f}</span>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<span style='font-size:0.8rem;'>₹{take_profit:.2f}</span>", unsafe_allow_html=True)
                with col4:
                    st.markdown(f"<span style='font-size:0.8rem;'>₹{stop_loss:.2f}</span>", unsafe_allow_html=True)
                with col5:
                    st.markdown(f"<span style='font-size:0.8rem;'>{days_remaining} days</span>", unsafe_allow_html=True)
                with col6:
                    st.markdown("<span style='font-size:0.8rem;'>Active</span>", unsafe_allow_html=True)
                with col7:
                    if st.button("📊", key=f"swing_today_details_{i}"):
                        self.display_swing_plan(strategy)
                with col8:
                    if st.button("🗑️", key=f"swing_today_delete_{i}"):
                        date_str = today  # Use today's date for deletion
                        st.session_state.data_persistence.delete_swing_strategy(symbol, date_str)
                        st.success(f"Deleted {symbol} strategy for {date_str}!")
                        st.rerun()

                st.markdown("<hr style='margin: 0.2rem 0;'/>", unsafe_allow_html=True)
    
    def display_saved_watchlist(self):
        """Display saved watchlist items from persistent storage."""
        data_persistence = st.session_state.data_persistence
        try:
            saved_watchlist = data_persistence.get_watchlist()
        except Exception as e:
            logger.error(f"Error loading saved watchlist: {str(e)}")
            st.error("Failed to load saved watchlist from storage.")
            return
        
        if not saved_watchlist:
            st.info("No saved watchlist items found in storage.")
            return
        
        st.subheader(f"📁 Saved Watchlist Items ({len(saved_watchlist)} stocks)")
        
        # Simple tabular display of saved items
        for item in saved_watchlist:
            symbol = item.get('symbol', 'N/A')
            company_name = item.get('company_name', '')
            entry_price = item.get('entry_price', 0)
            current_price = item.get('current_price', 0)
            status = item.get('status', 'ACTIVE')
            added_date = item.get('added_date', '')
            
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([1.5, 2, 1, 1, 1])
                col1.write(symbol)
                col2.write(company_name or "-")
                col3.write(f"₹{entry_price:.2f}")
                col4.write(f"₹{current_price:.2f}" if current_price else "-")
                col5.write(status)
                if added_date:
                    st.caption(f"Added: {added_date}")
            
            st.markdown("---")
    
    def watchlist_tab(self):
        """Watchlist tab."""
        st.header("👀 Watchlist Management")

        # Auto-update prices if it's the first load or refresh interval has passed
        last_update = st.session_state.get('last_price_update')
        refresh_interval = 300  # 5 minutes in seconds

        if last_update is None or (datetime.now() - last_update).total_seconds() > refresh_interval:
            with st.spinner("Updating stock prices..."):
                self.update_watchlist_prices()
            st.session_state['last_price_update'] = datetime.now()

        # Check for delete actions from watchlist details (per-row X button)
        for key in list(st.session_state.keys()):
            if key.startswith('delete_from_watchlist_'):
                symbol_to_delete = key.replace('delete_from_watchlist_', '')
                st.session_state.watchlist = [
                    item for item in st.session_state.watchlist
                    if item.get('symbol') != symbol_to_delete
                ]
                self._auto_save_watchlist()
                del st.session_state[key]
                st.success(f"✅ Deleted {symbol_to_delete} from watchlist!")
                st.rerun()

        # Top action buttons
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

        with col1:
            if st.button("🔄 Update Prices", type="primary", key="update_prices_btn"):
                self.update_watchlist_prices()

        with col2:
            if st.button("🧠 Analyze Performance", key="analyze_performance_btn"):
                self.analyze_watchlist_stocks()

        # col3 reserved for future actions

        with col4:
            if st.button("🗑️ Clear Watchlist", key="clear_watchlist_btn"):
                st.session_state.watchlist = []
                self._auto_save_watchlist()
                st.success("Watchlist cleared!")
                st.rerun()

        # Display watchlist content
        if st.session_state.watchlist:
            st.subheader(f"👀 Watchlist ({len(st.session_state.watchlist)} stocks)")

            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Stocks", len(st.session_state.watchlist))

            with col2:
                active_count = len([
                    item for item in st.session_state.watchlist
                    if item.get('status') == 'ACTIVE'
                ])
                st.metric("Active", active_count)

            with col3:
                total_pnl_percent = 0
                valid_stocks = 0
                for item in st.session_state.watchlist:
                    entry_price = item.get('entry_price', 0)
                    current_price = item.get('current_price', 0)
                    if entry_price > 0:
                        pnl_percent = ((current_price - entry_price) / entry_price) * 100
                        total_pnl_percent += pnl_percent
                        valid_stocks += 1

                if valid_stocks > 0:
                    avg_pnl_percent = total_pnl_percent / valid_stocks
                    pnl_color = "#28a745" if avg_pnl_percent > 0 else "#dc3545" if avg_pnl_percent < 0 else "#6c757d"
                    st.markdown(
                        f'<div style="font-size: 1.5rem; color: {pnl_color};">'
                        f'<b>Avg P&L</b><br>{avg_pnl_percent:+.1f}%'
                        '</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.metric("Avg P&L", "0.0%")

            with col4:
                st.metric("Actions", "View Saved")
                if st.button("📊 View Saved", key="view_saved_watchlist"):
                    st.session_state.show_saved_watchlist = not st.session_state.get(
                        'show_saved_watchlist', False
                    )

            # Show saved watchlist if toggled
            if st.session_state.get('show_saved_watchlist', False):
                self.display_saved_watchlist()
                return

            st.markdown("---")

            # Sorting controls
            sort_col1, sort_col2 = st.columns(2)
            with sort_col1:
                sort_by = st.selectbox(
                    "Sort by",
                    ["Date Added", "Symbol", "P&L %", "Current Price", "Entry Price", "Status"],
                    key="watchlist_sort_by"
                )
            with sort_col2:
                sort_order = st.radio(
                    "Order",
                    ["Ascending", "Descending"],
                    index=1,
                    horizontal=True,
                    key="watchlist_sort_order"
                )

            # Apply sorting
            sorted_watchlist = st.session_state.watchlist.copy()
            reverse_sort = (sort_order == "Descending")

            if sort_by == "Symbol":
                sorted_watchlist.sort(
                    key=lambda x: x.get('symbol', '').upper(),
                    reverse=reverse_sort
                )
            elif sort_by == "P&L %":
                sorted_watchlist.sort(
                    key=lambda x: (
                        (x.get('current_price', 0) - x.get('entry_price', 0)) / x.get('entry_price', 1)
                        if x.get('entry_price', 0) > 0 else 0
                    ),
                    reverse=reverse_sort
                )
            elif sort_by == "Current Price":
                sorted_watchlist.sort(
                    key=lambda x: x.get('current_price', 0),
                    reverse=reverse_sort
                )
            elif sort_by == "Entry Price":
                sorted_watchlist.sort(
                    key=lambda x: x.get('entry_price', 0),
                    reverse=reverse_sort
                )
            elif sort_by == "Status":
                sorted_watchlist.sort(
                    key=lambda x: x.get('status', ''),
                    reverse=not reverse_sort
                )
            else:  # Date Added
                sorted_watchlist.sort(
                    key=lambda x: x.get('added_date', ''),
                    reverse=not reverse_sort  # Most recent first
                )

            # Display sorted watchlist items in rows
            for i, item in enumerate(sorted_watchlist):
                ExpandableUI.display_watchlist_row(item, i)

            # Bulk delete selected stocks
            st.markdown("---")
            if st.button("🗑️ Delete Selected", key="bulk_delete_watchlist_btn"):
                selected_symbols = []
                for item in st.session_state.watchlist:
                    symbol = item.get('symbol')
                    if not symbol:
                        continue
                    if st.session_state.get(f"watchlist_select_{symbol}", False):
                        selected_symbols.append(symbol)

                if selected_symbols:
                    st.session_state.watchlist = [
                        item for item in st.session_state.watchlist
                        if item.get('symbol') not in selected_symbols
                    ]
                    self._auto_save_watchlist()

                    for symbol in selected_symbols:
                        select_key = f"watchlist_select_{symbol}"
                        if select_key in st.session_state:
                            del st.session_state[select_key]

                    st.success(f"Deleted {len(selected_symbols)} selected watchlist item(s)")
                    st.rerun()
        else:
            st.info("No stocks in watchlist. Add stocks from recommendations or manual analysis.")

    def fetch_news(self):
        """Fetch and display filtered Indian news articles."""
        with st.spinner("📰 Fetching and filtering Indian news..."):
            try:
                # Step 1: Fetch all articles from RSS feeds
                all_articles = self.news_analyzer.fetch_all_news_articles()
                
                if not all_articles:
                    st.warning("⚠️ No articles found in RSS feeds")
                    return
                
                st.info(f"📊 Fetched {len(all_articles)} total articles from RSS feeds")
                
                # Step 2: Filter by India-related keywords in headlines
                indian_articles = self.news_analyzer.filter_indian_news_by_headline(all_articles)
                
                if not indian_articles:
                    st.warning("⚠️ No India-related articles found")
                    return
                
                # Store filtered articles
                st.session_state.news_articles = indian_articles
                st.session_state.all_articles_count = len(all_articles)
                st.session_state.indian_articles_count = len(indian_articles)
                
                # Auto-save news articles
                self._auto_save_news()
                
                st.success(f"✅ Filtered {len(indian_articles)} India-related articles from {len(all_articles)} total articles")
                
                # Display filtered articles
                self.display_filtered_news(indian_articles)
                
            except Exception as e:
                st.error(f"❌ Error fetching news: {str(e)}")
    
    def display_filtered_news(self, articles: List[Dict]):
        """Display filtered Indian news articles."""
        st.subheader(f"🇮🇳 Indian News Articles ({len(articles)} articles)")
        
        # Show filtering statistics
        if hasattr(st.session_state, 'all_articles_count') and hasattr(st.session_state, 'indian_articles_count'):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Articles", st.session_state.all_articles_count)
            with col2:
                st.metric("Indian Articles", st.session_state.indian_articles_count)
            with col3:
                filter_rate = (st.session_state.indian_articles_count / st.session_state.all_articles_count * 100) if st.session_state.all_articles_count > 0 else 0
                st.metric("Filter Rate", f"{filter_rate:.1f}%")
        
        # Display articles
        for i, article in enumerate(articles[:20]):  # Show first 20 articles
            with st.expander(f"📰 {i+1}. {article.get('title', 'No title')[:80]}..."):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Title:** {article.get('title', 'No title')}")
                    st.write(f"**Description:** {article.get('description', 'No description')}")
                    st.write(f"**Source:** {article.get('source', 'Unknown')}")
                    st.write(f"**Published:** {article.get('publishedAt', 'No date')}")
                
                with col2:
                    st.write(f"**URL:** [Read Full Article]({article.get('url', '#')})")
                    st.write("🇮🇳 **India Related:** ✅")
                    if article.get('filter_reason'):
                        st.write(f"**Filter Reason:** {', '.join(article.get('filter_reason', []))}")
                
                st.write("---")
    
    def analyze_sentiment(self):
        """Analyze news sentiment."""
        if not st.session_state.news_articles:
            st.error("No news articles available. Please fetch news first.")
            return
        
        with st.spinner("🔍 Analyzing sentiment..."):
            try:
                sentiment = self.news_analyzer.analyze_news_sentiment(st.session_state.news_articles)
                st.success(f"✅ Sentiment analysis complete: {sentiment:.3f}")
            except Exception as e:
                st.error(f"❌ Error analyzing sentiment: {str(e)}")
    
    def test_rss_feeds(self):
        """Test RSS feeds to see what content they provide."""
        with st.spinner("🔍 Testing RSS feeds..."):
            try:
                feed_results = self.news_analyzer.test_rss_feeds()
                
                st.subheader("📡 RSS Feed Test Results")
                
                for feed_url, result in feed_results.items():
                    with st.expander(f"📰 {feed_url.split('/')[-1]}"):
                        if result.get('status') == 'success':
                            st.success(f"✅ {result.get('article_count', 0)} articles found")
                            
                            st.write("**Sample Articles:**")
                            for i, article in enumerate(result.get('sample_articles', [])[:3]):
                                st.write(f"**{i+1}.** {article.get('title', 'No title')}")
                                st.write(f"   📅 {article.get('publishedAt', 'No date')}")
                                st.write(f"   🔗 {article.get('url', 'No URL')}")
                                st.write("---")
                        else:
                            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                            
            except Exception as e:
                st.error(f"❌ Error testing RSS feeds: {str(e)}")
    
    def fetch_groq_news_analysis(self):
        """Fetch Groq news analysis with full content from filtered Indian articles."""
        with st.spinner("📰 Fetching top 10 Indian news with full content..."):
            try:
                # Step 1: Fetch top 10 Indian news articles with full content
                top_10_news = self.news_analyzer.fetch_top_10_news_with_content()
                
                if not top_10_news:
                    st.error("❌ No Indian news articles fetched")
                    return
                
                st.success(f"✅ Fetched {len(top_10_news)} Indian news articles with content")
                
                # Show sample of fetched articles
                with st.expander("📰 Sample Indian Articles for Groq Analysis"):
                    for i, article in enumerate(top_10_news[:3]):
                        content_length = len(article.get('full_content', ''))
                        content_source = "Full Article" if content_length > 200 else "Description Fallback"
                        
                        st.write(f"**{i+1}.** {article.get('title', 'No title')}")
                        st.write(f"   📅 {article.get('publishedAt', 'No date')}")
                        st.write(f"   🇮🇳 India Related: {article.get('is_india_related', True)}")
                        st.write(f"   📄 Content: {content_source} ({content_length} characters)")
                        
                        # Show content preview
                        content_preview = article.get('full_content', '')[:200] + "..." if len(article.get('full_content', '')) > 200 else article.get('full_content', '')
                        st.write(f"   📝 Preview: {content_preview}")
                        st.write("---")
                
                # Step 2: Analyze with Groq AI
                with st.spinner("🤖 Analyzing Indian news with Groq AI..."):
                    groq_data = self.groq_analyzer.analyze_top_10_news_with_full_content(top_10_news)
                    
                    if groq_data.get('status') == 'success':
                        st.session_state.groq_news_data = groq_data.get('articles', [])
                        st.success(f"✅ Analyzed {len(st.session_state.groq_news_data)} Indian stocks from news")
                    else:
                        st.error(f"❌ Groq analysis failed: {groq_data.get('message', 'Unknown error')}")
                        
            except Exception as e:
                st.error(f"❌ Error in news analysis: {str(e)}")
    
    def _validate_nse_stocks(self, stock_symbols: List[str]) -> List[str]:
        """Validate stock symbols against known NSE stocks."""
        try:
            # Get comprehensive list of NSE stocks
            nse_stocks = self.news_analyzer.get_comprehensive_nse_stocks_list()
            nse_stocks_set = set(nse_stocks)
            
            # Filter out invalid stocks
            valid_stocks = []
            for symbol in stock_symbols:
                # Remove any suffixes like .NS, .BO, etc.
                clean_symbol = symbol.split('.')[0].upper()
                
                # Check if it's in our NSE list
                if clean_symbol in nse_stocks_set:
                    valid_stocks.append(clean_symbol)
                else:
                    logger.warning(f"Invalid/delisted stock symbol: {symbol}")
            
            logger.info(f"Validated {len(valid_stocks)} out of {len(stock_symbols)} stock symbols")
            return valid_stocks
            
        except Exception as e:
            logger.error(f"Error validating NSE stocks: {str(e)}")
            return stock_symbols  # Return original list if validation fails
    
    def analyze_market(self):
        """Analyze market and generate recommendations."""
        if st.session_state.analysis_in_progress:
            st.warning("Analysis already in progress. Please wait...")
            return
        
        st.session_state.analysis_in_progress = True
        
        fundamental_enabled = not st.session_state.fundamental_analysis_disabled

        try:
            with st.spinner("🔍 Starting comprehensive market analysis..."):
                # Step 1: Fetch news with caching
                st.info("📰 Step 1: Fetching news with caching...")
                all_news = self.news_analyzer.fetch_top_10_news_with_content()
                
                if not all_news:
                    st.error("❌ No news articles fetched")
                    return
                
                # Cache articles and get only new ones
                cache_manager = st.session_state.cache_manager
                new_articles = cache_manager.cache_articles(all_news)
                
                st.success(f"✅ Fetched {len(all_news)} total articles, {len(new_articles)} new articles")
                
                # Step 2: Analyze with Groq AI to get stocks with sentiment impact
                st.info("🤖 Step 2: Analyzing news with Groq AI...")
                groq_news_data = self.groq_analyzer.analyze_top_10_news_with_full_content(all_news)
                
                if groq_news_data.get('status') != 'success':
                    st.error(f"❌ Groq analysis failed: {groq_news_data.get('message', 'Unknown error')}")
                    return
                
                # Extract stocks from Groq analysis and validate them
                all_news_stocks = [item.get('symbol', '') for item in groq_news_data.get('articles', []) if item.get('symbol')]
                news_stocks = self._validate_nse_stocks(all_news_stocks)
                
                if len(news_stocks) != len(all_news_stocks):
                    invalid_stocks = set(all_news_stocks) - set(news_stocks)
                    st.warning(f"⚠️ Filtered out {len(invalid_stocks)} invalid/delisted stocks: {', '.join(list(invalid_stocks)[:5])}")
                
                # Filter out stocks already in watchlist (unless very negative news)
                filtered_stocks = cache_manager.filter_watchlist_stocks(
                    groq_news_data.get('articles', []), 
                    st.session_state.watchlist,
                    allow_negative_news=True
                )
                
                # Get symbols from filtered stocks
                news_stocks = [stock.get('symbol', '') for stock in filtered_stocks if stock.get('symbol')]
                
                st.success(f"✅ Identified {len(news_stocks)} valid NSE stocks with sentiment impact (after watchlist filtering)")
                
                # Step 3: Analyze news stocks
                st.info("📊 Step 3: Analyzing stocks from news...")
                news_recommendations = []
                
                progress_bar = st.progress(0)
                total_stocks = len(news_stocks)
                
                for i, symbol in enumerate(news_stocks):
                    try:
                        symbol_with_suffix = f"{symbol}.NS"
                        
                        # Check cache for stock analysis
                        cached_analysis = cache_manager.get_cached_stock_analysis(symbol)

                        if cached_analysis and fundamental_enabled:
                            # Use cached analysis
                            technical_data = cached_analysis.get('technical_data', {})
                            fundamental_data = cached_analysis.get('fundamental_data', {})
                            groq_analysis = cached_analysis.get('groq_analysis', {})
                            gemini_analysis = cached_analysis.get('gemini_analysis', {})
                            recommendation = cached_analysis.get('recommendation', {})

                            logger.info(f"Using cached analysis for {symbol}")
                        else:
                            # Perform fresh analysis
                            # Get technical analysis
                            technical_data = self.technical_analyzer.analyze_stock(symbol_with_suffix)
                            if not technical_data:
                                continue
                            
                            fundamental_data = {}
                            if fundamental_enabled:
                                fundamental_data = self.fundamental_analyzer.get_financial_data(symbol_with_suffix)
                             
                            # Get comprehensive Groq AI analysis using the analyzed news
                            groq_analysis = self.groq_analyzer.get_comprehensive_stock_analysis(
                                symbol, technical_data, fundamental_data, all_news
                            )
                            
                            # Get Gemini AI analysis
                            gemini_analysis = None
                            if self.gemini_analyzer.initialized:
                                gemini_analysis = self.gemini_analyzer.analyze_stock_comprehensive(
                                    symbol, technical_data, fundamental_data, st.session_state.news_articles, groq_analysis
                                )
                             
                            # Generate AI recommendation
                            # Calculate news sentiment for this stock
                            news_sentiment = 0.5  # Default neutral
                            if all_news:
                                news_sentiment = self.news_analyzer.analyze_news_sentiment(all_news)
                             
                            recommendation = self.ai_engine.generate_ai_recommendation(
                                technical_data, technical_data, news_sentiment, [], groq_analysis, gemini_analysis,
                                use_fundamental=fundamental_enabled
                            )
                             
                            # Cache the analysis
                            analysis_data = {
                                'technical_data': technical_data,
                                'fundamental_data': fundamental_data,
                                'groq_analysis': groq_analysis,
                                'gemini_analysis': gemini_analysis,
                                'recommendation': recommendation
                            }
                            cache_manager.cache_stock_analysis(symbol, analysis_data)
                        
                        # Include BUY and SELL recommendations; skip HOLD (no clear edge)
                        action = recommendation.get('action', '')
                        if action in ('BUY', 'SELL'):
                            # Get company name from groq analysis or use symbol as fallback
                            company_name = ''
                            if groq_analysis and groq_analysis.get('status') == 'success':
                                company_name = groq_analysis.get('company_name', '')

                            if action == 'BUY':
                                # Generate standard swing trading plan for long positions
                                swing_strategy = st.session_state.swing_strategy
                                swing_plan = swing_strategy.generate_swing_trading_plan({
                                    'symbol': symbol,
                                    'company_name': company_name,
                                    'current_price': technical_data.get('current_price', 0),
                                    'confidence': recommendation['confidence'],
                                    'target_price': recommendation['target_price'],
                                    'stop_loss': recommendation['stop_loss'],
                                    'technical_data': technical_data,
                                    'groq_analysis': groq_analysis
                                })
                                validation = swing_strategy.validate_swing_opportunity({
                                    'symbol': symbol,
                                    'current_price': technical_data.get('current_price', 0),
                                    'confidence': recommendation['confidence'],
                                    'technical_data': technical_data,
                                    'groq_analysis': groq_analysis
                                })
                            else:  # SELL
                                # For SELL signals, swing plan targets the downside
                                swing_plan = {
                                    'direction': 'SHORT',
                                    'entry': technical_data.get('current_price', 0),
                                    'target': recommendation['target_price'],
                                    'stop_loss': recommendation['stop_loss'],
                                    'risk_reward': round(
                                        (technical_data.get('current_price', 0) - recommendation['target_price']) /
                                        max(recommendation['stop_loss'] - technical_data.get('current_price', 0), 0.01),
                                        2
                                    )
                                }
                                validation = {'valid': True, 'reason': 'Bearish signal confirmed by AI engine'}

                            rec_data = {
                                'symbol': symbol,
                                'current_price': technical_data.get('current_price', 0),
                                'recommendation': action,
                                'confidence': recommendation['confidence'],
                                'target_price': recommendation['target_price'],
                                'stop_loss': recommendation['stop_loss'],
                                'reasoning': recommendation['reasoning'],
                                'technical_data': technical_data,
                                'fundamental_data': fundamental_data,
                                'groq_analysis': groq_analysis,
                                'gemini_analysis': gemini_analysis,
                                'swing_plan': swing_plan,
                                'swing_validation': validation
                            }
                            news_recommendations.append(rec_data)
                            logger.info(f"Added {action} recommendation for {symbol}")
                        else:
                            logger.info(f"Skipped {symbol} - HOLD signal (no directional edge)")
                        
                        # Update progress
                        progress_bar.progress((i + 1) / total_stocks)
                        
                    except Exception as e:
                        logger.error(f"Error analyzing news stock {symbol}: {str(e)}")
                        continue
                
                # Set final recommendations
                st.session_state.recommendations = news_recommendations
                st.session_state.last_analysis_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Save to database if available
                self.save_recommendations()
                
                # Auto-save recommendations and swing strategies
                self._auto_save_recommendations()
                self._auto_save_buy_recommendations()  # Specifically save BUY recommendations date-wise
                self._auto_save_swing_strategies()
                
                buy_count  = sum(1 for r in news_recommendations if r.get('recommendation') == 'BUY')
                sell_count = sum(1 for r in news_recommendations if r.get('recommendation') == 'SELL')
                st.success(f"✅ Analysis complete! {buy_count} BUY 📈 + {sell_count} SELL 📉 signals generated. Data auto-saved for 7 days.")
                
        except Exception as e:
            st.error(f"❌ Error analyzing market: {str(e)}")
        finally:
            st.session_state.analysis_in_progress = False
    
    def analyze_manual_stock(self, symbol: str):
        """Analyze a manually entered stock with fallback to EQUITY_L.csv for symbol lookup."""
        with st.spinner(f"🔍 Analyzing {symbol}..."):
            try:
                # Try with the provided symbol first
                symbol_with_suffix = f"{symbol}.NS"
                company_name = None
                
                # Get technical analysis with the original symbol
                technical_data = self.technical_analyzer.analyze_stock(symbol_with_suffix)
                
                # If no technical data, try with company name lookup from EQUITY_L.csv
                if not technical_data or not technical_data.get('current_price'):
                    # Try to find the company name from the symbol
                    stock_info = get_stock_data(symbol)
                    if stock_info and stock_info.get('company_name'):
                        company_name = stock_info['company_name']
                        st.info(f"Found company name: {company_name}")
                        
                        # Try again with the found symbol
                        symbol = stock_info['symbol']
                        symbol_with_suffix = f"{symbol}.NS"
                        technical_data = self.technical_analyzer.analyze_stock(symbol_with_suffix)
                
                # If still no data, show error and return
                if not technical_data or not technical_data.get('current_price'):
                    st.error(f"❌ No data available for {symbol}.")
                    
                    # Try to find similar symbols in EQUITY_L.csv
                    similar_symbols = []
                    try:
                        from utils.stock_utils import load_equity_data
                        df = load_equity_data()
                        if not df.empty:
                            matches = df[df['SYMBOL'].str.contains(symbol, case=False, na=False)]
                            if not matches.empty:
                                similar_symbols = matches['SYMBOL'].tolist()
                    except Exception as e:
                        logger.error(f"Error finding similar symbols: {str(e)}")
                    
                    if similar_symbols:
                        st.warning(f"Did you mean one of these? {', '.join(similar_symbols[:5])}")
                    return
                
                # Get fundamental analysis
                fundamental_enabled = not st.session_state.fundamental_analysis_disabled
                fundamental_data = {}
                if fundamental_enabled:
                    fundamental_data = self.fundamental_analyzer.get_financial_data(symbol_with_suffix)
                
                # If fundamental data is missing, try to enhance it with our utility
                if not fundamental_data or not fundamental_data.get('company_name'):
                    stock_info = get_stock_data(symbol, company_name)
                    if stock_info:
                        if not fundamental_data:
                            fundamental_data = {}
                        fundamental_data.update({
                            'company_name': stock_info.get('company_name', symbol),
                            'sector': stock_info.get('sector', ''),
                            'market_cap': stock_info.get('market_cap'),
                            'pe_ratio': stock_info.get('pe_ratio')
                        })
                
                # Get news articles for this stock
                news_articles = []
                search_terms = [symbol]
                if company_name:
                    search_terms.extend(company_name.split()[:3])  # First few words of company name
                
                for article in st.session_state.news_articles:
                    article_text = (article.get('title', '') + ' ' + article.get('description', '')).lower()
                    if any(term.lower() in article_text for term in search_terms):
                        news_articles.append(article)
                
                # Get comprehensive Groq AI analysis
                groq_analysis = self.groq_analyzer.get_comprehensive_stock_analysis(
                    symbol, technical_data, fundamental_data, news_articles
                )
                
                # Get Gemini AI analysis if available
                gemini_analysis = None
                if self.gemini_analyzer.initialized:
                    gemini_analysis = self.gemini_analyzer.analyze_stock_comprehensive(
                        symbol, technical_data, fundamental_data, news_articles, groq_analysis
                    )
                
                # Generate AI recommendation
                news_sentiment = 0.5  # Default neutral
                if news_articles:
                    news_sentiment = self.news_analyzer.analyze_news_sentiment(news_articles)
                
                recommendation = self.ai_engine.generate_ai_recommendation(
                    technical_data, technical_data, news_sentiment, [], groq_analysis, gemini_analysis,
                    use_fundamental=fundamental_enabled
                )
                
                # Store result
                st.session_state.manual_analysis_result = {
                    'symbol': symbol,
                    'recommendation': recommendation,
                    'technical_data': technical_data,
                    'fundamental_data': fundamental_data,
                    'news_articles': news_articles,
                    'groq_analysis': groq_analysis,
                    'gemini_analysis': gemini_analysis
                }
                
                # Auto-save BUY recommendations if it's a BUY
                if recommendation.get('action', '').upper() == 'BUY':
                    # Create a single recommendation list for saving
                    single_recommendation = [{
                        'symbol': symbol,
                        'company_name': technical_data.get('company_name', company_name or symbol),
                        'current_price': technical_data.get('current_price', 0),
                        'recommendation': 'BUY',
                        'action': 'BUY',
                        'confidence': recommendation.get('confidence', 0),
                        'target_price': recommendation.get('target_price', 0),
                        'stop_loss': recommendation.get('stop_loss', 0),
                        'reasoning': recommendation.get('reasoning', ''),
                        'technical_data': technical_data,
                        'fundamental_data': fundamental_data,
                        'groq_analysis': groq_analysis,
                        'gemini_analysis': gemini_analysis
                    }]
                    
                    # Save BUY recommendation date-wise
                    self._auto_save_buy_recommendations_for_manual(single_recommendation)
                
                st.success(f"✅ Analysis complete for {symbol} ({company_name or 'N/A'})")
                
            except Exception as e:
                st.error(f"❌ Error analyzing {symbol}: {str(e)}")
                logger.exception(f"Error in analyze_manual_stock for {symbol}")
    
    def display_manual_analysis_result(self):
        """Display manual analysis result."""
        result = st.session_state.manual_analysis_result
        symbol = result['symbol']
        recommendation = result['recommendation']

        st.subheader(f"📊 Analysis Results for {symbol}")

        # Recommendation
        rec_class = f"recommendation-{recommendation['action'].lower()}"
        rec_emoji = "📈" if recommendation['action'] == "BUY" else "📉" if recommendation['action'] == "SELL" else "➡️"

        st.markdown(f"""
        <div class="metric-card">
            <h3>{rec_emoji} {recommendation['action']}</h3>
            <p><strong>Confidence:</strong> {recommendation['confidence']:.1f}%</p>
            <p><strong>Current Price:</strong> ₹{result['technical_data'].get('current_price', 0):.2f}</p>
            <p><strong>Target Price:</strong> ₹{recommendation['target_price']:.2f}</p>
            <p><strong>Stop Loss:</strong> ₹{recommendation['stop_loss']:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

        # Reasoning
        with st.expander("💭 Reasoning"):
            st.markdown(recommendation['reasoning'])

        # Add to watchlist button
        if st.button(f"👀 Add {symbol} to Watchlist", key=f"add_to_watchlist_{symbol}"):
            self.add_to_watchlist({
                'symbol': symbol,
                'company_name': result['technical_data'].get('company_name', symbol),
                'current_price': result['technical_data'].get('current_price', 0),
                'recommendation': recommendation['action'],
                'confidence': recommendation['confidence'],
                'target_price': recommendation.get('target_price', 0),
                'stop_loss': recommendation.get('stop_loss', 0),
                'reasoning': recommendation.get('reasoning', ''),
                'technical_data': result.get('technical_data', {}),
                'fundamental_data': result.get('fundamental_data', {}),
                'groq_analysis': result.get('groq_analysis', {}),
                'gemini_analysis': result.get('gemini_analysis', {}),
            })
            st.success(f"✅ Added {symbol} to watchlist")

    def add_to_watchlist(self, rec: Dict):
        """Add recommendation to watchlist."""
        try:
            symbol = rec.get('symbol')
            if not symbol:
                st.error("Invalid recommendation data")
                return

            # Check if already in watchlist
            for item in st.session_state.watchlist:
                if item.get('symbol') == symbol:
                    st.warning(f"{symbol} is already in watchlist")
                    return

            # Add to watchlist with full recommendation payload
            watchlist_item = {
                'symbol': symbol,
                'company_name': rec.get('company_name', ''),
                'entry_price': rec.get('current_price', 0),
                'current_price': rec.get('current_price', 0),
                'target_price': rec.get('target_price', 0),
                'stop_loss': rec.get('stop_loss', 0),
                'recommendation': rec.get('recommendation', 'HOLD'),
                'confidence': rec.get('confidence', 0),
                'reasoning': rec.get('reasoning', ''),
                'added_date': datetime.now().isoformat(),
                'status': 'ACTIVE',
                # Store full recommendation so watchlist details match recommendations tab
                'full_recommendation': rec,
            }

            st.session_state.watchlist.append(watchlist_item)
            self._auto_save_watchlist()
        except Exception as e:
            st.error(f"❌ Error adding to watchlist: {str(e)}")

    def analyze_watchlist_stocks(self):
        """Analyze watchlist stocks for learning."""
        if not st.session_state.watchlist:
            st.error("No stocks in watchlist to analyze")
            return

        with st.spinner("🧠 Learning from watchlist performance..."):
            try:
                analyzed_count = 0
                total_count = len(st.session_state.watchlist)

                progress_bar = st.progress(0)

                for i, item in enumerate(st.session_state.watchlist):
                    symbol = item.get('symbol')
                    if not symbol:
                        continue
                    
                    try:
                        symbol_with_suffix = f"{symbol}.NS"
                        
                        # Get current technical analysis
                        technical_data = self.technical_analyzer.analyze_stock(symbol_with_suffix)
                        if not technical_data:
                            continue
                        
                        # Get fundamental analysis
                        fundamental_data = self.fundamental_analyzer.get_financial_data(symbol_with_suffix)
                        
                        # Get news articles for this stock
                        news_articles = []
                        for article in st.session_state.news_articles:
                            if symbol.lower() in article.get('title', '').lower() or symbol.lower() in article.get('description', '').lower():
                                news_articles.append(article)
                        
                        # Get comprehensive Groq AI analysis
                        groq_analysis = self.groq_analyzer.get_comprehensive_stock_analysis(
                            symbol, technical_data, fundamental_data, news_articles
                        )
                        
                        # Get Gemini AI learning analysis
                        gemini_analysis = None
                        if self.gemini_analyzer.initialized:
                            gemini_analysis = self.gemini_analyzer.analyze_stock_for_learning(
                                symbol, technical_data, fundamental_data, news_articles, groq_analysis, item
                            )
                        
                        # Calculate performance
                        entry_price = item.get('entry_price', 0)
                        current_price = technical_data.get('current_price', 0)
                        performance_pct = 0
                        if entry_price > 0 and current_price > 0:
                            performance_pct = ((current_price - entry_price) / entry_price) * 100
                        
                        # Update watchlist item
                        item.update({
                            'current_price': current_price,
                            'performance_pct': performance_pct,
                            'last_learning_analysis': datetime.now().isoformat(),
                            'learning_insights': gemini_analysis.get('analysis', {}) if gemini_analysis else {}
                        })
                        
                        analyzed_count += 1
                        progress_bar.progress((i + 1) / total_count)
                        
                    except Exception as e:
                        logger.error(f"Error analyzing watchlist stock {symbol}: {str(e)}")
                        continue
                
                st.success(f"✅ Learned from {analyzed_count}/{total_count} watchlist stocks")
                
            except Exception as e:
                st.error(f"❌ Error in watchlist learning analysis: {str(e)}")
    
    def analyze_swing_performance(self):
        """Analyze swing trading performance and adjust parameters."""
        try:
            with st.spinner("📊 Analyzing swing trading performance..."):
                # Get all swing strategies from data persistence
                data_persistence = st.session_state.data_persistence
                all_swing_strategies = data_persistence.get_swing_strategies()
                
                if not all_swing_strategies:
                    st.warning("No swing strategies found to analyze")
                    return
                
                # Flatten all strategies from all dates
                all_strategies = []
                for date_str, strategies in all_swing_strategies.items():
                    all_strategies.extend(strategies)
                
                # Analyze performance
                performance_tracker = st.session_state.swing_performance_tracker
                analysis_results = performance_tracker.analyze_swing_performance(all_strategies)
                
                # Display results
                self.display_swing_performance_results(analysis_results)
                
                # Update swing strategy with new parameters
                adaptive_params = performance_tracker.get_adaptive_parameters()
                st.session_state.swing_strategy = SwingTradingStrategy(adaptive_parameters=adaptive_params)
                
                st.success("✅ Swing trading parameters updated based on performance analysis!")
                
        except Exception as e:
            st.error(f"❌ Error analyzing swing performance: {str(e)}")
    
    def display_swing_performance_results(self, results: Dict):
        """Display swing trading performance analysis results."""
        try:
            st.subheader("📊 Swing Trading Performance Analysis")
            
            # Performance metrics
            metrics = results.get('performance_metrics', {})
            if metrics:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Trades", metrics.get('total_trades', 0))
                
                with col2:
                    win_rate = metrics.get('win_rate', 0)
                    st.metric("Win Rate", f"{win_rate:.1f}%")
                
                with col3:
                    avg_return = metrics.get('avg_return', 0)
                    st.metric("Avg Return", f"{avg_return:.2f}%")
                
                with col4:
                    current_capital = metrics.get('current_capital', 100000)
                    st.metric("Current Capital", f"₹{current_capital:,.0f}")
                
                # Additional metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    profit_factor = metrics.get('profit_factor', 0)
                    st.metric("Profit Factor", f"{profit_factor:.2f}")
                
                with col2:
                    sharpe_ratio = metrics.get('sharpe_ratio', 0)
                    st.metric("Sharpe Ratio", f"{sharpe_ratio:.2f}")
                
                with col3:
                    max_drawdown = metrics.get('max_drawdown', 0)
                    st.metric("Max Drawdown", f"{max_drawdown:.1f}%")
            
            # Parameter adjustments
            adjustments = results.get('adjustments_made', [])
            if adjustments:
                st.subheader("🔧 Parameter Adjustments Made")
                for adjustment in adjustments:
                    st.info(f"• {adjustment}")
            else:
                st.info("No parameter adjustments needed based on current performance")
            
            # Updated parameters
            updated_params = results.get('updated_parameters', {})
            if updated_params:
                st.subheader("⚙️ Current Adaptive Parameters")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Stop Loss", f"{updated_params.get('stop_loss_percentage', 0)*100:.1f}%")
                    st.metric("Take Profit", f"{updated_params.get('take_profit_percentage', 0)*100:.1f}%")
                
                with col2:
                    st.metric("Position Size", f"{updated_params.get('position_size_percentage', 0)*100:.1f}%")
                    st.metric("Confidence Threshold", f"{updated_params.get('confidence_threshold', 0):.1f}%")
                
                with col3:
                    st.metric("Risk-Reward Ratio", f"{updated_params.get('risk_reward_ratio', 0):.1f}:1")
                    st.metric("Max Drawdown", f"{updated_params.get('max_drawdown', 0)*100:.1f}%")
            
            # Strategy status summary
            st.subheader("📈 Strategy Status Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Completed Strategies", results.get('completed_strategies', 0))
            
            with col2:
                st.metric("Active Strategies", results.get('active_strategies', 0))
            
            with col3:
                st.metric("Expired Strategies", results.get('expired_strategies', 0))
                
        except Exception as e:
            st.error(f"Error displaying performance results: {str(e)}")
    
    def display_current_adaptive_parameters(self):
        """Display current adaptive parameters in swing tab."""
        try:
            performance_tracker = st.session_state.swing_performance_tracker
            adaptive_params = performance_tracker.get_adaptive_parameters()
            performance_summary = performance_tracker.get_performance_summary()
            
            st.subheader("⚙️ Current Adaptive Parameters (Realistic 7-Day Targets)")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                stop_loss = adaptive_params.get('stop_loss_percentage', 0)*100
                st.metric(
                    "Stop Loss", 
                    f"{stop_loss:.1f}%",
                    help=f"Realistic stop loss for 7-day swing trading (2-5% range)"
                )
            
            with col2:
                take_profit = adaptive_params.get('take_profit_percentage', 0)*100
                st.metric(
                    "Take Profit", 
                    f"{take_profit:.1f}%",
                    help=f"Realistic target for 7-day swing trading (1.5-3% range)"
                )
            
            with col3:
                position_size = adaptive_params.get('position_size_percentage', 0)*100
                st.metric(
                    "Position Size", 
                    f"{position_size:.1f}%",
                    help="Maximum position size per trade (5-15% range)"
                )
            
            with col4:
                confidence = adaptive_params.get('confidence_threshold', 0)
                st.metric(
                    "Confidence Threshold", 
                    f"{confidence:.1f}%",
                    help="Minimum confidence required for trades (50-75% range)"
                )
            
            # Show realistic expectations
            st.info(f"🎯 **Realistic 7-Day Swing Targets:** Stop Loss: {stop_loss:.1f}%, Take Profit: {take_profit:.1f}% (These are achievable targets for 7-day swing trading)")
            
            # Performance summary
            metrics = performance_summary.get('performance_metrics', {})
            if metrics and metrics.get('total_trades', 0) > 0:
                st.subheader("📊 Performance Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Trades", metrics.get('total_trades', 0))
                
                with col2:
                    win_rate = metrics.get('win_rate', 0)
                    st.metric("Win Rate", f"{win_rate:.1f}%")
                
                with col3:
                    current_capital = metrics.get('current_capital', 100000)
                    st.metric("Current Capital", f"₹{current_capital:,.0f}")
                
                with col4:
                    last_updated = adaptive_params.get('last_updated', 'Never')
                    if last_updated != 'Never':
                        try:
                            last_update_date = datetime.fromisoformat(last_updated)
                            last_updated = last_update_date.strftime('%Y-%m-%d %H:%M')
                        except:
                            pass
                    st.metric("Last Updated", last_updated)
            else:
                st.info("No performance data available yet. Run performance analysis after completing some trades.")
                
        except Exception as e:
            st.error(f"Error displaying adaptive parameters: {str(e)}")
    
    def update_watchlist_prices(self):
        """Update watchlist prices."""
        if not st.session_state.watchlist:
            st.error("No stocks in watchlist to update")
            return
        
        with st.spinner("🔄 Updating watchlist prices..."):
            try:
                updated_count = 0
                total_count = len(st.session_state.watchlist)
                
                progress_bar = st.progress(0)
                
                for i, item in enumerate(st.session_state.watchlist):
                    symbol = item.get('symbol')
                    if symbol:
                        try:
                            symbol_with_suffix = f"{symbol}.NS"
                            ticker = yf.Ticker(symbol_with_suffix)
                            hist = ticker.history(period="1d")
                            
                            if not hist.empty:
                                current_price = hist['Close'].iloc[-1]
                                item['current_price'] = float(current_price)
                                item['last_updated'] = datetime.now().isoformat()
                                updated_count += 1
                            
                            progress_bar.progress((i + 1) / total_count)
                            
                        except Exception as e:
                            logger.error(f"Error updating price for {symbol}: {str(e)}")
                
                # Auto-save updated watchlist
                self._auto_save_watchlist()
                
                st.success(f"✅ Updated prices for {updated_count}/{total_count} stocks")
                
            except Exception as e:
                st.error(f"❌ Error updating watchlist prices: {str(e)}")
    
    def update_watchlist_item(self, symbol: str):
        """Update a specific watchlist item."""
        st.info(f"Updating {symbol}...")
        # Implementation for updating individual items
        st.success(f"Updated {symbol}")
    
    def show_recommendation_details(self, rec: Dict):
        """Show detailed recommendation analysis."""
        st.subheader(f"📊 Detailed Analysis: {rec.get('symbol', 'N/A')}")
        
        # Technical Analysis
        with st.expander("📈 Technical Analysis"):
            technical_data = rec.get('technical_data', {})
            if technical_data:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("RSI", f"{technical_data.get('rsi', 0):.2f}")
                    st.metric("MACD", f"{technical_data.get('macd', 0):.2f}")
                with col2:
                    st.metric("SMA 20", f"{technical_data.get('sma_20', 0):.2f}")
                    st.metric("SMA 50", f"{technical_data.get('sma_50', 0):.2f}")
                with col3:
                    st.metric("Volume Ratio", f"{technical_data.get('volume_ratio', 0):.2f}")
                    st.metric("Technical Score", f"{technical_data.get('technical_score', 0):.2f}")
        
        # Fundamental Analysis
        with st.expander("📊 Fundamental Analysis"):
            fundamental_data = rec.get('fundamental_data', {})
            if fundamental_data:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("P/E Ratio", f"{fundamental_data.get('pe_ratio', 0):.2f}")
                    st.metric("P/B Ratio", f"{fundamental_data.get('pb_ratio', 0):.2f}")
                with col2:
                    st.metric("ROE", f"{fundamental_data.get('roe', 0):.2f}")
                    st.metric("ROA", f"{fundamental_data.get('roa', 0):.2f}")
                with col3:
                    st.metric("Debt/Equity", f"{fundamental_data.get('debt_equity', 0):.2f}")
                    st.metric("Fundamental Score", f"{fundamental_data.get('score', 0):.2f}")
        
        # Groq AI Analysis
        with st.expander("🤖 Groq AI Comprehensive Analysis"):
            groq_analysis = rec.get('groq_analysis', {})
            if groq_analysis and groq_analysis.get('status') == 'success':
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Overall Score", f"{groq_analysis.get('overall_score', 0):.2f}")
                    st.metric("Recommendation", groq_analysis.get('recommendation', 'HOLD'))
                    st.metric("Confidence", f"{groq_analysis.get('confidence', 0):.1%}")
                with col2:
                    st.metric("Risk Assessment", groq_analysis.get('risk_assessment', 'MEDIUM'))
                    st.metric("Time Horizon", groq_analysis.get('time_horizon', 'MEDIUM'))
                    st.metric("Price Target", groq_analysis.get('price_target', 'N/A'))
                
                st.markdown(f"**Reasoning:** {groq_analysis.get('reasoning', 'No reasoning provided')}")
                st.markdown(f"**Key Factors:** {', '.join(groq_analysis.get('key_factors', []))}")
                st.markdown(f"**Stop Loss:** {groq_analysis.get('stop_loss', 'N/A')}")
                
                # Detailed insights
                with st.expander("📊 Detailed Insights"):
                    st.markdown(f"**Technical Insights:** {groq_analysis.get('technical_insights', 'No technical insights')}")
                    st.markdown(f"**Fundamental Insights:** {groq_analysis.get('fundamental_insights', 'No fundamental insights')}")
                    st.markdown(f"**Sentiment Insights:** {groq_analysis.get('sentiment_insights', 'No sentiment insights')}")
                    st.markdown(f"**Market Outlook:** {groq_analysis.get('market_outlook', 'No market outlook')}")
            else:
                st.info("No Groq AI analysis available")
        
        # Gemini AI Analysis
        with st.expander("🧠 Gemini AI Analysis"):
            gemini_analysis = rec.get('gemini_analysis', {})
            if gemini_analysis and gemini_analysis.get('status') == 'success':
                analysis_data = gemini_analysis.get('analysis', {})
                st.metric("Overall Score", f"{analysis_data.get('overall_score', 0):.2f}")
                st.metric("Confidence", f"{analysis_data.get('confidence', 0):.1%}")
                st.markdown(f"**Recommendation:** {analysis_data.get('recommendation', 'N/A')}")
                st.markdown(f"**Risk Assessment:** {analysis_data.get('risk_assessment', 'N/A')}")
            else:
                st.info("No Gemini AI analysis available")
    
    def save_recommendations(self):
        """Save recommendations to database."""
        try:
            if not st.session_state.recommendations:
                st.warning("No recommendations to save")
                return
            
            # Save to local database if available
            if hasattr(self, 'recommendation_db') and self.recommendation_db:
                if self.recommendation_db.save_recommendations(st.session_state.recommendations, 'enhanced'):
                    st.success("✅ Recommendations saved to local database")
                else:
                    st.warning("⚠️ Failed to save to local database")
            
            # Save to Firebase if available
            if st.session_state.firebase_available and hasattr(self, 'firebase_sync'):
                if self.firebase_sync.sync_recommendations(st.session_state.recommendations, "enhanced"):
                    st.success("✅ Recommendations synced to Firebase")
                else:
                    st.warning("⚠️ Failed to sync to Firebase")
            
        except Exception as e:
            st.error(f"❌ Error saving recommendations: {str(e)}")

def main():
    """Main function to run the Streamlit app."""
    try:
        app = StreamlitTradingApp()
        app.run()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()