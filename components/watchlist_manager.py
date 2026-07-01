#!/usr/bin/env python3
"""
Watchlist Manager Component
Watchlist management functionality with Firebase sync.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import streamlit as st

logger = logging.getLogger(__name__)

class WatchlistManager:
    """Watchlist management functionality with Firebase sync."""
    
    def __init__(self, firebase_sync=None):
        self.firebase_sync = firebase_sync
        self._load_watchlist()
        logger.info("Watchlist Manager initialized")
    
    def _load_watchlist(self) -> None:
        """Load watchlist from Firebase or local storage."""
        try:
            # Try to load from Firebase first
            if self.firebase_sync and self.firebase_sync.user_id:
                firebase_watchlist = self._load_from_firebase()
                if firebase_watchlist is not None:
                    st.session_state.watchlist = firebase_watchlist
                    logger.info(f"Watchlist loaded from Firebase with {len(firebase_watchlist)} items")
                    return
            
            # Fallback to session state
            if 'watchlist' not in st.session_state:
                st.session_state.watchlist = []
                
            # Try to load from local file as backup
            self._load_from_file()
            
        except Exception as e:
            logger.error(f"Error loading watchlist: {str(e)}")
            st.session_state.watchlist = []
    
    def _load_from_firebase(self) -> Optional[List[Dict]]:
        """Load watchlist from Firebase."""
        try:
            if not self.firebase_sync or not self.firebase_sync.user_id:
                return None
            
            # Try real Firebase load
            if hasattr(self.firebase_sync, 'db') and self.firebase_sync.db:
                try:
                    doc_ref = self.firebase_sync.db.collection('watchlists').document(self.firebase_sync.user_id)
                    doc = doc_ref.get()
                    
                    if doc.exists:
                        watchlist_data = doc.to_dict()
                        watchlist = watchlist_data.get('watchlist', [])
                        logger.info(f"Watchlist loaded from Firebase for user {self.firebase_sync.user_id}")
                        return watchlist
                    else:
                        logger.info(f"No watchlist found in Firebase for user {self.firebase_sync.user_id}")
                        return None
                        
                except Exception as e:
                    logger.error(f"Firebase watchlist load error: {str(e)}")
            
            # Mock load from session state
            if 'firebase_watchlist_backup' in st.session_state and self.firebase_sync.user_id in st.session_state.firebase_watchlist_backup:
                watchlist_data = st.session_state.firebase_watchlist_backup[self.firebase_sync.user_id]
                watchlist = watchlist_data.get('watchlist', [])
                logger.info(f"Watchlist loaded from mock Firebase for user {self.firebase_sync.user_id}")
                return watchlist
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading watchlist from Firebase: {str(e)}")
            return None
    
    def _load_from_file(self) -> None:
        """Load watchlist from local file."""
        try:
            import os
            import json
            
            watchlist_file = os.path.join("saved_data", "watchlist.json")
            if os.path.exists(watchlist_file):
                with open(watchlist_file, 'r', encoding='utf-8') as f:
                    watchlist_data = json.load(f)
                
                if isinstance(watchlist_data, list):
                    st.session_state.watchlist = watchlist_data
                    # Sync to Firebase for future access
                    if self.firebase_sync:
                        self.firebase_sync.sync_watchlist(watchlist_data)
                    logger.info(f"Watchlist loaded from file with {len(watchlist_data)} items and synced to cloud")
                    
        except Exception as e:
            logger.error(f"Error loading watchlist from file: {str(e)}")
    
    def _save_watchlist(self) -> None:
        """Save watchlist to Firebase and local file."""
        try:
            if 'watchlist' not in st.session_state:
                return
            
            watchlist_data = st.session_state.watchlist
            
            # Save to Firebase
            if self.firebase_sync:
                self.firebase_sync.sync_watchlist(watchlist_data)
            
            # Save to local file as backup
            try:
                import os
                import json
                
                watchlist_file = os.path.join("saved_data", "watchlist.json")
                os.makedirs(os.path.dirname(watchlist_file), exist_ok=True)
                
                with open(watchlist_file, 'w', encoding='utf-8') as f:
                    json.dump(watchlist_data, f, indent=2, ensure_ascii=False, default=str)
                
                logger.info(f"Watchlist saved to file with {len(watchlist_data)} items")
                
            except Exception as file_error:
                logger.warning(f"File save failed (expected on cloud): {str(file_error)}")
                
        except Exception as e:
            logger.error(f"Error saving watchlist: {str(e)}")
    
    def add_to_watchlist(self, stock_data: Dict) -> bool:
        """Add stock to watchlist."""
        try:
            # Check if already exists
            for item in st.session_state.watchlist:
                if item.get('symbol') == stock_data.get('symbol'):
                    return False
            
            # Add to watchlist
            watchlist_item = {
                'symbol': stock_data.get('symbol'),
                'company_name': stock_data.get('company_name', ''),
                'entry_price': stock_data.get('current_price', 0),
                'current_price': stock_data.get('current_price', 0),
                'target_price': stock_data.get('target_price', 0),
                'stop_loss': stock_data.get('stop_loss', 0),
                'recommendation': stock_data.get('recommendation', 'HOLD'),
                'confidence': stock_data.get('confidence', 0),
                'added_date': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'status': 'ACTIVE',
                'notes': stock_data.get('notes', '')
            }
            
            st.session_state.watchlist.append(watchlist_item)
            self._save_watchlist()
            logger.info(f"Added {stock_data.get('symbol')} to watchlist")
            return True
            
        except Exception as e:
            logger.error(f"Error adding to watchlist: {str(e)}")
            return False
    
    def remove_from_watchlist(self, symbol: str) -> bool:
        """Remove stock from watchlist."""
        try:
            for i, item in enumerate(st.session_state.watchlist):
                if item.get('symbol') == symbol:
                    st.session_state.watchlist.pop(i)
                    self._save_watchlist()
                    logger.info(f"Removed {symbol} from watchlist")
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Error removing from watchlist: {str(e)}")
            return False
    
    def get_watchlist(self) -> List[Dict]:
        """Get current watchlist."""
        return st.session_state.get('watchlist', []).copy()
    
    def update_watchlist_item(self, symbol: str, updates: Dict) -> bool:
        """Update watchlist item."""
        try:
            for item in st.session_state.watchlist:
                if item.get('symbol') == symbol:
                    item.update(updates)
                    item['last_updated'] = datetime.now().isoformat()
                    self._save_watchlist()
                    logger.info(f"Updated {symbol} in watchlist")
                    return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating watchlist item: {str(e)}")
            return False
    
    def sync_status(self) -> Dict:
        """Get sync status for watchlist."""
        if self.firebase_sync:
            return self.firebase_sync.get_sync_status()
        return {
            'initialized': False,
            'user_id': None,
            'sync_enabled': False,
            'has_real_db': False
        }
