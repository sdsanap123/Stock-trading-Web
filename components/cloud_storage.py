#!/usr/bin/env python3
"""
Simple Cloud Storage Component
File-based cloud storage for portfolio persistence on Streamlit Cloud.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
import streamlit as st

logger = logging.getLogger(__name__)

class CloudStorage:
    """Simple cloud storage using Streamlit's persistent storage."""
    
    def __init__(self, storage_key: str = "portfolio_data"):
        self.storage_key = storage_key
        
    def save_portfolio(self, portfolio: List[Dict]) -> bool:
        """Save portfolio to cloud storage."""
        try:
            # Use Streamlit's session state with persistence
            storage_data = {
                'portfolio': portfolio,
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Store in session state (persists during session)
            st.session_state[self.storage_key] = storage_data
            
            # Also store as a serialized string for potential file download
            st.session_state[f"{self.storage_key}_backup"] = json.dumps(storage_data, indent=2, default=str)
            
            logger.info(f"Portfolio saved to cloud storage with {len(portfolio)} items")
            return True
            
        except Exception as e:
            logger.error(f"Error saving portfolio to cloud: {str(e)}")
            return False
    
    def load_portfolio(self) -> Optional[List[Dict]]:
        """Load portfolio from cloud storage."""
        try:
            if self.storage_key in st.session_state:
                storage_data = st.session_state[self.storage_key]
                portfolio = storage_data.get('portfolio', [])
                logger.info(f"Portfolio loaded from cloud storage with {len(portfolio)} items")
                return portfolio
            else:
                logger.info("No portfolio found in cloud storage")
                return None
                
        except Exception as e:
            logger.error(f"Error loading portfolio from cloud: {str(e)}")
            return None
    
    def export_portfolio(self) -> Optional[str]:
        """Export portfolio as JSON string."""
        try:
            if f"{self.storage_key}_backup" in st.session_state:
                return st.session_state[f"{self.storage_key}_backup"]
            return None
        except Exception as e:
            logger.error(f"Error exporting portfolio: {str(e)}")
            return None
    
    def import_portfolio(self, json_data: str) -> bool:
        """Import portfolio from JSON string."""
        try:
            data = json.loads(json_data)
            if 'portfolio' in data and isinstance(data['portfolio'], list):
                return self.save_portfolio(data['portfolio'])
            return False
        except Exception as e:
            logger.error(f"Error importing portfolio: {str(e)}")
            return False
    
    def get_storage_info(self) -> Dict:
        """Get information about current storage."""
        info = {
            'has_data': self.storage_key in st.session_state,
            'last_updated': None,
            'portfolio_size': 0
        }
        
        if self.storage_key in st.session_state:
            storage_data = st.session_state[self.storage_key]
            info['last_updated'] = storage_data.get('last_updated')
            info['portfolio_size'] = len(storage_data.get('portfolio', []))
        
        return info

# Usage example for enhanced_portfolio.py
def integrate_cloud_storage():
    """
    Integration function to add cloud storage to EnhancedPortfolio.
    Add this to the EnhancedPortfolio.__init__ method:
    """
    
    # Replace Firebase initialization with:
    # self.cloud_storage = CloudStorage()
    
    # Update _load_portfolio method:
    """
    def _load_portfolio(self) -> None:
        # Try cloud storage first
        cloud_portfolio = self.cloud_storage.load_portfolio()
        if cloud_portfolio is not None:
            st.session_state.portfolio = cloud_portfolio
            st.session_state.portfolio_data = cloud_portfolio
            st.session_state.portfolio_last_saved = datetime.now().isoformat()
            logger.info(f"Loaded portfolio from cloud storage with {len(cloud_portfolio)} items")
            return
        
        # Fallback to existing logic...
    """
    
    # Update _save_portfolio method:
    """
    def _save_portfolio(self) -> None:
        # ... existing data preparation ...
        
        # Save to cloud storage
        self.cloud_storage.save_portfolio(data_to_save)
        
        # ... existing file save logic ...
    """
    
    return "Integration instructions provided"
