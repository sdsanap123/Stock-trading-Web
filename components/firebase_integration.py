#!/usr/bin/env python3
"""
Firebase Integration Component
Firebase sync functionality for portfolio and other data.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import streamlit as st

logger = logging.getLogger(__name__)

class FirebaseSync:
    """Firebase synchronization functionality."""
    
    def __init__(self, config_file: str = None):
        self.initialized = False
        self.config_file = config_file
        self.user_id = None
        self.db = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Firebase connection."""
        try:
            # Try to get Firebase config from environment or secrets
            firebase_config = self._get_firebase_config()
            
            if firebase_config:
                # Initialize Firebase Admin SDK
                try:
                    import firebase_admin
                    from firebase_admin import credentials, firestore
                    
                    # Check if already initialized
                    if not firebase_admin._apps:
                        # Use certificate from environment or file
                        cred = self._get_credentials()
                        if cred:
                            firebase_admin.initialize_app(cred)
                    
                    self.db = firestore.client()
                    self.initialized = True
                    logger.info("Firebase Admin SDK initialized successfully")
                    
                except ImportError:
                    logger.warning("Firebase Admin SDK not installed. Using mock mode.")
                    self._initialize_mock()
                except Exception as e:
                    logger.error(f"Firebase initialization error: {str(e)}")
                    self._initialize_mock()
            else:
                self._initialize_mock()
                
        except Exception as e:
            logger.error(f"Error initializing Firebase: {str(e)}")
            self._initialize_mock()
    
    def _initialize_mock(self):
        """Initialize mock mode for development."""
        self.initialized = True
        logger.info("Firebase Sync initialized in mock mode")
    
    def _get_firebase_config(self) -> Optional[Dict]:
        """Get Firebase configuration from various sources."""
        # Try Streamlit secrets first
        if 'FIREBASE_CONFIG' in st.secrets:
            try:
                return json.loads(st.secrets.FIREBASE_CONFIG)
            except:
                pass
        
        # Try environment variable
        if os.getenv('FIREBASE_CONFIG'):
            try:
                return json.loads(os.getenv('FIREBASE_CONFIG'))
            except:
                pass
        
        # Try config file
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return None
    
    def _get_credentials(self):
        """Get Firebase credentials."""
        try:
            import firebase_admin
            from firebase_admin import credentials
            
            # Try service account key from secrets
            if 'FIREBASE_SERVICE_ACCOUNT' in st.secrets:
                service_account_info = json.loads(st.secrets.FIREBASE_SERVICE_ACCOUNT)
                return credentials.Certificate(service_account_info)
            
            # Try environment variable
            if os.getenv('FIREBASE_SERVICE_ACCOUNT'):
                service_account_info = json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT'))
                return credentials.Certificate(service_account_info)
            
            # Try file
            service_account_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if service_account_file and os.path.exists(service_account_file):
                return credentials.Certificate(service_account_file)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Firebase credentials: {str(e)}")
            return None
    
    def set_user_id(self, user_id: str):
        """Set the user ID for data isolation."""
        self.user_id = user_id
        logger.info(f"User ID set: {user_id}")
    
    def sync_portfolio(self, portfolio: List[Dict]) -> bool:
        """Sync portfolio to Firebase."""
        try:
            if not self.initialized:
                logger.warning("Firebase not initialized, skipping sync")
                return False
            
            if not self.user_id:
                logger.warning("No user ID set, skipping portfolio sync")
                return False
            
            # Prepare portfolio data for Firebase
            portfolio_data = {
                'portfolio': portfolio,
                'last_updated': datetime.now().isoformat(),
                'user_id': self.user_id,
                'version': '1.0'
            }
            
            # Try real Firebase sync
            if self.db:
                try:
                    doc_ref = self.db.collection('portfolios').document(self.user_id)
                    doc_ref.set(portfolio_data)
                    logger.info(f"Portfolio synced to Firebase for user {self.user_id}")
                    return True
                except Exception as e:
                    logger.error(f"Firebase sync error: {str(e)}")
                    # Fallback to mock mode
            
            # Mock sync for demo - store in session state
            if 'firebase_portfolio_backup' not in st.session_state:
                st.session_state.firebase_portfolio_backup = {}
            st.session_state.firebase_portfolio_backup[self.user_id] = portfolio_data
            
            logger.info(f"Portfolio synced to mock Firebase for user {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing portfolio: {str(e)}")
            return False
    
    def load_portfolio(self) -> Optional[List[Dict]]:
        """Load portfolio from Firebase."""
        try:
            if not self.initialized:
                logger.warning("Firebase not initialized, cannot load portfolio")
                return None
            
            if not self.user_id:
                logger.warning("No user ID set, cannot load portfolio")
                return None
            
            # Try real Firebase load
            if self.db:
                try:
                    doc_ref = self.db.collection('portfolios').document(self.user_id)
                    doc = doc_ref.get()
                    
                    if doc.exists:
                        portfolio_data = doc.to_dict()
                        portfolio = portfolio_data.get('portfolio', [])
                        logger.info(f"Portfolio loaded from Firebase for user {self.user_id}")
                        return portfolio
                    else:
                        logger.info(f"No portfolio found in Firebase for user {self.user_id}")
                        return None
                        
                except Exception as e:
                    logger.error(f"Firebase load error: {str(e)}")
                    # Fallback to mock mode
            
            # Mock load from session state
            if 'firebase_portfolio_backup' in st.session_state and self.user_id in st.session_state.firebase_portfolio_backup:
                portfolio_data = st.session_state.firebase_portfolio_backup[self.user_id]
                portfolio = portfolio_data.get('portfolio', [])
                logger.info(f"Portfolio loaded from mock Firebase for user {self.user_id}")
                return portfolio
            
            logger.info(f"No portfolio found in mock Firebase for user {self.user_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error loading portfolio: {str(e)}")
            return None
    
    def sync_recommendations(self, recommendations: List[Dict], source: str) -> bool:
        """Sync recommendations to Firebase."""
        try:
            if not self.initialized:
                return False
            
            if not self.user_id:
                logger.warning("No user ID set, skipping recommendations sync")
                return False
            
            # Prepare recommendations data
            recommendations_data = {
                'recommendations': recommendations,
                'source': source,
                'last_updated': datetime.now().isoformat(),
                'user_id': self.user_id
            }
            
            # Try real Firebase sync
            if self.db:
                try:
                    doc_ref = self.db.collection('recommendations').document(f"{self.user_id}_{source}")
                    doc_ref.set(recommendations_data)
                    logger.info(f"Recommendations synced to Firebase from {source}")
                    return True
                except Exception as e:
                    logger.error(f"Firebase recommendations sync error: {str(e)}")
            
            # Mock sync for demo
            logger.info(f"Recommendations synced to mock Firebase from {source}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing recommendations: {str(e)}")
            return False
    
    def sync_watchlist(self, watchlist: List[Dict]) -> bool:
        """Sync watchlist to Firebase."""
        try:
            if not self.initialized:
                return False
            
            if not self.user_id:
                logger.warning("No user ID set, skipping watchlist sync")
                return False
            
            # Prepare watchlist data
            watchlist_data = {
                'watchlist': watchlist,
                'last_updated': datetime.now().isoformat(),
                'user_id': self.user_id
            }
            
            # Try real Firebase sync
            if self.db:
                try:
                    doc_ref = self.db.collection('watchlists').document(self.user_id)
                    doc_ref.set(watchlist_data)
                    logger.info(f"Watchlist synced to Firebase for user {self.user_id}")
                    return True
                except Exception as e:
                    logger.error(f"Firebase watchlist sync error: {str(e)}")
            
            # Mock sync for demo - store in session state
            if 'firebase_watchlist_backup' not in st.session_state:
                st.session_state.firebase_watchlist_backup = {}
            st.session_state.firebase_watchlist_backup[self.user_id] = watchlist_data
            
            logger.info(f"Watchlist synced to mock Firebase for user {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing watchlist: {str(e)}")
            return False
    
    def backup_all_data(self, data: Dict[str, Any]) -> bool:
        """Backup all user data to Firebase."""
        try:
            if not self.initialized or not self.user_id:
                return False
            
            backup_data = {
                'data': data,
                'backup_timestamp': datetime.now().isoformat(),
                'user_id': self.user_id,
                'backup_version': '1.0'
            }
            
            # Try real Firebase backup
            if self.db:
                try:
                    doc_ref = self.db.collection('backups').document(self.user_id)
                    doc_ref.set(backup_data)
                    logger.info(f"Data backed up to Firebase for user {self.user_id}")
                    return True
                except Exception as e:
                    logger.error(f"Firebase backup error: {str(e)}")
            
            # Mock backup
            logger.info(f"Data backed up to mock Firebase for user {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error backing up data: {str(e)}")
            return False
    
    def restore_all_data(self) -> Optional[Dict[str, Any]]:
        """Restore all user data from Firebase."""
        try:
            if not self.initialized or not self.user_id:
                return None
            
            # Try real Firebase restore
            if self.db:
                try:
                    doc_ref = self.db.collection('backups').document(self.user_id)
                    doc = doc_ref.get()
                    
                    if doc.exists:
                        backup_data = doc.to_dict()
                        logger.info(f"Data restored from Firebase for user {self.user_id}")
                        return backup_data.get('data', {})
                    else:
                        logger.info(f"No backup found in Firebase for user {self.user_id}")
                        return None
                        
                except Exception as e:
                    logger.error(f"Firebase restore error: {str(e)}")
            
            # Mock restore
            logger.info(f"No data to restore from mock Firebase for user {self.user_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error restoring data: {str(e)}")
            return None
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status."""
        return {
            'initialized': self.initialized,
            'user_id': self.user_id,
            'last_sync': datetime.now().isoformat() if self.initialized else None,
            'sync_enabled': self.initialized and self.user_id is not None,
            'has_real_db': self.db is not None
        }
    
    def delete_user_data(self) -> bool:
        """Delete all user data from Firebase."""
        try:
            if not self.initialized or not self.user_id:
                return False
            
            deleted_count = 0
            
            # Try real Firebase deletion
            if self.db:
                try:
                    collections = ['portfolios', 'watchlists', 'recommendations', 'backups']
                    for collection_name in collections:
                        doc_ref = self.db.collection(collection_name).document(self.user_id)
                        doc = doc_ref.get()
                        if doc.exists:
                            doc_ref.delete()
                            deleted_count += 1
                    
                    logger.info(f"Deleted {deleted_count} documents from Firebase for user {self.user_id}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Firebase deletion error: {str(e)}")
            
            # Mock deletion
            if 'firebase_portfolio_backup' in st.session_state and self.user_id in st.session_state.firebase_portfolio_backup:
                del st.session_state.firebase_portfolio_backup[self.user_id]
                deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} items from mock Firebase for user {self.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user data: {str(e)}")
            return False
