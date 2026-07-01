#!/usr/bin/env python3
"""
Test script for watchlist Firebase sync functionality.
"""

import sys
import os
import streamlit as st

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.firebase_integration import FirebaseSync
from components.watchlist_manager import WatchlistManager

def test_watchlist_sync():
    """Test watchlist sync functionality."""
    print("Testing Watchlist Firebase Sync...")
    
    # Initialize session state
    if not hasattr(st, 'session_state'):
        class MockSessionState:
            def __init__(self):
                self.data = {}
            
            def get(self, key, default=None):
                return self.data.get(key, default)
            
            def __contains__(self, key):
                return key in self.data
            
            def __setitem__(self, key, value):
                self.data[key] = value
            
            def __getitem__(self, key):
                return self.data[key]
        
        st.session_state = MockSessionState()
    
    # Initialize Firebase sync
    firebase_sync = FirebaseSync()
    
    # Set user ID
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "test_user_12345"
    firebase_sync.set_user_id(st.session_state.user_id)
    
    # Initialize watchlist manager
    watchlist_manager = WatchlistManager(firebase_sync)
    
    # Test adding to watchlist
    test_stock = {
        'symbol': 'RELIANCE.NS',
        'company_name': 'Reliance Industries Ltd',
        'current_price': 2500.0,
        'target_price': 2600.0,
        'stop_loss': 2400.0,
        'recommendation': 'BUY',
        'confidence': 0.85,
        'notes': 'Test stock for sync'
    }
    
    print(f"Adding {test_stock['symbol']} to watchlist...")
    success = watchlist_manager.add_to_watchlist(test_stock)
    print(f"Add success: {success}")
    
    # Check watchlist
    watchlist = watchlist_manager.get_watchlist()
    print(f"Watchlist size: {len(watchlist)}")
    if watchlist:
        print(f"First item: {watchlist[0]['symbol']}")
    
    # Test sync status
    sync_status = watchlist_manager.sync_status()
    print(f"Sync status: {sync_status}")
    
    # Test updating watchlist item
    updates = {
        'target_price': 2650.0,
        'notes': 'Updated target price'
    }
    
    print(f"Updating {test_stock['symbol']}...")
    update_success = watchlist_manager.update_watchlist_item(test_stock['symbol'], updates)
    print(f"Update success: {update_success}")
    
    # Check updated watchlist
    updated_watchlist = watchlist_manager.get_watchlist()
    if updated_watchlist:
        updated_item = updated_watchlist[0]
        print(f"Updated target price: {updated_item.get('target_price')}")
        print(f"Updated notes: {updated_item.get('notes')}")
    
    # Test removing from watchlist
    print(f"Removing {test_stock['symbol']} from watchlist...")
    remove_success = watchlist_manager.remove_from_watchlist(test_stock['symbol'])
    print(f"Remove success: {remove_success}")
    
    # Final watchlist check
    final_watchlist = watchlist_manager.get_watchlist()
    print(f"Final watchlist size: {len(final_watchlist)}")
    
    print("\nWatchlist sync test completed!")

if __name__ == "__main__":
    test_watchlist_sync()
