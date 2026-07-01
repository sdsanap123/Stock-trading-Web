import pandas as pd
import os
import time
import requests
from typing import Optional, Dict, Any, List, Tuple
import yfinance as yf
import logging
from functools import lru_cache

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store the equity data
equity_df = None

# Cache for online symbol searches
@lru_cache(maxsize=100)
def search_symbol_online(company_name: str) -> Optional[Dict[str, str]]:
    """
    Search for stock symbol online using Yahoo Finance API.
    
    Args:
        company_name: The name of the company to search for
        
    Returns:
        Dict containing symbol and company name if found, None otherwise
    """
    try:
        # First try yfinance's search
        try:
            search_results = yf.Tickers(company_name)
            if search_results.symbols:
                ticker = yf.Ticker(search_results.symbols[0])
                info = ticker.info
                if info and 'symbol' in info:
                    return {
                        'symbol': info['symbol'].split('.')[0],  # Remove exchange suffix if any
                        'name': info.get('shortName', company_name)
                    }
        except Exception as e:
            logger.debug(f"yfinance search failed, trying direct API: {str(e)}")
        
        # Fallback to Yahoo Finance API
        url = f"https://query1.finance.yahoo.com/v1/finance/search?q={company_name}&quotesCount=5&newsCount=0"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'quotes' in data and data['quotes']:
            return {
                'symbol': data['quotes'][0]['symbol'].split('.')[0],  # Remove exchange suffix
                'name': data['quotes'][0].get('longname', company_name)
            }
            
        return None
        
    except Exception as e:
        logger.warning(f"Error searching for symbol online: {str(e)}")
        return None

def load_equity_data() -> pd.DataFrame:
    """
    Load the EQUITY_L.csv file into a pandas DataFrame with caching.
    
    Returns:
        pd.DataFrame: DataFrame containing equity data with columns like 'SYMBOL', 'NAME OF COMPANY', etc.
    """
    global equity_df
    
    if equity_df is not None and not equity_df.empty:
        return equity_df
    
    try:
        # Try to find EQUITY_L.csv in common locations
        search_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'EQUITY_L.csv'),
            'EQUITY_L.csv',
            os.path.join('data', 'EQUITY_L.csv'),
            os.path.join('..', 'EQUITY_L.csv')
        ]
        
        file_path = None
        for path in search_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if not file_path:
            logger.error("EQUITY_L.csv not found in any of the searched locations")
            return pd.DataFrame(columns=['SYMBOL', 'NAME OF COMPANY'])
        
        # Read the CSV with appropriate encoding
        try:
            equity_df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            equity_df = pd.read_csv(file_path, encoding='latin1')
        
        # Standardize column names (strip and uppercase)
        equity_df.columns = equity_df.columns.str.strip().str.upper()
        
        # Ensure required columns exist
        required_columns = ['SYMBOL', 'NAME OF COMPANY']
        for col in required_columns:
            if col not in equity_df.columns:
                logger.error(f"Required column '{col}' not found in EQUITY_L.csv")
                return pd.DataFrame(columns=required_columns)
        
        # Clean the data
        equity_df = equity_df.dropna(subset=['SYMBOL', 'NAME OF COMPANY'], how='all')
        equity_df['SYMBOL'] = equity_df['SYMBOL'].astype(str).str.strip()
        equity_df['NAME OF COMPANY'] = equity_df['NAME OF COMPANY'].astype(str).str.strip()
        
        # Remove duplicates, keeping the first occurrence
        equity_df = equity_df.drop_duplicates(subset=['SYMBOL'], keep='first')
        
        logger.info(f"Successfully loaded {len(equity_df)} equity records from {file_path}")
        
    except Exception as e:
        logger.error(f"Error loading EQUITY_L.csv: {str(e)}")
        equity_df = pd.DataFrame(columns=['SYMBOL', 'NAME OF COMPANY'])
    
    return equity_df

def find_stock_symbol(company_name: str, search_online: bool = True) -> Optional[str]:
    """
    Find stock symbol by company name or symbol, with optional online search.
    
    Args:
        company_name: The name or symbol of the company to search for
        search_online: Whether to search online if not found locally
        
    Returns:
        str: The stock symbol with exchange suffix (e.g., 'RELIANCE.NS') if found, None otherwise
    """
    try:
        if not company_name or not isinstance(company_name, str):
            return None
            
        # First try local lookup
        symbol = _find_stock_symbol_local(company_name)
        if symbol:
            return symbol
            
        # If not found locally and online search is enabled
        if search_online:
            online_result = search_symbol_online(company_name)
            if online_result:
                # Cache the result in local database for future use
                try:
                    df = load_equity_data()
                    if not df.empty and 'SYMBOL' in df.columns and 'NAME OF COMPANY' in df.columns:
                        # Check if symbol already exists to avoid duplicates
                        if not df[df['SYMBOL'] == online_result['symbol']].empty:
                            return f"{online_result['symbol']}.NS"
                            
                        # Add new symbol to the dataframe
                        new_row = pd.DataFrame([{
                            'SYMBOL': online_result['symbol'],
                            'NAME OF COMPANY': online_result['name'],
                            'SOURCE': 'ONLINE',
                            'ADDED_DATE': pd.Timestamp.now().strftime('%Y-%m-%d')
                        }])
                        
                        # Save the updated dataframe
                        global equity_df
                        equity_df = pd.concat([df, new_row], ignore_index=True)
                        
                        # Try to save back to the original file if possible
                        try:
                            file_path = None
                            search_paths = [
                                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'EQUITY_L.csv'),
                                'EQUITY_L.csv',
                                os.path.join('data', 'EQUITY_L.csv'),
                                os.path.join('..', 'EQUITY_L.csv')
                            ]
                            
                            for path in search_paths:
                                if os.path.exists(path):
                                    file_path = path
                                    break
                            
                            if file_path:
                                equity_df.to_csv(file_path, index=False, encoding='utf-8')
                        except Exception as e:
                            logger.warning(f"Could not save updated EQUITY_L.csv: {str(e)}")
                except Exception as e:
                    logger.warning(f"Could not cache online result: {str(e)}")
                
                return f"{online_result['symbol']}.NS"
                
        return None
            
    except Exception as e:
        logger.error(f"Error in find_stock_symbol for '{company_name}': {str(e)}")
        return None

