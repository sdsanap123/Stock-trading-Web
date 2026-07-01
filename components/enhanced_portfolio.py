"""
Enhanced Portfolio Management
Handles portfolio operations with AI-powered analysis.
"""
import json
import logging
import os
import time
import uuid
from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import streamlit as st
import yfinance as yf

from .stock_analyzer import StockAnalyzer
from .firebase_integration import FirebaseSync

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPortfolio:
    """Enhanced portfolio management with AI analysis."""
    
    def __init__(self, data_dir: str = "saved_data"):
        """Initialize the enhanced portfolio manager."""
        self.data_dir = data_dir
        self.portfolio_file = os.path.join(data_dir, "portfolio_enhanced.json")
        self.analyzer = StockAnalyzer()
        
        # Initialize Firebase sync
        self.firebase_sync = FirebaseSync()
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize session state with empty portfolio
        if 'portfolio' not in st.session_state:
            st.session_state.portfolio = []
        
        # Initialize edit state
        st.session_state.setdefault('show_edit_form', False)
        st.session_state.setdefault('show_delete_confirm', False)
        
        # Set user ID for Firebase (using session ID or generated ID)
        if 'user_id' not in st.session_state:
            # Generate a simple user ID based on session or use existing
            if 'session_id' in st.session_state:
                st.session_state.user_id = st.session_state.session_id
            else:
                # Generate a unique user ID
                import hashlib
                import time
                user_string = f"portfolio_user_{int(time.time())}_{hash(str(st.session_state))}"
                st.session_state.user_id = hashlib.md5(user_string.encode()).hexdigest()[:16]
        
        # Set user ID in Firebase sync
        self.firebase_sync.set_user_id(st.session_state.user_id)
        
        # Load existing portfolio (prioritizes cloud storage)
        if not st.session_state.get('portfolio_initialized', False):
            self._load_portfolio()
            st.session_state.portfolio_initialized = True

    def _load_portfolio(self) -> None:
        """
        Load portfolio from Firebase cloud storage (primary), session state (secondary), or file (fallback).
        Priority: Firebase > Session State > Local File
        """
        try:
            # First, try to load from Firebase cloud storage (primary)
            firebase_portfolio = self.firebase_sync.load_portfolio()
            if firebase_portfolio is not None:
                st.session_state.portfolio = firebase_portfolio
                st.session_state.portfolio_data = firebase_portfolio
                st.session_state.portfolio_last_saved = datetime.now().isoformat()
                st.session_state.portfolio_source = "firebase"
                logger.info(f"Loaded portfolio from Firebase with {len(firebase_portfolio)} items")
                return
            
            # Second, try to load from session state (secondary)
            if 'portfolio_data' in st.session_state:
                st.session_state.portfolio = st.session_state.portfolio_data
                st.session_state.portfolio_source = "session"
                logger.info(f"Loaded portfolio from session state with {len(st.session_state.portfolio)} items")
                return
            
            # Third, try to load from file (fallback for local development)
            if os.path.exists(self.portfolio_file):
                try:
                    with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                        portfolio_data = json.load(f)
                    
                    # Validate the loaded data
                    if isinstance(portfolio_data, list):
                        st.session_state.portfolio = portfolio_data
                        # Also save to session state and Firebase for future use
                        st.session_state.portfolio_data = portfolio_data
                        st.session_state.portfolio_last_saved = datetime.now().isoformat()
                        st.session_state.portfolio_source = "file"
                        
                        # Sync to Firebase for future cloud access
                        self.firebase_sync.sync_portfolio(portfolio_data)
                        
                        logger.info(f"Loaded portfolio from file with {len(portfolio_data)} items and synced to cloud")
                    else:
                        logger.error("Portfolio file is not in expected format")
                        st.session_state.portfolio = []
                        self._save_portfolio()
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding portfolio file: {str(e)}")
                    st.warning("Portfolio file is corrupted. Starting with an empty portfolio.")
                    st.session_state.portfolio = []
                    self._save_portfolio()
                    
            else:
                # No file exists, start with empty portfolio
                st.session_state.portfolio = []
                st.session_state.portfolio_source = "new"
                self._save_portfolio()
                logger.info("No existing portfolio found, starting with empty portfolio")
                
        except Exception as e:
            logger.error(f"Unexpected error loading portfolio: {str(e)}")
            st.session_state.portfolio = []
            st.session_state.portfolio_source = "error"
            self._save_portfolio()

    def _save_portfolio(self) -> None:
        """
        Save portfolio to Firebase cloud storage (primary), session state (secondary), and file (backup).
        Priority: Firebase > Session State > Local File
        """
        try:
            # Ensure we have a portfolio to save
            if 'portfolio' not in st.session_state:
                st.session_state.portfolio = []
            
            # Prepare the data to be saved
            data_to_save = []
            for item in st.session_state.portfolio:
                # Only save essential fields
                if isinstance(item, dict) and 'symbol' in item and 'quantity' in item and 'buy_price' in item:
                    data_to_save.append({
                        'symbol': item['symbol'],
                        'quantity': item['quantity'],
                        'buy_price': item['buy_price'],
                        'buy_date': item.get('buy_date', ''),
                        'notes': item.get('notes', '')
                    })
            
            # Update session state (secondary storage)
            st.session_state.portfolio_data = data_to_save
            st.session_state.portfolio_last_saved = datetime.now().isoformat()
            
            # Sync to Firebase cloud storage (primary storage)
            firebase_sync_success = self.firebase_sync.sync_portfolio(data_to_save)
            if firebase_sync_success:
                st.session_state.portfolio_sync_status = "synced"
                logger.info(f"Portfolio synced to Firebase with {len(data_to_save)} items")
            else:
                st.session_state.portfolio_sync_status = "sync_failed"
                logger.warning("Failed to sync portfolio to Firebase")
            
            # Try to save to file as backup (works locally, may not persist on cloud)
            try:
                # Ensure the directory exists
                os.makedirs(os.path.dirname(self.portfolio_file), exist_ok=True)
                
                # Create a backup of the current file if it exists
                backup_file = None
                if os.path.exists(self.portfolio_file):
                    backup_file = f"{self.portfolio_file}.bak"
                    try:
                        import shutil
                        shutil.copy2(self.portfolio_file, backup_file)
                    except Exception as e:
                        logger.warning(f"Could not create backup: {str(e)}")
                
                # Save to a temporary file first
                temp_file = f"{self.portfolio_file}.tmp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data_to_save, f, indent=2, ensure_ascii=False, default=str)
                    f.flush()
                    os.fsync(f.fileno())
                
                # Replace the old file with the new one
                if os.path.exists(self.portfolio_file):
                    os.replace(temp_file, self.portfolio_file)
                else:
                    os.rename(temp_file, self.portfolio_file)
                
                # If we got here, the save was successful, we can remove the backup
                if backup_file and os.path.exists(backup_file):
                    try:
                        os.remove(backup_file)
                    except Exception as e:
                        logger.warning(f"Could not remove backup file: {str(e)}")
                
                logger.info(f"Successfully saved portfolio with {len(data_to_save)} items to file and session state")
                
            except Exception as file_error:
                # File save failed, but session state and Firebase save succeeded
                logger.warning(f"File save failed (expected on cloud): {str(file_error)}")
                logger.info(f"Portfolio saved to session state and Firebase with {len(data_to_save)} items")
                
        except Exception as e:
            logger.error(f"Error saving portfolio: {str(e)}")
            st.error(f"Failed to save portfolio: {str(e)}")
            # Re-raise to allow calling code to handle the error if needed
            raise
    
    def _get_stock_data(self, symbol_or_company: str) -> tuple[Optional[float], Optional[dict], str]:
        """
        Get stock data from yfinance with symbol validation using EQUITY_L.csv.
        
        Args:
            symbol_or_company: Stock symbol (e.g., 'RELIANCE.NS') or company name (e.g., 'Bajaj Finance Limited')
            
        Returns:
            tuple: (current_price, stock_info, resolved_symbol) or (None, None, None) if not found
        """
        from utils.stock_utils import find_stock_symbol, load_equity_data
        
        # Clean the input
        symbol_or_company = str(symbol_or_company).strip()
        if not symbol_or_company:
            return None, None, None
            
        # Remove any existing .NS suffix to standardize
        clean_input = symbol_or_company.upper().replace('.NS', '').strip()
        
        # Specific symbol mappings for common mismatches
        symbol_mappings = {
            'DEEPAK NITRITE': 'DEEPAKNTR',
            'DEEPAK NITRT': 'DEEPAKNTR',
            'TCS LTD': 'TCS',
            'TCS LIMITED': 'TCS',
            'NIFTY BEES': 'NIFTYBEES',
            'NIFTYBEES ETF': 'NIFTYBEES',
            'ESCORTS LTD.': 'ESCORTS',
            'ESCORTS LTD': 'ESCORTS',
            'ESCORT': 'ESCORTS',
            'JK TYRE IND': 'JKTYRES',
            'JK TYRE': 'JKTYRES',
            'J K TYRE': 'JKTYRES',
            'SANWAR AG OI (BSE INDONEXT)': 'SANWARIA',
            'SANWAR AG': 'SANWARIA',
            'YAARII DIGITAL LTD.': 'YAARII',
            'YAARII DIGITAL': 'YAARII',
        }
        
        # Check if input matches any of our specific mappings
        if clean_input in symbol_mappings:
            symbol = symbol_mappings[clean_input]
            return self._fetch_yfinance_data(symbol)
        
        # Try to find the symbol in the database
        try:
            equity_df = load_equity_data()
            if not equity_df.empty:
                # Look for exact symbol match (case-insensitive)
                symbol_match = equity_df[equity_df['SYMBOL'].str.upper() == clean_input]
                
                # If no direct symbol match, try company name match
                if symbol_match.empty:
                    # Look for company name match (case-insensitive, partial match)
                    name_matches = equity_df[
                        equity_df['NAME OF COMPANY'].str.upper().str.contains(clean_input, case=False, na=False) |
                        equity_df['NAME OF COMPANY'].str.upper().str.replace('LIMITED', '').str.strip().str.contains(clean_input, case=False, na=False)
                    ]
                    
                    if not name_matches.empty:
                        # Get the first match with the closest name
                        symbol = name_matches.iloc[0]['SYMBOL']
                        return self._fetch_yfinance_data(symbol)
                    
                    # Try fuzzy matching if no direct match found
                    from fuzzywuzzy import fuzz
                    
                    # Get list of all company names
                    companies = equity_df[['SYMBOL', 'NAME OF COMPANY']].drop_duplicates()
                    
                    # Calculate similarity scores
                    companies['score'] = companies['NAME OF COMPANY'].apply(
                        lambda x: fuzz.ratio(clean_input.upper(), str(x).upper())
                    )
                    
                    # Get best match
                    if not companies.empty:
                        best_match = companies.loc[companies['score'].idxmax()]
                        if best_match is not None and best_match['score'] > 70:  # Threshold for fuzzy match
                            return self._fetch_yfinance_data(best_match['SYMBOL'])
                else:
                    # Found exact symbol match
                    symbol = symbol_match.iloc[0]['SYMBOL']
                    return self._fetch_yfinance_data(symbol)
        except Exception as e:
            logger.warning(f"Error looking up symbol in database: {str(e)}")
            
        # Last resort: try the input as-is with .NS suffix
        return self._fetch_yfinance_data(clean_input)
        
    def _fetch_yfinance_data(self, symbol: str) -> tuple[Optional[float], Optional[dict], str]:
        """Helper method to fetch data from yfinance with proper symbol formatting."""
        # Ensure symbol has .NS suffix if not already present and not an index
        if not any(ext in symbol.upper() for ext in ['.NS', '.BO', '.NSEI', '^', '=']):
            symbol = f"{symbol}.NS"
            
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period='1d')
            
            if not hist.empty:
                return float(hist['Close'].iloc[-1]), stock.info, symbol
                
            # If no data, try with .BO (BSE) suffix
            if symbol.endswith('.NS'):
                return self._fetch_yfinance_data(symbol.replace('.NS', '.BO'))
                
        except Exception as e:
            logger.warning(f"Error fetching data for {symbol}: {str(e)}")
            
            # Try with .BO (BSE) suffix if .NS failed
            if symbol.endswith('.NS'):
                return self._fetch_yfinance_data(symbol.replace('.NS', '.BO'))
                
        return None, None, symbol

    def _add_stock(self, symbol: str, quantity: float, buy_price: float, 
                  buy_date: Union[str, date], notes: str = "") -> bool:
        """
        Add a stock to the portfolio with enhanced validation.
        
        Args:
            symbol: Stock symbol or company name (e.g., 'RELIANCE' or 'RELIANCE.NS')
            quantity: Number of shares
            buy_price: Purchase price per share
            buy_date: Purchase date (string or date object)
            notes: Optional notes about the stock
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get stock data and resolve symbol
            current_price, stock_info, resolved_symbol = self._get_stock_data(symbol)
            
            if current_price is None or not resolved_symbol:
                st.error(f"Could not find or fetch data for: {symbol}. Please check the company name/symbol and try again.")
                return False
            
            # Update symbol to the resolved one
            symbol = resolved_symbol
            
            # Convert buy_date to string if it's a date object
            if isinstance(buy_date, date):
                buy_date = buy_date.isoformat()
            
            # Ensure portfolio exists in session state
            if 'portfolio' not in st.session_state:
                st.session_state.portfolio = []
            
            # Validate quantity and price
            if quantity <= 0:
                st.error("Quantity must be greater than 0")
                return False
                
            if buy_price <= 0:
                st.error("Buy price must be greater than 0")
                return False
            
            # Check if stock already exists in portfolio
            if 'portfolio' in st.session_state:
                existing_symbols = [item['symbol'].split('.')[0] for item in st.session_state.portfolio]
                if symbol.split('.')[0] in existing_symbols:
                    st.warning(f"{symbol} is already in your portfolio. Updating existing entry.")
                    # Remove existing entry to replace it
                    st.session_state.portfolio = [
                        item for item in st.session_state.portfolio 
                        if item['symbol'].split('.')[0] != symbol.split('.')[0]
                    ]
            
            # Add to portfolio
            stock_info = {
                'symbol': symbol,
                'quantity': float(quantity),
                'buy_price': float(buy_price),
                'current_price': current_price,
                'buy_date': buy_date,
                'last_updated': datetime.now().isoformat(),
                'notes': str(notes).strip(),
                'id': str(uuid.uuid4())  # Add unique ID for each holding
            }
            
            # Initialize portfolio if it doesn't exist
            if 'portfolio' not in st.session_state:
                st.session_state.portfolio = []
            
            # Add to portfolio
            st.session_state.portfolio.append(stock_info)
            
            # Save to file
            self._save_portfolio()
            
            return True
            
        except Exception as e:
            error_msg = f"Error adding stock: {str(e)}"
            st.error(error_msg)
            logger.exception(error_msg)
            return False
    
    def _update_stock(self, index: int, **updates) -> bool:
        """Update a stock in the portfolio."""
        try:
            if 'portfolio' not in st.session_state or index < 0 or index >= len(st.session_state.portfolio):
                st.error("Invalid stock index")
                return False
                
            stock = st.session_state.portfolio[index]
            
            # Apply updates
            for key, value in updates.items():
                if key in stock:
                    stock[key] = value
            
            # Update current price if symbol changed
            if 'symbol' in updates:
                _, _, current_price = self._get_stock_data(updates['symbol'])
                if current_price is not None:
                    stock['current_price'] = current_price
            
            # Update timestamps
            stock['last_updated'] = datetime.now().isoformat()
            
            # Save the changes
            self._save_portfolio()
            
            # Reset edit state
            for key in ["editing_index", "edit_symbol", "edit_quantity", "edit_buy_price", "show_edit_form"]:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.success("Stock updated successfully!")
            st.rerun()
            return True
            
        except Exception as e:
            error_msg = f"Error updating stock: {str(e)}"
            st.error(error_msg)
            logger.exception(error_msg)
            return False
            return True
            
        except Exception as e:
            error_msg = f"Error removing stock: {str(e)}"
            st.error(error_msg)
            logger.exception(error_msg)
            return False
    
    def _analyze_stock(self, symbol: str) -> Dict:
        """Analyze a stock using the StockAnalyzer."""
        with st.spinner(f"Analyzing {symbol}..."):
            return self.analyzer.analyze_stock(symbol)
    
    def _display_analysis(self, analysis: Dict) -> None:
        """Display stock analysis results."""
        if not analysis or 'error' in analysis:
            st.error(f"Analysis failed: {analysis.get('error', 'Unknown error')}")
            return
        
        # Display overall recommendation
        st.subheader(f"Analysis for {analysis['symbol']}")
        
        # Overall score and recommendation
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Overall Score", f"{analysis['overall_score']}/100")
        with col2:
            # Color code the recommendation
            rec = analysis['recommendation']
            if 'BUY' in rec:
                st.metric("Recommendation", rec, help="Based on technical and fundamental analysis", 
                         delta_color="normal")
            elif 'SELL' in rec:
                st.metric("Recommendation", rec, help="Based on technical and fundamental analysis",
                         delta_color="inverse")
            else:
                st.metric("Recommendation", rec, help="Based on technical and fundamental analysis")
        
        # Score breakdown
        with st.expander("Score Breakdown"):
            st.write(f"- News Sentiment: {analysis['score_breakdown']['news_score']}/100")
            st.write(f"- Technical Analysis: {analysis['score_breakdown']['technical_score']}/100")
            st.write(f"- Fundamental Analysis: {analysis['score_breakdown']['fundamental_score']}/100")
        
        # News Analysis
        with st.expander("📰 News Sentiment Analysis"):
            news = analysis.get('news_analysis', {})
            if news and 'sentiment' in news:
                st.write(f"**Sentiment:** {news['sentiment']} ({news.get('sentiment_score', 0):.2f})")
                st.write(f"Total News Analyzed: {news.get('total_news', 0)}")
                st.write(f"Positive News: {news.get('positive_news', 0)}")
                st.write(f"Negative News: {news.get('negative_news', 0)}")
                
                if news.get('news_samples'):
                    st.subheader("Recent News Headlines")
                    for item in news['news_samples'][:3]:
                        st.write(f"- **{item.get('publisher', '')}**: {item.get('title', '')}")
                        if item.get('link'):
                            st.markdown(f"[Read more]({item['link']})")
                        st.write("---")
            else:
                st.warning("No news analysis available")
        
        # Technical Analysis
        with st.expander("📈 Technical Analysis"):
            tech = analysis.get('technical_analysis', {})
            if tech:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current Price", f"₹{tech.get('current_price', 'N/A'):.2f}")
                    st.metric("RSI (14)", f"{tech.get('rsi', 0):.2f}", 
                             help="Overbought (>70) or Oversold (<30)")
                    st.metric("Volume", f"{tech.get('volume_ratio', 0):.2f}x avg",
                             help="Volume compared to average")
                
                with col2:
                    st.metric("20-day MA", f"₹{tech.get('sma_20', 0):.2f}")
                    st.metric("50-day MA", f"₹{tech.get('sma_50', 0):.2f}")
                    st.metric("200-day MA", f"₹{tech.get('sma_200', 0):.2f}")
                
                if tech.get('signals'):
                    st.subheader("Technical Signals")
                    for signal in tech['signals']:
                        st.write(f"- {signal}")
            else:
                st.warning("No technical analysis available")
        
        # Fundamental Analysis
        with st.expander("📊 Fundamental Analysis"):
            fund = analysis.get('fundamental_analysis', {})
            if fund:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Sector", fund.get('sector', 'N/A'))
                    st.metric("Market Cap", f"₹{fund.get('market_cap', 0)/1e9:.2f}B" if fund.get('market_cap') else 'N/A')
                    st.metric("P/E Ratio", f"{fund.get('pe_ratio', 'N/A')}")
                    st.metric("PEG Ratio", f"{fund.get('peg_ratio', 'N/A')}")
                
                with col2:
                    st.metric("Price/Book", f"{fund.get('price_to_book', 'N/A')}")
                    st.metric("Profit Margin", f"{fund.get('profit_margin', 0)*100:.2f}%" if fund.get('profit_margin') is not None else 'N/A')
                    st.metric("ROE", f"{fund.get('return_on_equity', 0)*100:.2f}%" if fund.get('return_on_equity') else 'N/A')
                    st.metric("Dividend Yield", f"{fund.get('dividend_yield', 0)*100:.2f}%" if fund.get('dividend_yield') else '0.00%')
            else:
                st.warning("No fundamental analysis available")
    
    def _display_portfolio_table(self) -> None:
        """Display the portfolio in a table with actions using native Streamlit components."""
        if not st.session_state.portfolio:
            st.info("Your portfolio is empty. Add stocks to get started!")
            return
        
        # Create a container for the table
        table_container = st.container()
        
        # Create header row
        with table_container:
            cols = st.columns([2, 1, 1.5, 1.5, 1.5, 1.5, 2])
            headers = ['Symbol', 'Quantity', 'Avg. Buy Price', 'Current Price', 'P&L', 'Value', 'Actions']
            for col, header in zip(cols, headers):
                col.markdown(f"**{header}**")
            
            st.markdown("---")
        
        # Fetch latest prices for all stocks
        with st.spinner("Fetching latest prices..."):
            updated_portfolio = []
            for stock in st.session_state.portfolio:
                # Get the latest price
                current_price, _, _ = self._get_stock_data(stock['symbol'])
                
                # Update the stock with latest price if available
                if current_price is not None:
                    stock['current_price'] = current_price
                # Fallback to existing current_price or buy_price if fetch fails
                elif 'current_price' not in stock:
                    stock['current_price'] = stock['buy_price']
                
                # Add the stock to the updated portfolio
                updated_portfolio.append(stock)
        
        # Update the session state with latest prices
        st.session_state.portfolio = updated_portfolio
        
        # Add rows with data and buttons
        total_pnl = 0
        for i, stock in enumerate(st.session_state.portfolio):
            current_price = stock.get('current_price', stock['buy_price'])
            pnl = stock.get('current_pnl', 0)
            pnl_pct = stock.get('current_pnl_pct', 0)
            total_pnl += pnl
        
            # Determine P&L color
            pnl_color = "#4CAF50" if pnl >= 0 else "#f44336"
            pnl_display = f"<span style='color: {pnl_color}'>₹{abs(pnl):,.2f} ({pnl_pct:+.2f}%)</span>"
            
            # Create columns for this row
            with table_container:
                cols = st.columns([2, 1, 1.5, 1.5, 1.5, 1.5, 2])
                
                # Stock data
                cols[0].write(stock['symbol'])
                cols[1].write(f"{stock['quantity']:.4f}")
                cols[2].write(f"₹{stock['buy_price']:,.2f}")
                cols[3].write(f"₹{current_price:,.2f}")
                cols[4].markdown(pnl_display, unsafe_allow_html=True)
                cols[5].write(f"₹{(stock['quantity'] * current_price):,.2f}")
                
                # Action buttons
                btn_col1, btn_col2 = cols[6].columns(2)
                with btn_col1:
                    if st.button("✏️", key=f"edit_btn_{stock['symbol']}_{i}"):
                        # Set up the edit form state
                        st.session_state['editing_stock_index'] = i
                        st.session_state['editing_stock_symbol'] = stock['symbol']
                        st.session_state['show_edit_form'] = True
                        # Clear any existing delete state
                        if 'show_delete_confirm' in st.session_state:
                            del st.session_state['show_delete_confirm']
                        st.rerun()
                
                with btn_col2:
                    if st.button("🗑️", key=f"delete_btn_{stock['symbol']}_{i}"):
                        st.session_state["delete_index"] = i
                        st.session_state["deleting_stock_symbol"] = stock['symbol']
                        st.session_state["show_delete_confirm"] = True
                        st.rerun()
                
                # Show delete confirmation if this is the stock being deleted
                if st.session_state.get("show_delete_confirm", False) and \
                   st.session_state.get("delete_index") == i:
                    self._render_delete_confirmation(
                        stock_symbol=stock['symbol'],
                        stock=stock,
                        index=i
                    )
    
    def _clean_numeric_value(self, value):
        """Remove currency symbols and convert to float."""
        if pd.isna(value) or value == '':
            return 0.0
        if isinstance(value, str):
            # Remove any non-numeric characters except decimal point and negative sign
            value = ''.join(c for c in value if c.isdigit() or c in '.-')
            if not value:  # If we're left with nothing, return 0
                return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _handle_csv_upload(self, uploaded_file) -> None:
        """Handle CSV file upload for portfolio import with symbol lookup."""
        try:
            from utils.stock_utils import find_stock_symbol, load_equity_data
            
            # Load the equity data for symbol lookup
            equity_df = load_equity_data()
            if equity_df.empty:
                st.error("Could not load stock database. Please ensure EQUITY_L.csv is available.")
                return
            
            # Try reading with different encodings
            try:
                df = pd.read_csv(uploaded_file)
            except UnicodeDecodeError:
                # Try with different encodings if the default fails
                df = pd.read_csv(uploaded_file, encoding='latin1')
            
            # Convert column names to lowercase and strip whitespace
            df.columns = df.columns.str.strip().str.lower()
            
            # Check for required columns (case-insensitive)
            required_columns = ['symbol', 'quantity', 'buy_price']
            missing = [col for col in required_columns if col not in df.columns]
            
            # Check if we have a company name column for better matching
            has_company_name = 'company' in df.columns or 'company_name' in df.columns
            company_col = 'company' if 'company' in df.columns else 'company_name' if 'company_name' in df.columns else None
            
            if missing and not has_company_name:
                st.error(f"Missing required columns in CSV. Need either: {', '.join(required_columns)} or 'company' column")
                st.warning(f"Available columns: {', '.join(df.columns)}")
                return
            
            # Process each row
            success_count = 0
            skipped_count = 0
            errors = []
            
            with st.spinner("Processing your portfolio..."):
                progress_bar = st.progress(0)
                total_rows = len(df)
                
                for idx, row in df.iterrows():
                    try:
                        # Update progress
                        progress = (idx + 1) / total_rows
                        progress_bar.progress(min(int(progress * 100), 100))
                        
                        # Get symbol or company name
                        symbol = str(row.get('symbol', '')).strip()
                        company_name = str(row.get(company_col, '')).strip() if company_col else ''
                        
                        # If we have a company name but no symbol, try to find the symbol
                        if (not symbol or symbol.upper() == 'NAN') and company_name:
                            found_symbol = find_stock_symbol(company_name)
                            if found_symbol:
                                symbol = found_symbol
                                st.toast(f"Found symbol {found_symbol} for {company_name}", icon="ℹ️")
                            else:
                                errors.append(f"Row {idx+2}: Could not find symbol for company: {company_name}")
                                skipped_count += 1
                                continue
                        
                        if not symbol or symbol.upper() == 'NAN':
                            errors.append(f"Row {idx+2}: Missing both symbol and company name")
                            skipped_count += 1
                            continue
                        
                        # Clean and convert numeric values
                        quantity = self._clean_numeric_value(row['quantity'])
                        buy_price = self._clean_numeric_value(row['buy_price'])
                        
                        # Validate required fields
                        if quantity <= 0 or buy_price <= 0:
                            errors.append(f"Row {idx+2}: Invalid quantity or price for {symbol}")
                            skipped_count += 1
                            continue
                        
                        # Handle date (with fallback to today)
                        buy_date = datetime.now().date()
                        if 'buy_date' in df.columns and pd.notna(row.get('buy_date')):
                            try:
                                buy_date = pd.to_datetime(row['buy_date']).date()
                            except (ValueError, TypeError):
                                # If date parsing fails, use today's date
                                pass
                        
                        # Get notes if available
                        notes = str(row.get('notes', '')).strip()
                        
                        if self._add_stock(symbol, quantity, buy_price, buy_date, notes):
                            success_count += 1
                        else:
                            errors.append(f"Row {idx+2}: Failed to add {symbol} ({company_name if company_name else 'no company name'})")
                            skipped_count += 1
                            
                    except Exception as e:
                        errors.append(f"Row {idx+2}: {str(e)}")
                        skipped_count += 1
                
                progress_bar.empty()
            
            # Show results
            if success_count > 0:
                st.success(f"✅ Successfully imported {success_count} stocks from {uploaded_file.name}")
            
            if skipped_count > 0:
                st.warning(f"⚠️ Skipped {skipped_count} rows due to errors or missing data")
            
            if errors:
                with st.expander("⚠️ Import Warnings/Errors", expanded=len(errors) < 5):
                    for error in errors[:20]:  # Show first 20 errors to avoid overwhelming the UI
                        st.error(error)
                    if len(errors) > 20:
                        st.warning(f"... and {len(errors) - 20} more errors not shown")
            
            if success_count > 0:
                st.balloons()
                st.rerun()
            
        except Exception as e:
            st.error(f"Error processing CSV file: {str(e)}")
            st.warning("Please ensure the file is a valid CSV with the correct format.")
            logger.exception("Error in _handle_csv_upload")
    
    def _render_add_stock_form(self) -> None:
        """Render the form to add a new stock with company name lookup."""
        with st.form("add_stock_form"):
            st.subheader("Add Stock")
            
            # Toggle between symbol and company name search
            search_mode = st.radio("Search by:", ["Company Name", "Stock Symbol"], horizontal=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if search_mode == "Company Name":
                    company_name = st.text_input("Company Name", 
                                               placeholder="e.g., Reliance Industries",
                                               help="Start typing the company name")
                    
                    # Show symbol lookup results as the user types
                    if company_name and len(company_name) > 2:
                        from utils.stock_utils import find_stock_symbol
                        symbol = find_stock_symbol(company_name)
                        if symbol:
                            st.info(f"Found symbol: {symbol}")
                        else:
                            st.warning("No matching company found. Try a different name.")
                            return
                    else:
                        symbol = ""
                else:
                    symbol = st.text_input("Stock Symbol", 
                                         placeholder="e.g., RELIANCE.NS",
                                         help="Enter the stock symbol (e.g., RELIANCE.NS)")
                
                quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
            
            with col2:
                buy_price = st.number_input("Buy Price (₹)", min_value=0.01, value=100.0, step=0.01)
                buy_date = st.date_input("Buy Date", value=datetime.now().date())
            
            notes = st.text_area("Notes (Optional)", 
                               placeholder="Add any notes about this investment")
            
            if st.form_submit_button("Add to Portfolio", use_container_width=True):
                if not symbol and search_mode == "Company Name" and company_name:
                    st.error("Please select a company from the suggestions")
                    return
                
                if not symbol and search_mode == "Stock Symbol":
                    st.error("Please enter a stock symbol")
                    return
                
                try:
                    # If we searched by company name, ensure we have a valid symbol
                    if search_mode == "Company Name" and company_name and not symbol:
                        from utils.stock_utils import find_stock_symbol
                        symbol = find_stock_symbol(company_name)
                        if not symbol:
                            st.error(f"Could not find symbol for {company_name}")
                            return
                    
                    if self._add_stock(symbol, quantity, buy_price, buy_date, notes):
                        st.success(f"Successfully added {symbol} to your portfolio!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error adding stock: {str(e)}")
                    logger.exception("Error in _render_add_stock_form")
        
    def _render_add_import_tab(self) -> None:
        """Render the add/import stocks tab."""
        st.header("Add or Import Stocks")
        
        # Manual entry form
        self._render_add_stock_form()
        
        # CSV import section
        st.subheader("Import from CSV")
        st.download_button(
            label="📥 Download Template",
            data="symbol,quantity,buy_price,buy_date,notes\nAAPL,10,150.25,2023-01-15,Long term hold\nMSFT,5,300.50,2023-02-20,Tech growth",
            file_name="portfolio_template.csv",
            mime="text/csv"
        )
        
    def _render_analysis_tab(self) -> None:
        """Render the analysis tab."""
        st.header("📈 Portfolio Analysis")
        
        if not st.session_state.portfolio:
            st.info("Your portfolio is empty. Add stocks to see analysis.")
            
        # Add file uploader
        uploaded_file = st.file_uploader("Or upload your portfolio CSV", type=["csv"])
        if uploaded_file is not None:
            self._handle_csv_upload(uploaded_file)

    def _render_edit_form(self) -> None:
        """Render the edit stock form with a unique key."""
        if not st.session_state.get('show_edit_form'):
            return
            
        stock_symbol = st.session_state.get('editing_stock_symbol')
        edit_index = st.session_state.get('editing_stock_index')
        
        if stock_symbol is None or edit_index is None or edit_index >= len(st.session_state.portfolio):
            # Reset form state if the index is invalid
            st.session_state['show_edit_form'] = False
            if 'editing_stock_symbol' in st.session_state:
                del st.session_state['editing_stock_symbol']
            if 'editing_stock_index' in st.session_state:
                del st.session_state['editing_stock_index']
            return
            
        # Get the stock data
        stock = st.session_state.portfolio[edit_index]
        
        # Create a unique form key
        form_key = f"edit_form_{stock_symbol}_{edit_index}"
        
        with st.form(key=form_key):
            st.subheader(f"Edit {stock_symbol}")
            
            # Form fields with current values
            quantity = st.number_input(
                "Quantity", 
                min_value=0.0, 
                step=0.01, 
                format="%.2f",
                value=float(stock['quantity']),
                key=f"edit_quantity_{form_key}"
            )
            
            buy_price = st.number_input(
                "Buy Price (₹)", 
                min_value=0.0, 
                step=0.01, 
                format="%.2f",
                value=float(stock['buy_price']),
                key=f"edit_buy_price_{form_key}"
            )
            
            buy_date = st.date_input(
                "Buy Date",
                value=datetime.strptime(stock.get('buy_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
                key=f"edit_buy_date_{form_key}"
            )
            
            notes = st.text_area(
                "Notes",
                value=stock.get('notes', ''),
                key=f"edit_notes_{form_key}"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                save_clicked = st.form_submit_button("💾 Save Changes")
            
            with col2:
                cancel_clicked = st.form_submit_button("❌ Cancel", type="secondary")
            
            if save_clicked:
                try:
                    updates = {
                        'quantity': float(quantity),
                        'buy_price': float(buy_price),
                        'buy_date': buy_date.strftime('%Y-%m-%d'),
                        'notes': notes
                    }
                    if self._update_stock(edit_index, **updates):
                        st.session_state['show_edit_form'] = False
                        if 'editing_stock_symbol' in st.session_state:
                            del st.session_state['editing_stock_symbol']
                        if 'editing_stock_index' in st.session_state:
                            del st.session_state['editing_stock_index']
                        st.rerun()
                except Exception as e:
                    st.error(f"Error updating stock: {str(e)}")
            
            if cancel_clicked:
                st.session_state['show_edit_form'] = False
                if 'editing_stock_symbol' in st.session_state:
                    del st.session_state['editing_stock_symbol']
                if 'editing_stock_index' in st.session_state:
                    del st.session_state['editing_stock_index']
                st.rerun()

    def _delete_stock(self, index: int) -> None:
        """
        Delete a stock from the portfolio by index.
        
        Args:
            index: Index of the stock to delete
        """
        try:
            if 0 <= index < len(st.session_state.portfolio):
                # Get the stock being deleted for logging
                deleted_stock = st.session_state.portfolio[index]
                
                # Remove the stock from the portfolio
                del st.session_state.portfolio[index]
                
                # Save the updated portfolio
                self._save_portfolio()
                
                logger.info(f"Deleted stock: {deleted_stock['symbol']} at index {index}")
                st.success(f"Successfully deleted {deleted_stock['symbol']} from your portfolio.")
            else:
                logger.warning(f"Invalid index {index} for deletion. Portfolio length: {len(st.session_state.portfolio)}")
                st.error("Error: Invalid stock index for deletion.")
        except Exception as e:
            logger.error(f"Error deleting stock at index {index}: {str(e)}")
            st.error(f"An error occurred while deleting the stock: {str(e)}")

    def _render_delete_confirmation(self, stock_symbol: str, stock: dict, index: int) -> None:
        """Render the delete confirmation dialog with unique keys."""
        with st.container():
            st.warning("⚠️ Are you sure you want to delete this stock?")
            st.write(f"**Symbol:** {stock_symbol}")
            st.write(f"**Quantity:** {stock['quantity']}")
            st.write(f"**Buy Price:** ₹{stock['buy_price']:,.2f}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Yes, delete it", key=f"confirm_del_{stock_symbol}_{index}"):
                    self._delete_stock(index)
                    # Clear the delete state after deletion
                    for key in ["delete_index", "show_delete_confirm", "deleting_stock_symbol"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
            
            with col2:
                if st.button("❌ No, keep it", key=f"cancel_del_{stock_symbol}_{index}"):
                    for key in ["delete_index", "show_delete_confirm", "deleting_stock_symbol"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()

    def render(self) -> None:
        """Render the enhanced portfolio interface."""
        st.title("📊 Enhanced Portfolio Management")
        
        # Cloud persistence warning and status
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            # Get sync status
            sync_status = self.firebase_sync.get_sync_status()
            source = st.session_state.get('portfolio_source', 'unknown')
            
            if source == "firebase":
                st.success("☁️ **Cloud Storage**: Portfolio loaded from Firebase cloud storage")
            elif source == "session":
                st.info("💾 **Session Storage**: Portfolio loaded from current session")
            elif source == "file":
                st.warning("📁 **Local File**: Portfolio loaded from local file (synced to cloud)")
            else:
                st.info("🆕 **New Portfolio**: Start by adding stocks to your portfolio")
        
        with col2:
            if 'portfolio_last_saved' in st.session_state:
                last_saved = st.session_state.portfolio_last_saved[:19].replace('T', ' ')
                st.success(f"✅ Saved\n{last_saved}")
            else:
                st.warning("⚠️ Not saved")
        
        with col3:
            sync_status_icon = "🔄" if st.session_state.get('portfolio_sync_status') == 'sync_failed' else "☁️"
            if sync_status.get('sync_enabled', False):
                if sync_status.get('has_real_db', False):
                    st.success(f"{sync_status_icon}\nFirebase")
                else:
                    st.info(f"{sync_status_icon}\nMock")
            else:
                st.info("📱\nLocal")

        # Create tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["My Portfolio", "Add/Import Stocks", "Analysis", "Cloud Backup"])

        with tab1:
            self._render_portfolio_tab()

        with tab2:
            self._render_add_import_tab()

        with tab3:
            self._render_analysis_tab()
            
        with tab4:
            self._render_cloud_backup_tab()

    def _render_portfolio_tab(self) -> None:
        """Render the main portfolio tab."""
        # Custom CSS for better tab styling
        st.markdown("""
        <style>
            /* Main tab styling */
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                padding: 10px 20px;
                margin: 0 5px;
                background-color: #f0f2f6;
                border-radius: 8px 8px 0 0;
                border: 1px solid #dcdcdc;
                color: #4a4a4a;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            /* Hover state */
            .stTabs [data-baseweb="tab"]:hover {
                background-color: #e1e4eb;
                color: #2c3e50;
            }
            
            /* Active tab */
            .stTabs [aria-selected="true"] {
                background-color: #4a90e2 !important;
                color: white !important;
                border-bottom: 3px solid #2c3e50;
            }
            
            /* Container for tabs */
            .stTabs [role="tablist"] {
                gap: 5px;
                padding: 0 10px;
            }
            
            /* Better contrast for metrics */
            .stMetric {
                background-color: #f8f9fa !important;
                color: #2c3e50 !important;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            /* Ensure text is visible in metric cards */
            .stMetric > div > div {
                color: #2c3e50 !important;
            }
            
            .stMetric > div > div[data-testid="stMetricValue"] > div {
                color: #2c3e50 !important;
                font-weight: 600;
                font-size: 1.2rem;
            }
            
            .stMetric > div > div[data-testid="stMetricLabel"] > div {
                color: #4a4a4a !important;
                opacity: 0.9;
            }
            
            /* Make sure delta indicators are visible */
            .stMetric > div > div[data-testid="stMetricDelta"] > div {
                font-weight: 500;
            }
            
            /* Improve button visibility */
            .stButton>button {
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
            }
            
            /* Table styling */
            .stDataFrame {
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            }
            
            /* Section headers */
            h1, h2, h3 {
                color: #2c3e50;
            }
            
            /* Status messages */
            .stAlert {
                border-radius: 8px;
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.header("📊 My Portfolio")
        
        # Show edit form if in edit mode
        if st.session_state.get('show_edit_form', False):
            self._render_edit_form()
            return
            
        # Show delete confirmation if needed
        if st.session_state.get('show_delete_confirm', False) and 'delete_index' in st.session_state:
            delete_index = st.session_state['delete_index']
            if 0 <= delete_index < len(st.session_state.portfolio):
                stock = st.session_state.portfolio[delete_index]
                self._render_delete_confirmation(
                    stock_symbol=stock['symbol'],
                    stock=stock,
                    index=delete_index
                )
                return
        
        if st.session_state.portfolio:
            # Ensure we have the latest prices
            updated_portfolio = []
            for stock in st.session_state.portfolio:
                try:
                    # Get the latest price
                    current_price, _, _ = self._get_stock_data(stock['symbol'])
                    if current_price is not None:
                        stock['current_price'] = current_price
                    # Fallback to existing current_price or buy_price if fetch fails
                    elif 'current_price' not in stock:
                        stock['current_price'] = stock['buy_price']
                except Exception as e:
                    logger.warning(f"Failed to update price for {stock.get('symbol', 'unknown')}: {str(e)}")
                    stock['current_price'] = stock.get('current_price', stock['buy_price'])
                updated_portfolio.append(stock)
            
            # Update the session state with latest prices
            st.session_state.portfolio = updated_portfolio
            
            # Calculate portfolio metrics
            total_investment = sum(stock['quantity'] * stock['buy_price'] for stock in st.session_state.portfolio)
            current_value = 0
            total_pnl = 0
            
            # Calculate individual stock P&L and update current value
            for stock in st.session_state.portfolio:
                current_price = stock.get('current_price', stock['buy_price'])
                stock_pnl = (current_price - stock['buy_price']) * stock['quantity']
                stock['current_pnl'] = stock_pnl
                stock['current_pnl_pct'] = ((current_price - stock['buy_price']) / stock['buy_price'] * 100) if stock['buy_price'] > 0 else 0
                current_value += stock['quantity'] * current_price
                total_pnl += stock_pnl
            
            # Calculate total P&L percentage
            total_pnl_pct = (total_pnl / total_investment * 100) if total_investment > 0 else 0
            
            # Display summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Investment", f"₹{total_investment:,.2f}")
            with col2:
                st.metric("Current Value", f"₹{current_value:,.2f}")
            with col3:
                st.metric(
                    "Total P&L", 
                    f"₹{total_pnl:+,.2f}", 
                    f"{total_pnl_pct:+.2f}%",
                    delta_color="normal" if total_pnl >= 0 else "inverse"
                )
            
            # Action buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Update All Prices"):
                    with st.spinner("Updating prices..."):
                        for stock in st.session_state.portfolio:
                            try:
                                ticker = yf.Ticker(stock['symbol'])
                                stock['current_price'] = ticker.history(period='1d')['Close'].iloc[-1]
                                stock['last_updated'] = datetime.now().isoformat()
                            except Exception as e:
                                st.warning(f"Failed to update price for {stock.get('symbol', 'unknown')}: {str(e)}")
                                continue
                        self._save_portfolio()
                        st.rerun()
            
            with col2:
                if st.button("🗑️ Delete Portfolio", type="secondary", help="Delete all stocks from your portfolio"):
                    st.session_state['show_delete_all_confirm'] = True
                    st.rerun()
            
            # Delete all confirmation dialog
            if st.session_state.get('show_delete_all_confirm', False):
                st.warning("⚠️ Are you sure you want to delete your entire portfolio? This action cannot be undone!")
                confirm_col1, confirm_col2 = st.columns(2)
                
                with confirm_col1:
                    if st.button("✅ Yes, delete everything", type="primary"):
                        st.session_state.portfolio = []
                        self._save_portfolio()
                        st.session_state['show_delete_all_confirm'] = False
                        st.rerun()
                
                with confirm_col2:
                    if st.button("❌ Cancel"):
                        st.session_state['show_delete_all_confirm'] = False
                        st.rerun()
                
                st.markdown("---")  # Add a separator
            
            # Portfolio table
            st.subheader("Your Holdings")
            self._display_portfolio_table()
            
            # Handle analysis actions
            if 'selected_action' in st.session_state and st.session_state.selected_action:
                action_parts = st.session_state.selected_action.split('_')
                if len(action_parts) == 3 and action_parts[0] == 'analyze':
                    symbol = action_parts[1]
                    idx = int(action_parts[2])
                    if 0 <= idx < len(st.session_state.portfolio):
                        with st.expander(f"Analysis for {symbol}", expanded=True):
                            if st.session_state.portfolio[idx].get('analysis'):
                                self._display_analysis(st.session_state.portfolio[idx]['analysis'])
                            else:
                                st.info("No analysis available. Click 'Analyze' to generate one.")
        else:
            st.info("Your portfolio is empty. Add stocks to get started!")
            
            # Add a download template button
            st.download_button(
                label="📥 Download Portfolio Template",
                data="symbol,company,quantity,buy_price,buy_date,notes\nRELIANCE.NS,RELIANCE INDUSTRIES LTD,10,2500,2023-01-15,Long term hold\n,TATA CONSULTANCY SERVICES,5,3500,2023-02-20,IT sector",
                file_name="portfolio_template.csv",
                mime="text/csv"
            )
            
            # Add file uploader
            uploaded_file = st.file_uploader("Or upload your portfolio CSV", type=["csv"])
            if uploaded_file is not None:
                self._handle_csv_upload(uploaded_file)
    
    def render(self) -> None:
        """Render the enhanced portfolio interface."""
        st.title("📊 Enhanced Portfolio Management")
        
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["My Portfolio", "Add/Import Stocks", "Analysis"])
        
        with tab1:
            self._render_portfolio_tab()
            
        with tab2:
            self._render_add_import_tab()
            
        with tab3:
            self._render_analysis_tab()
    
    def _render_analysis_tab(self) -> None:
        """Render the analysis tab."""
        st.header("Portfolio Analysis")
        
        if not st.session_state.portfolio:
            st.info("Your portfolio is empty. Add stocks to see analysis.")
            return
        
        # Portfolio-wide analysis
        st.subheader("Portfolio Health")
        
        # Calculate sector allocation
        sectors = {}
        for stock in st.session_state.portfolio:
            # Get sector information (simplified - in a real app, you'd use an API)
            sector = "Unknown"
            if stock.get('analysis') and stock['analysis'].get('fundamental_analysis', {}).get('sector'):
                sector = stock['analysis']['fundamental_analysis']['sector']
            
            current_value = stock['quantity'] * stock.get('current_price', stock['buy_price'])
            sectors[sector] = sectors.get(sector, 0) + current_value
        
        # Display sector allocation
        if sectors:
            st.subheader("Sector Allocation")
            sector_df = pd.DataFrame({
                'Sector': list(sectors.keys()),
                'Value': list(sectors.values())
            })
            sector_df['Percentage'] = (sector_df['Value'] / sector_df['Value'].sum() * 100).round(1)
            st.bar_chart(sector_df.set_index('Sector')['Percentage'])
        
        # Individual stock analysis
        st.subheader("Stock Analysis")
        
        # Create a selectbox to choose which stock to analyze
        stock_options = [f"{stock['symbol']} - {stock.get('notes', '')}" for stock in st.session_state.portfolio]
        selected_stock = st.selectbox(
            "Select a stock to analyze",
            [""] + stock_options,
            index=0
        )
        
        if selected_stock:
            idx = stock_options.index(selected_stock)
            stock = st.session_state.portfolio[idx]
            
            # Check if we already have analysis for this stock
            if not stock.get('analysis'):
                if st.button(f"Analyze {stock['symbol']}"):
                    with st.spinner(f"Analyzing {stock['symbol']}..."):
                        analysis = self._analyze_stock(stock['symbol'])
                        if analysis and 'error' not in analysis:
                            stock['analysis'] = analysis
                            self._save_portfolio()
                            st.rerun()
                        else:
                            st.error("Failed to analyze stock. Please try again later.")
            else:
                # Display the analysis
                self._display_analysis(stock['analysis'])
                
                # Add a button to refresh the analysis
                if st.button(f"🔄 Refresh Analysis for {stock['symbol']}"):
                    with st.spinner(f"Refreshing analysis for {stock['symbol']}..."):
                        analysis = self._analyze_stock(stock['symbol'])
                        if analysis and 'error' not in analysis:
                            stock['analysis'] = analysis
                            self._save_portfolio()
                            st.rerun()

    def _render_cloud_backup_tab(self) -> None:
        """Render the cloud backup and restore tab."""
        st.header("☁️ Cloud Backup & Restore")
        
        # Get sync status
        sync_status = self.firebase_sync.get_sync_status()
        
        # Display sync status
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Sync Status")
            st.write(f"**Firebase Initialized**: {'✅ Yes' if sync_status['initialized'] else '❌ No'}")
            st.write(f"**User ID**: {sync_status['user_id'] or 'Not set'}")
            st.write(f"**Sync Enabled**: {'✅ Yes' if sync_status['sync_enabled'] else '❌ No'}")
            st.write(f"**Database Type**: {'Real Firebase' if sync_status.get('has_real_db', False) else 'Mock Mode'}")
            if sync_status['last_sync']:
                st.write(f"**Last Sync**: {sync_status['last_sync'][:19].replace('T', ' ')}")
        
        with col2:
            st.subheader("💾 Backup Actions")
            
            # Manual sync button
            if st.button("🔄 Force Sync to Cloud", help="Manually sync your portfolio to Firebase"):
                with st.spinner("Syncing to cloud..."):
                    if self.firebase_sync.sync_portfolio(st.session_state.portfolio):
                        st.success("Portfolio synced to cloud successfully!")
                        st.session_state.portfolio_sync_status = "synced"
                        st.rerun()
                    else:
                        st.error("Failed to sync portfolio to cloud")
            
            # Export portfolio
            if st.button("📥 Export Portfolio", help="Download your portfolio as JSON"):
                portfolio_data = {
                    'portfolio': st.session_state.portfolio,
                    'export_date': datetime.now().isoformat(),
                    'user_id': st.session_state.get('user_id'),
                    'version': '1.0'
                }
                json_data = json.dumps(portfolio_data, indent=2, ensure_ascii=False, default=str)
                st.download_button(
                    label="💾 Download Portfolio JSON",
                    data=json_data,
                    file_name=f"portfolio_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        # Import/Restore section
        st.subheader("🔄 Import & Restore")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Import from File**")
            uploaded_file = st.file_uploader("Upload portfolio JSON file", type=['json'])
            if uploaded_file is not None:
                try:
                    imported_data = json.load(uploaded_file)
                    if 'portfolio' in imported_data and isinstance(imported_data['portfolio'], list):
                        if st.button("📥 Import Portfolio", key="import_portfolio"):
                            # Validate and import portfolio
                            valid_portfolio = []
                            for item in imported_data['portfolio']:
                                if isinstance(item, dict) and 'symbol' in item and 'quantity' in item and 'buy_price' in item:
                                    valid_portfolio.append(item)
                            

                            if valid_portfolio:
                                st.session_state.portfolio = valid_portfolio
                                self._save_portfolio()
                                st.success(f"Successfully imported {len(valid_portfolio)} stocks!")
                                st.rerun()
                            else:
                                st.error("No valid portfolio data found in file")
                    else:
                        st.error("Invalid portfolio file format")
                except Exception as e:
                    st.error(f"Error importing portfolio: {str(e)}")
        
        with col2:
            st.write("**Restore from Cloud**")
            if st.button("☁️ Restore from Firebase", help="Restore portfolio from Firebase cloud storage"):
                with st.spinner("Restoring from cloud..."):
                    cloud_portfolio = self.firebase_sync.load_portfolio()
                    if cloud_portfolio is not None:
                        st.session_state.portfolio = cloud_portfolio
                        self._save_portfolio()
                        st.success(f"Successfully restored {len(cloud_portfolio)} stocks from cloud!")
                        st.rerun()
                    else:
                        st.info("No portfolio found in cloud storage")
        
        # Advanced options
        with st.expander("🔧 Advanced Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Clear Cloud Data", type="secondary", help="Remove portfolio from Firebase"):
                    if st.session_state.get('confirm_clear_cloud', False):
                        # Clear cloud data
                        if self.firebase_sync.delete_user_data():
                            st.success("Cloud data cleared!")
                        else:
                            st.error("Failed to clear cloud data")
                        st.session_state.confirm_clear_cloud = False
                        st.rerun()
                    else:
                        st.session_state.confirm_clear_cloud = True
                        st.warning("Click again to confirm clearing cloud data")
            
            with col2:
                if st.button("🔄 Reset User ID", type="secondary", help="Generate a new user ID"):
                    # Generate new user ID
                    import hashlib
                    import time
                    user_string = f"portfolio_user_{int(time.time())}_{hash(str(st.session_state))}"
                    new_user_id = hashlib.md5(user_string.encode()).hexdigest()[:16]
                    st.session_state.user_id = new_user_id
                    self.firebase_sync.set_user_id(new_user_id)
                    st.success(f"New User ID generated: {new_user_id}")
                    st.rerun()
        
        # Firebase setup instructions
        if not sync_status.get('has_real_db', False):
            st.info("💡 **To enable real Firebase sync:**\n"
                   "1. Create a Firebase project at https://console.firebase.google.com\n"
                   "2. Set up Firestore Database\n"
                   "3. Add Firebase credentials to Streamlit secrets\n"
                   "4. Add 'firebase-admin' to requirements.txt")

# Helper function to use in app.py
def render_enhanced_portfolio():
    """Render the enhanced portfolio interface."""
    portfolio = EnhancedPortfolio()
    portfolio.render()

if __name__ == "__main__":
    # For testing
    import streamlit as st
    st.set_page_config(layout="wide")
    render_enhanced_portfolio()
