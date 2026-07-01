#!/usr/bin/env python3
"""
Data Persistence Manager Component
Manages saving and loading of recommendations, watchlist, and swing trading strategies with datewise organization.
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class RecommendationData:
    """Data structure for recommendation storage."""
    symbol: str
    company_name: str
    current_price: float
    recommendation: str
    confidence: float
    target_price: float
    stop_loss: float
    reasoning: str
    technical_data: Dict
    fundamental_data: Dict
    groq_analysis: Dict
    gemini_analysis: Dict
    swing_plan: Dict
    swing_validation: Dict
    created_at: str
    expiry_date: str

@dataclass
class WatchlistData:
    """Data structure for watchlist storage."""
    symbol: str
    company_name: str
    entry_price: float
    current_price: float
    target_price: float
    stop_loss: float
    recommendation: str
    confidence: float
    added_date: str
    last_updated: str
    status: str
    notes: str

@dataclass
class SwingStrategyData:
    """Data structure for swing strategy storage."""
    symbol: str
    company_name: str
    strategy_name: str
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: int
    investment_amount: float
    risk_amount: float
    risk_reward_ratio: float
    confidence: float
    entry_date: str
    expected_exit_date: str
    holding_period_days: int
    status: str
    created_at: str

class DataPersistenceManager:
    """Manages data persistence for recommendations, watchlist, and swing strategies."""
    
    def __init__(self, data_dir: str = "saved_data"):
        self.data_dir = data_dir
        self.recommendations_file = os.path.join(data_dir, "recommendations.json")
        self.watchlist_file = os.path.join(data_dir, "watchlist.json")
        self.swing_strategies_file = os.path.join(data_dir, "swing_strategies.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing data
        self.recommendations = self._load_recommendations()
        self.watchlist = self._load_watchlist()
        self.swing_strategies = self._load_swing_strategies()
        
        # Clean up expired data
        self._cleanup_expired_data()
        
        logger.info("DataPersistenceManager initialized")
    
    def _load_recommendations(self) -> Dict[str, List[Dict]]:
        """Load recommendations from file, organized by date."""
        try:
            if os.path.exists(self.recommendations_file):
                with open(self.recommendations_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        return {}
                    return json.loads(content)
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in recommendations file: {str(e)}")
            # Try to backup and recreate the file
            try:
                backup_file = self.recommendations_file + '.backup'
                if os.path.exists(self.recommendations_file):
                    os.rename(self.recommendations_file, backup_file)
                logger.info(f"Backed up corrupted file to {backup_file}")
            except Exception as backup_error:
                logger.error(f"Failed to backup corrupted file: {str(backup_error)}")
            return {}
        except Exception as e:
            logger.error(f"Error loading recommendations: {str(e)}")
            return {}
    
    def _load_watchlist(self) -> List[Dict]:
        """Load watchlist from file."""
        try:
            if os.path.exists(self.watchlist_file):
                with open(self.watchlist_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        return []
                    return json.loads(content)
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in watchlist file: {str(e)}")
            # Try to backup and recreate the file
            try:
                backup_file = self.watchlist_file + '.backup'
                if os.path.exists(self.watchlist_file):
                    os.rename(self.watchlist_file, backup_file)
                logger.info(f"Backed up corrupted file to {backup_file}")
            except Exception as backup_error:
                logger.error(f"Failed to backup corrupted file: {str(backup_error)}")
            return []
        except Exception as e:
            logger.error(f"Error loading watchlist: {str(e)}")
            return []
    
    def _load_swing_strategies(self) -> Dict[str, List[Dict]]:
        """Load swing strategies from file, organized by date."""
        try:
            if os.path.exists(self.swing_strategies_file):
                with open(self.swing_strategies_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        return {}
                    return json.loads(content)
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in swing strategies file: {str(e)}")
            # Try to backup and recreate the file
            try:
                backup_file = self.swing_strategies_file + '.backup'
                if os.path.exists(self.swing_strategies_file):
                    os.rename(self.swing_strategies_file, backup_file)
                logger.info(f"Backed up corrupted file to {backup_file}")
            except Exception as backup_error:
                logger.error(f"Failed to backup corrupted file: {str(backup_error)}")
            return {}
        except Exception as e:
            logger.error(f"Error loading swing strategies: {str(e)}")
            return {}
    
    def _save_recommendations(self):
        """Save recommendations to file."""
        try:
            # Convert numpy types to native Python types for JSON serialization
            serializable_data = self._convert_to_serializable(self.recommendations)
            # Clean up problematic characters in text fields
            serializable_data = self._clean_text_fields(serializable_data)
            with open(self.recommendations_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving recommendations: {str(e)}")
    
    def _save_watchlist(self):
        """Save watchlist to file."""
        try:
            # Convert numpy types to native Python types for JSON serialization
            serializable_data = self._convert_to_serializable(self.watchlist)
            # Clean up problematic characters in text fields
            serializable_data = self._clean_text_fields(serializable_data)
            with open(self.watchlist_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving watchlist: {str(e)}")
    
    def _save_swing_strategies(self):
        """Save swing strategies to file."""
        try:
            # Convert numpy types to native Python types for JSON serialization
            serializable_data = self._convert_to_serializable(self.swing_strategies)
            # Clean up problematic characters in text fields
            serializable_data = self._clean_text_fields(serializable_data)
            with open(self.swing_strategies_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving swing strategies: {str(e)}")
    
    def _convert_to_serializable(self, obj):
        """Convert numpy types and other non-serializable objects to JSON serializable types."""
        import numpy as np
        
        if isinstance(obj, dict):
            return {key: self._convert_to_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, 'item'):  # For numpy scalars
            return obj.item()
        else:
            return obj
    
    def _clean_text_fields(self, obj):
        """Clean problematic characters from text fields to prevent JSON parsing issues."""
        import re
        
        if isinstance(obj, dict):
            cleaned_dict = {}
            for key, value in obj.items():
                if isinstance(value, str):
                    # Remove or replace problematic characters
                    cleaned_value = re.sub(r'[^\x00-\x7F]+', '', value)  # Remove non-ASCII characters
                    cleaned_value = cleaned_value.replace('\x00', '')  # Remove null bytes
                    cleaned_value = cleaned_value.replace('\u0000', '')  # Remove Unicode null
                    cleaned_dict[key] = cleaned_value
                else:
                    cleaned_dict[key] = self._clean_text_fields(value)
            return cleaned_dict
        elif isinstance(obj, list):
            return [self._clean_text_fields(item) for item in obj]
        elif isinstance(obj, str):
            # Clean string values
            cleaned = re.sub(r'[^\x00-\x7F]+', '', obj)  # Remove non-ASCII characters
            cleaned = cleaned.replace('\x00', '')  # Remove null bytes
            cleaned = cleaned.replace('\u0000', '')  # Remove Unicode null
            return cleaned
        else:
            return obj
    
    def _cleanup_expired_data(self):
        """Remove expired recommendations (older than 7 days)."""
        try:
            current_date = datetime.now()
            expired_dates = []
            
            for date_str in self.recommendations.keys():
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    if (current_date - date_obj).days > 7:
                        expired_dates.append(date_str)
                except ValueError:
                    # Invalid date format, remove it
                    expired_dates.append(date_str)
            
            # Remove expired dates
            for date_str in expired_dates:
                del self.recommendations[date_str]
                logger.info(f"Removed expired recommendations for {date_str}")
            
            if expired_dates:
                self._save_recommendations()
                
        except Exception as e:
            logger.error(f"Error cleaning up expired data: {str(e)}")
    
    def save_recommendations(self, recommendations: List[Dict], date_str: str = None) -> bool:
        """Save recommendations for a specific date."""
        try:
            if date_str is None:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            # Convert recommendations to serializable format
            serializable_recs = []
            for rec in recommendations:
                # Create expiry date (7 days from now)
                expiry_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                
                rec_data = {
                    'symbol': rec.get('symbol', ''),
                    'company_name': rec.get('company_name', ''),
                    'current_price': rec.get('current_price', 0),
                    'recommendation': rec.get('recommendation', ''),
                    'confidence': rec.get('confidence', 0),
                    'target_price': rec.get('target_price', 0),
                    'stop_loss': rec.get('stop_loss', 0),
                    'reasoning': rec.get('reasoning', ''),
                    'technical_data': rec.get('technical_data', {}),
                    'fundamental_data': rec.get('fundamental_data', {}),
                    'groq_analysis': rec.get('groq_analysis', {}),
                    'gemini_analysis': rec.get('gemini_analysis', {}),
                    'swing_plan': rec.get('swing_plan', {}),
                    'swing_validation': rec.get('swing_validation', {}),
                    'created_at': datetime.now().isoformat(),
                    'expiry_date': expiry_date
                }
                serializable_recs.append(rec_data)
            
            # Save to datewise structure
            self.recommendations[date_str] = serializable_recs
            self._save_recommendations()
            
            logger.info(f"Saved {len(serializable_recs)} recommendations for {date_str}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving recommendations: {str(e)}")
            return False
    
    def save_buy_recommendations(self, recommendations: List[Dict], date_str: str = None) -> bool:
        """Save only BUY recommendations for a specific date."""
        try:
            if date_str is None:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            # Filter only BUY recommendations
            buy_recommendations = []
            for rec in recommendations:
                recommendation = rec.get('recommendation', '').upper()
                action = rec.get('action', '').upper()
                
                # Check both 'recommendation' and 'action' fields for BUY
                if recommendation == 'BUY' or action == 'BUY':
                    buy_recommendations.append(rec)
            
            if not buy_recommendations:
                logger.info(f"No BUY recommendations found for {date_str}")
                return True
            
            # Convert BUY recommendations to serializable format
            serializable_buy_recs = []
            for rec in buy_recommendations:
                # Create expiry date (7 days from now)
                expiry_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                
                rec_data = {
                    'symbol': rec.get('symbol', ''),
                    'company_name': rec.get('company_name', ''),
                    'current_price': rec.get('current_price', 0),
                    'recommendation': 'BUY',  # Ensure it's marked as BUY
                    'confidence': rec.get('confidence', 0),
                    'target_price': rec.get('target_price', 0),
                    'stop_loss': rec.get('stop_loss', 0),
                    'reasoning': rec.get('reasoning', ''),
                    'technical_data': rec.get('technical_data', {}),
                    'fundamental_data': rec.get('fundamental_data', {}),
                    'groq_analysis': rec.get('groq_analysis', {}),
                    'gemini_analysis': rec.get('gemini_analysis', {}),
                    'swing_plan': rec.get('swing_plan', {}),
                    'swing_validation': rec.get('swing_validation', {}),
                    'created_at': datetime.now().isoformat(),
                    'expiry_date': expiry_date,
                    'is_buy_recommendation': True  # Flag to identify BUY recommendations
                }
                serializable_buy_recs.append(rec_data)
            
            # Save BUY recommendations to datewise structure
            if date_str not in self.recommendations:
                self.recommendations[date_str] = []
            
            # Add BUY recommendations to existing recommendations for the date
            self.recommendations[date_str].extend(serializable_buy_recs)
            self._save_recommendations()
            
            logger.info(f"Saved {len(serializable_buy_recs)} BUY recommendations for {date_str}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving BUY recommendations: {str(e)}")
            return False
    
    def get_buy_recommendations_by_date(self, date_str: str = None) -> List[Dict]:
        """Get BUY recommendations for a specific date."""
        try:
            if date_str is None:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            if date_str not in self.recommendations:
                return []
            
            # Filter only BUY recommendations
            buy_recommendations = []
            for rec in self.recommendations[date_str]:
                if rec.get('is_buy_recommendation', False) or rec.get('recommendation', '').upper() == 'BUY':
                    buy_recommendations.append(rec)
            
            logger.info(f"Retrieved {len(buy_recommendations)} BUY recommendations for {date_str}")
            return buy_recommendations
            
        except Exception as e:
            logger.error(f"Error getting BUY recommendations for {date_str}: {str(e)}")
            return []
    
    def get_all_buy_recommendations(self) -> Dict[str, List[Dict]]:
        """Get all BUY recommendations organized by date."""
        try:
            buy_recommendations_by_date = {}
            
            for date_str, recommendations in self.recommendations.items():
                buy_recs = []
                for rec in recommendations:
                    if rec.get('is_buy_recommendation', False) or rec.get('recommendation', '').upper() == 'BUY':
                        buy_recs.append(rec)
                
                if buy_recs:
                    buy_recommendations_by_date[date_str] = buy_recs
            
            logger.info(f"Retrieved BUY recommendations for {len(buy_recommendations_by_date)} dates")
            return buy_recommendations_by_date
            
        except Exception as e:
            logger.error(f"Error getting all BUY recommendations: {str(e)}")
            return {}
    
    def save_watchlist(self, watchlist: List[Dict]) -> bool:
        """Save watchlist data."""
        try:
            # Convert watchlist to serializable format
            serializable_watchlist = []
            for item in watchlist:
                watchlist_data = {
                    'symbol': item.get('symbol', ''),
                    'company_name': item.get('company_name', ''),
                    'entry_price': item.get('entry_price', 0),
                    'current_price': item.get('current_price', 0),
                    'target_price': item.get('target_price', 0),
                    'stop_loss': item.get('stop_loss', 0),
                    'recommendation': item.get('recommendation', ''),
                    'confidence': item.get('confidence', 0),
                    'added_date': item.get('added_date', datetime.now().isoformat()),
                    'last_updated': datetime.now().isoformat(),
                    'status': item.get('status', 'ACTIVE'),
                    'notes': item.get('notes', '')
                }
                serializable_watchlist.append(watchlist_data)
            
            self.watchlist = serializable_watchlist
            self._save_watchlist()
            
            logger.info(f"Saved {len(serializable_watchlist)} watchlist items")
            return True
            
        except Exception as e:
            logger.error(f"Error saving watchlist: {str(e)}")
            return False
    
    def save_swing_strategies(self, strategies: List[Dict], date_str: str = None) -> bool:
        """Save swing strategies for a specific date."""
        try:
            if date_str is None:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            # Convert strategies to serializable format
            serializable_strategies = []
            for strategy in strategies:
                strategy_data = {
                    'symbol': strategy.get('symbol', ''),
                    'company_name': strategy.get('company_name', ''),
                    'strategy_name': strategy.get('strategy_name', ''),
                    'entry_price': strategy.get('entry_price', 0),
                    'stop_loss': strategy.get('stop_loss', 0),
                    'take_profit': strategy.get('take_profit', 0),
                    'position_size': strategy.get('position_size', 0),
                    'investment_amount': strategy.get('investment_amount', 0),
                    'risk_amount': strategy.get('risk_amount', 0),
                    'risk_reward_ratio': strategy.get('risk_reward_ratio', 0),
                    'confidence': strategy.get('confidence', 0),
                    'entry_date': strategy.get('entry_date', datetime.now().isoformat()),
                    'expected_exit_date': strategy.get('expected_exit_date', ''),
                    'holding_period_days': strategy.get('holding_period_days', 7),
                    'status': strategy.get('status', 'ACTIVE'),
                    'created_at': datetime.now().isoformat()
                }
                serializable_strategies.append(strategy_data)
            
            # Get existing strategies for this date
            existing_strategies = self.swing_strategies.get(date_str, [])
            existing_symbols = {s['symbol'] for s in existing_strategies}
            
            # Add only new strategies that don't already exist for this symbol
            new_strategies = [
                s for s in serializable_strategies 
                if s['symbol'] not in existing_symbols
            ]
            
            # Combine existing and new strategies
            updated_strategies = existing_strategies + new_strategies
            self.swing_strategies[date_str] = updated_strategies
            
            self._save_swing_strategies()
            
            logger.info(f"Saved {len(new_strategies)} new swing strategies for {date_str} (total: {len(updated_strategies)})")
            return True
            
        except Exception as e:
            logger.error(f"Error saving swing strategies: {str(e)}")
            return False
    
    def get_swing_strategies(self) -> Dict[str, List[Dict]]:
        """Get all swing strategies organized by date."""
        try:
            return self.swing_strategies.copy()
        except Exception as e:
            logger.error(f"Error getting swing strategies: {str(e)}")
            return {}
    
    def get_swing_strategies_by_date(self, date_str: str = None) -> List[Dict]:
        """Get swing strategies for a specific date."""
        try:
            if date_str is None:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            return self.swing_strategies.get(date_str, [])
        except Exception as e:
            logger.error(f"Error getting swing strategies for {date_str}: {str(e)}")
            return []
    
    def get_recommendations_by_date(self, date_str: str = None) -> List[Dict]:
        """Get recommendations for a specific date."""
        try:
            if date_str is None:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            return self.recommendations.get(date_str, [])
        except Exception as e:
            logger.error(f"Error getting recommendations by date: {str(e)}")
            return []
    
    def get_all_recommendations(self) -> Dict[str, List[Dict]]:
        """Get all recommendations organized by date."""
        return self.recommendations.copy()
    
    def get_watchlist(self) -> List[Dict]:
        """Get current watchlist."""
        return self.watchlist.copy()
    
    def get_swing_strategies_by_date(self, date_str: str = None) -> List[Dict]:
        """Get swing strategies for a specific date."""
        try:
            if date_str is None:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            return self.swing_strategies.get(date_str, [])
        except Exception as e:
            logger.error(f"Error getting swing strategies by date: {str(e)}")
            return []
    
    def get_all_swing_strategies(self) -> Dict[str, List[Dict]]:
        """Get all swing strategies organized by date."""
        return self.swing_strategies.copy()
    
    def get_available_dates(self) -> List[str]:
        """Get all available dates for recommendations and strategies."""
        dates = set()
        dates.update(self.recommendations.keys())
        dates.update(self.swing_strategies.keys())
        return sorted(dates, reverse=True)  # Most recent first
    
    def delete_recommendations_by_date(self, date_str: str) -> bool:
        """Delete recommendations for a specific date."""
        try:
            if date_str in self.recommendations:
                del self.recommendations[date_str]
                self._save_recommendations()
                logger.info(f"Deleted recommendations for {date_str}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting recommendations for {date_str}: {str(e)}")
            return False
            
    def delete_swing_strategy(self, symbol: str, date_str: str = None) -> bool:
        """
        Delete a specific swing strategy by symbol and date.
        
        Args:
            symbol: The stock symbol to delete
            date_str: The date string in YYYY-MM-DD format. If None, uses today's date.
            
        Returns:
            bool: True if the strategy was deleted, False otherwise
        """
        try:
            if date_str is None:
                date_str = datetime.now().strftime("%Y-%m-%d")
                
            if date_str in self.swing_strategies:
                # Filter out the strategy with the matching symbol
                initial_count = len(self.swing_strategies[date_str])
                self.swing_strategies[date_str] = [
                    s for s in self.swing_strategies[date_str]
                    if s.get('symbol', '').upper() != symbol.upper()
                ]
                
                # If strategies were removed, save the changes
                if len(self.swing_strategies[date_str]) < initial_count:
                    self._save_swing_strategies()
                    logger.info(f"Deleted swing strategy for {symbol} on {date_str}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error deleting swing strategy for {symbol} on {date_str}: {str(e)}")
            return False
            
    def get_all_recommendations(self) -> Dict[str, List[Dict]]:
        """Get all recommendations organized by date."""
        return self.recommendations.copy()
        
    def get_watchlist(self) -> List[Dict]:
        """Get current watchlist."""
        return self.watchlist.copy()
        
    def clear_watchlist(self) -> bool:
        """Clear all watchlist items."""
        try:
            self.watchlist = []
            self._save_watchlist()
            logger.info("Watchlist cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing watchlist: {str(e)}")
            return False
    
    def get_data_summary(self) -> Dict:
        """Get summary of all saved data."""
        try:
            total_recommendations = sum(len(recs) for recs in self.recommendations.values())
            total_strategies = sum(len(strategies) for strategies in self.swing_strategies.values())
            
            return {
                'recommendations': {
                    'total_count': total_recommendations,
                    'dates_count': len(self.recommendations),
                    'available_dates': list(self.recommendations.keys())
                },
                'watchlist': {
                    'total_count': len(self.watchlist),
                    'active_count': len([item for item in self.watchlist if item.get('status') == 'ACTIVE'])
                },
                'swing_strategies': {
                    'total_count': total_strategies,
                    'dates_count': len(self.swing_strategies),
                    'available_dates': list(self.swing_strategies.keys())
                },
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting data summary: {str(e)}")
            return {}
    
    def export_data(self, export_type: str = "all") -> Dict:
        """Export data for backup or analysis."""
        try:
            export_data = {}
            
            if export_type in ["all", "recommendations"]:
                export_data['recommendations'] = self.recommendations
            
            if export_type in ["all", "watchlist"]:
                export_data['watchlist'] = self.watchlist
            
            if export_type in ["all", "swing_strategies"]:
                export_data['swing_strategies'] = self.swing_strategies
            
            export_data['export_timestamp'] = datetime.now().isoformat()
            export_data['export_type'] = export_type
            
            return export_data
        except Exception as e:
            logger.error(f"Error exporting data: {str(e)}")
            return {}
    
    def import_data(self, import_data: Dict) -> bool:
        """Import data from backup."""
        try:
            if 'recommendations' in import_data:
                self.recommendations.update(import_data['recommendations'])
                self._save_recommendations()
            
            if 'watchlist' in import_data:
                self.watchlist = import_data['watchlist']
                self._save_watchlist()
            
            if 'swing_strategies' in import_data:
                self.swing_strategies.update(import_data['swing_strategies'])
                self._save_swing_strategies()
            
            logger.info("Data imported successfully")
            return True
        except Exception as e:
            logger.error(f"Error importing data: {str(e)}")
            return False
