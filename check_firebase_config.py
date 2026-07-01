#!/usr/bin/env python3
"""
Check Firebase configuration in secrets.
"""

import os
import sys
import streamlit as st

def check_firebase_config():
    """Check if Firebase is properly configured."""
    print("Checking Firebase Configuration...")
    
    # Initialize session state for testing
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
    
    # Check Firebase integration
    try:
        from components.firebase_integration import FirebaseSync
        
        # Initialize Firebase
        firebase_sync = FirebaseSync()
        
        print(f"Firebase initialized: {firebase_sync.initialized}")
        print(f"Has real database: {hasattr(firebase_sync, 'db') and firebase_sync.db is not None}")
        
        # Check secrets
        try:
            service_account = st.secrets.get('FIREBASE_SERVICE_ACCOUNT')
            if service_account:
                print("FIREBASE_SERVICE_ACCOUNT found in secrets")
                if isinstance(service_account, str) and service_account.strip():
                    print("Service account key is not empty")
                    # Check if it's properly formatted JSON
                    try:
                        import json
                        parsed = json.loads(service_account)
                        print("Service account is valid JSON")
                        print(f"Project ID: {parsed.get('project_id', 'Not found')}")
                        print(f"Client Email: {parsed.get('client_email', 'Not found')}")
                    except json.JSONDecodeError:
                        print("Service account is not valid JSON")
                else:
                    print("Service account key is empty")
            else:
                print("FIREBASE_SERVICE_ACCOUNT not found in secrets")
                
                # Check alternative configuration
                project_id = st.secrets.get('FIREBASE_PROJECT_ID')
                private_key = st.secrets.get('FIREBASE_PRIVATE_KEY')
                client_email = st.secrets.get('FIREBASE_CLIENT_EMAIL')
                
                if project_id and private_key and client_email:
                    print("Using alternative Firebase configuration")
                    print(f"Project ID: {project_id}")
                    print(f"Client Email: {client_email}")
                else:
                    print("No Firebase configuration found")
                    
        except Exception as e:
            print(f"Error checking secrets: {str(e)}")
        
        # Test user ID generation
        if 'user_id' not in st.session_state:
            import hashlib
            import time
            user_string = f"test_user_{int(time.time())}_{hash(str(st.session_state))}"
            user_id = hashlib.md5(user_string.encode()).hexdigest()[:16]
            st.session_state.user_id = user_id
            firebase_sync.set_user_id(user_id)
            print(f"Generated test user ID: {user_id}")
        
        # Test sync status
        sync_status = firebase_sync.get_sync_status()
        print(f"Sync status: {sync_status}")
        
        # Test portfolio sync
        test_portfolio = [
            {
                'symbol': 'TEST.NS',
                'quantity': 10,
                'buy_price': 1000.0,
                'buy_date': '2023-01-01',
                'notes': 'Test portfolio item'
            }
        ]
        
        portfolio_sync_success = firebase_sync.sync_portfolio(test_portfolio)
        print(f"Portfolio sync test: {'Success' if portfolio_sync_success else 'Failed'}")
        
        # Test watchlist sync
        test_watchlist = [
            {
                'symbol': 'WATCH.NS',
                'company_name': 'Watch Test Company',
                'current_price': 500.0,
                'target_price': 550.0,
                'stop_loss': 450.0,
                'recommendation': 'BUY',
                'confidence': 0.8,
                'added_date': '2023-01-01',
                'last_updated': '2023-01-01',
                'status': 'ACTIVE',
                'notes': 'Test watchlist item'
            }
        ]
        
        watchlist_sync_success = firebase_sync.sync_watchlist(test_watchlist)
        print(f"Watchlist sync test: {'Success' if watchlist_sync_success else 'Failed'}")
        
        print("\nFirebase configuration check completed!")
        
    except ImportError as e:
        print(f"Import error: {str(e)}")
        print("Make sure firebase-admin is installed: pip install firebase-admin")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_firebase_config()
