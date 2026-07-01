#!/usr/bin/env python3
"""
Cache Manager Component
Manages caching for articles and stock analysis to avoid redundant processing.
"""

import json
import pickle
import hashlib
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class CacheManager:
    """Manages caching for articles and stock analysis."""
    
    def __init__(self, cache_dir: str = "cache"):
        """Initialize cache manager."""
        self.cache_dir = cache_dir
        self.articles_cache_file = os.path.join(cache_dir, "articles_cache.pkl")
        self.stocks_cache_file = os.path.join(cache_dir, "stocks_cache.pkl")
        self.analysis_cache_file = os.path.join(cache_dir, "analysis_cache.pkl")
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load existing caches
        self.articles_cache = self._load_cache(self.articles_cache_file)
        self.stocks_cache = self._load_cache(self.stocks_cache_file)
        self.analysis_cache = self._load_cache(self.analysis_cache_file)
        
        # Cache expiration times (in hours)
        self.articles_cache_hours = 168  # Articles cache for 7 days (168 hours)
        self.stocks_cache_hours = 168    # Stock analysis cache for 7 days (168 hours)
        self.analysis_cache_hours = 168  # Groq analysis cache for 7 days (168 hours)
        
        logger.info("Cache Manager initialized successfully")
    
    def _load_cache(self, cache_file: str) -> Dict:
        """Load cache from file."""
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'rb') as f:
                    cache = pickle.load(f)
                    logger.info(f"Loaded cache from {cache_file}")
                    return cache
        except Exception as e:
            logger.warning(f"Could not load cache from {cache_file}: {str(e)}")
        
        return {}
    
    def _save_cache(self, cache: Dict, cache_file: str):
        """Save cache to file."""
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(cache, f)
                logger.info(f"Saved cache to {cache_file}")
        except Exception as e:
            logger.error(f"Could not save cache to {cache_file}: {str(e)}")
    
    def _generate_cache_key(self, data: Any) -> str:
        """Generate a cache key from data."""
        try:
            # Convert data to string and create hash
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception as e:
            logger.warning(f"Could not generate cache key: {str(e)}")
            return str(hash(str(data)))
    
    def _is_cache_valid(self, timestamp: str, cache_hours: int) -> bool:
        """Check if cache entry is still valid."""
        try:
            cache_time = datetime.fromisoformat(timestamp)
            expiry_time = cache_time + timedelta(hours=cache_hours)
            return datetime.now() < expiry_time
        except Exception as e:
            logger.warning(f"Could not check cache validity: {str(e)}")
            return False
    
    def _clean_expired_cache(self, cache: Dict, cache_hours: int) -> Dict:
        """Remove expired entries from cache."""
        cleaned_cache = {}
        for key, value in cache.items():
            if isinstance(value, dict) and 'timestamp' in value:
                if self._is_cache_valid(value['timestamp'], cache_hours):
                    cleaned_cache[key] = value
            else:
                # Keep entries without timestamp (legacy entries)
                cleaned_cache[key] = value
        
        return cleaned_cache
    
    def cache_articles(self, articles: List[Dict]) -> List[Dict]:
        """Cache articles and return only new ones."""
        try:
            # Clean expired cache entries
            self.articles_cache = self._clean_expired_cache(self.articles_cache, self.articles_cache_hours)
            
            new_articles = []
            current_time = datetime.now().isoformat()
            
            for article in articles:
                # Create cache key from article URL and title
                cache_key = self._generate_cache_key({
                    'url': article.get('url', ''),
                    'title': article.get('title', '')
                })
                
                if cache_key not in self.articles_cache:
                    # New article - add to cache and include in new articles
                    self.articles_cache[cache_key] = {
                        'article': article,
                        'timestamp': current_time
                    }
                    new_articles.append(article)
                    logger.debug(f"Cached new article: {article.get('title', '')[:50]}...")
                else:
                    logger.debug(f"Article already cached: {article.get('title', '')[:50]}...")
            
            # Save updated cache
            self._save_cache(self.articles_cache, self.articles_cache_file)
            
            logger.info(f"Cached {len(new_articles)} new articles out of {len(articles)} total articles")
            return new_articles
            
        except Exception as e:
            logger.error(f"Error caching articles: {str(e)}")
            return articles  # Return all articles if caching fails
    
    def cache_stock_analysis(self, symbol: str, analysis_data: Dict) -> bool:
        """Cache stock analysis data."""
        try:
            # Clean expired cache entries
            self.stocks_cache = self._clean_expired_cache(self.stocks_cache, self.stocks_cache_hours)
            
            cache_key = f"stock_{symbol.upper()}"
            current_time = datetime.now().isoformat()
            
            self.stocks_cache[cache_key] = {
                'analysis': analysis_data,
                'timestamp': current_time
            }
            
            # Save updated cache
            self._save_cache(self.stocks_cache, self.stocks_cache_file)
            
            logger.info(f"Cached analysis for stock: {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching stock analysis for {symbol}: {str(e)}")
            return False
    
    def get_cached_stock_analysis(self, symbol: str) -> Optional[Dict]:
        """Get cached stock analysis if available and valid."""
        try:
            cache_key = f"stock_{symbol.upper()}"
            
            if cache_key in self.stocks_cache:
                cache_entry = self.stocks_cache[cache_key]
                
                if isinstance(cache_entry, dict) and 'timestamp' in cache_entry:
                    if self._is_cache_valid(cache_entry['timestamp'], self.stocks_cache_hours):
                        logger.info(f"Retrieved cached analysis for stock: {symbol}")
                        return cache_entry['analysis']
                    else:
                        # Remove expired entry
                        del self.stocks_cache[cache_key]
                        self._save_cache(self.stocks_cache, self.stocks_cache_file)
                        logger.info(f"Removed expired cache for stock: {symbol}")
                else:
                    # Legacy entry without timestamp
                    logger.info(f"Retrieved legacy cached analysis for stock: {symbol}")
                    return cache_entry
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached stock analysis for {symbol}: {str(e)}")
            return None
    
    def cache_groq_analysis(self, analysis_key: str, analysis_data: Dict) -> bool:
        """Cache Groq analysis data."""
        try:
            # Clean expired cache entries
            self.analysis_cache = self._clean_expired_cache(self.analysis_cache, self.analysis_cache_hours)
            
            current_time = datetime.now().isoformat()
            
            self.analysis_cache[analysis_key] = {
                'analysis': analysis_data,
                'timestamp': current_time
            }
            
            # Save updated cache
            self._save_cache(self.analysis_cache, self.analysis_cache_file)
            
            logger.info(f"Cached Groq analysis: {analysis_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching Groq analysis {analysis_key}: {str(e)}")
            return False
    
    def get_cached_groq_analysis(self, analysis_key: str) -> Optional[Dict]:
        """Get cached Groq analysis if available and valid."""
        try:
            if analysis_key in self.analysis_cache:
                cache_entry = self.analysis_cache[analysis_key]
                
                if isinstance(cache_entry, dict) and 'timestamp' in cache_entry:
                    if self._is_cache_valid(cache_entry['timestamp'], self.analysis_cache_hours):
                        logger.info(f"Retrieved cached Groq analysis: {analysis_key}")
                        return cache_entry['analysis']
                    else:
                        # Remove expired entry
                        del self.analysis_cache[analysis_key]
                        self._save_cache(self.analysis_cache, self.analysis_cache_file)
                        logger.info(f"Removed expired Groq cache: {analysis_key}")
                else:
                    # Legacy entry without timestamp
                    logger.info(f"Retrieved legacy cached Groq analysis: {analysis_key}")
                    return cache_entry
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving cached Groq analysis {analysis_key}: {str(e)}")
            return None
    
    def is_stock_in_watchlist(self, symbol: str, watchlist: List[Dict]) -> bool:
        """Check if stock is already in watchlist."""
        try:
            symbol_upper = symbol.upper()
            for item in watchlist:
                if item.get('symbol', '').upper() == symbol_upper:
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking watchlist for {symbol}: {str(e)}")
            return False
    
    def filter_watchlist_stocks(self, stocks: List[Dict], watchlist: List[Dict], 
                               allow_negative_news: bool = True) -> List[Dict]:
        """Filter out stocks already in watchlist unless there's very negative news."""
        try:
            filtered_stocks = []
            
            for stock in stocks:
                symbol = stock.get('symbol', '')
                
                if not self.is_stock_in_watchlist(symbol, watchlist):
                    # Stock not in watchlist - include it
                    filtered_stocks.append(stock)
                elif allow_negative_news:
                    # Stock is in watchlist - only include if very negative news
                    sentiment_score = stock.get('sentiment_score', 0)
                    sentiment_label = stock.get('sentiment_label', 'NEUTRAL')
                    
                    # Only include if very negative (sentiment score < -0.7 or NEGATIVE with high impact)
                    if (sentiment_score < -0.7 or 
                        (sentiment_label == 'NEGATIVE' and stock.get('impact_level') == 'HIGH')):
                        stock['watchlist_override'] = True
                        stock['override_reason'] = 'Very negative news - potential sell signal'
                        filtered_stocks.append(stock)
                        logger.info(f"Including {symbol} from watchlist due to very negative news")
                    else:
                        logger.info(f"Excluding {symbol} from recommendations - already in watchlist")
                else:
                    logger.info(f"Excluding {symbol} from recommendations - already in watchlist")
            
            logger.info(f"Filtered {len(filtered_stocks)} stocks from {len(stocks)} (removed {len(stocks) - len(filtered_stocks)} watchlist stocks)")
            return filtered_stocks
            
        except Exception as e:
            logger.error(f"Error filtering watchlist stocks: {str(e)}")
            return stocks  # Return all stocks if filtering fails
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        try:
            # Clean all caches first
            self.articles_cache = self._clean_expired_cache(self.articles_cache, self.articles_cache_hours)
            self.stocks_cache = self._clean_expired_cache(self.stocks_cache, self.stocks_cache_hours)
            self.analysis_cache = self._clean_expired_cache(self.analysis_cache, self.analysis_cache_hours)
            
            return {
                'articles_cache_size': len(self.articles_cache),
                'stocks_cache_size': len(self.stocks_cache),
                'analysis_cache_size': len(self.analysis_cache),
                'articles_cache_hours': self.articles_cache_hours,
                'stocks_cache_hours': self.stocks_cache_hours,
                'analysis_cache_hours': self.analysis_cache_hours,
                'cache_dir': self.cache_dir
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {}
    
    def clear_cache(self, cache_type: str = 'all'):
        """Clear cache entries."""
        try:
            if cache_type in ['all', 'articles']:
                self.articles_cache = {}
                self._save_cache(self.articles_cache, self.articles_cache_file)
                logger.info("Cleared articles cache")
            
            if cache_type in ['all', 'stocks']:
                self.stocks_cache = {}
                self._save_cache(self.stocks_cache, self.stocks_cache_file)
                logger.info("Cleared stocks cache")
            
            if cache_type in ['all', 'analysis']:
                self.analysis_cache = {}
                self._save_cache(self.analysis_cache, self.analysis_cache_file)
                logger.info("Cleared analysis cache")
                
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