def _find_stock_symbol_local(company_name: str) -> Optional[str]:
    """
    Local implementation of stock symbol lookup in EQUITY_L.csv.
    
    Args:
        company_name: The name or symbol of the company to search for
        
    Returns:
        str: The stock symbol with exchange suffix (e.g., 'RELIANCE.NS') if found, None otherwise
    """
    try:
        if not company_name or not isinstance(company_name, str):
            return None
            
        df = load_equity_data()
        if df.empty:
            return None
        
        # Clean the input
        search_term = company_name.strip().upper()
        
        # Check if input is already a symbol
        symbol_matches = df[df['SYMBOL'].str.upper() == search_term]
        if not symbol_matches.empty:
            symbol = symbol_matches.iloc[0]['SYMBOL']
            return f"{symbol}.NS"  # Add NSE suffix by default
        
        # Check if input is an ISIN
        if 'ISIN' in df.columns:
            isin_matches = df[df['ISIN'].str.upper() == search_term]
            if not isin_matches.empty:
                return f"{isin_matches.iloc[0]['SYMBOL']}.NS"
        
        # Search in company names with flexible matching
        df['SEARCH_TERM'] = df['NAME OF COMPANY'].str.upper().fillna('')
        
        # Try exact match first
        exact_matches = df[df['SEARCH_TERM'] == search_term]
        if not exact_matches.empty:
            return f"{exact_matches.iloc[0]['SYMBOL']}.NS"
        
        # Try contains match
        contains_matches = df[df['SEARCH_TERM'].str.contains(search_term, case=False, na=False)]
        if not contains_matches.empty:
            return f"{contains_matches.iloc[0]['SYMBOL']}.NS"
        
        # Try word-by-word matching for better partial matches
        search_terms = search_term.split()
        if len(search_terms) > 1:
            # Look for rows that contain all search terms
            mask = df['SEARCH_TERM'].notna()
            for term in search_terms:
                mask = mask & df['SEARCH_TERM'].str.contains(term, case=False, na=False)
            
            matches = df[mask]
            if not matches.empty:
                return f"{matches.iloc[0]['SYMBOL']}.NS"
        
        # Try fuzzy matching for more flexible matching
        try:
            from fuzzywuzzy import process
            company_names = df['SEARCH_TERM'].tolist()
            best_match = process.extractOne(search_term, company_names, score_cutoff=70)
            if best_match:
                matched_name = best_match[0]
                symbol = df[df['SEARCH_TERM'] == matched_name].iloc[0]['SYMBOL']
                return f"{symbol}.NS"
        except ImportError:
            logger.debug("fuzzywuzzy not installed, skipping fuzzy matching")
        
        logger.warning(f"No matching symbol found for: {company_name}")
        return None
            
    except Exception as e:
        logger.error(f"Error finding stock symbol for '{company_name}': {str(e)}")
        return None

def get_stock_data(symbol: str, company_name: str = None) -> Optional[Dict[str, Any]]:
    """
    Get stock data from yfinance with fallback to symbol lookup.
    
    Args:
        symbol: The stock symbol to fetch data for
        company_name: Optional company name for fallback lookup
        
    Returns:
        Dict containing stock data or None if not found
    """
    try:
        # First try with the given symbol
        stock = yf.Ticker(f"{symbol}.NS")
        info = stock.info
        
        # If we don't get valid data, try with company name lookup
        if not info or 'symbol' not in info:
            if company_name:
                alt_symbol = find_stock_symbol(company_name)
                if alt_symbol and alt_symbol != symbol:
                    logger.info(f"Trying alternative symbol {alt_symbol} for {company_name}")
                    stock = yf.Ticker(f"{alt_symbol}.NS")
                    info = stock.info
                    
                    if info and 'symbol' in info:
                        return {
                            'symbol': alt_symbol,
                            'company_name': info.get('shortName', company_name),
                            'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
                            'sector': info.get('sector', ''),
                            'market_cap': info.get('marketCap'),
                            'pe_ratio': info.get('trailingPE'),
                            'volume': info.get('volume')
                        }
        
        # If we have valid data, return it
        if info and 'symbol' in info:
            return {
                'symbol': symbol,
                'company_name': info.get('shortName', company_name or symbol),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
                'sector': info.get('sector', ''),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'volume': info.get('volume')
            }
            
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {str(e)}")
        
    return None
