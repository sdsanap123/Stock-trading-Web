#!/usr/bin/env python3
"""
Test script for API key saving functionality
"""

import os
import sys

def test_api_key_saving():
    """Test the API key saving and loading functionality."""
    
    # Add the current directory to Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from app import StreamlitTradingApp
        
        # Create app instance
        app = StreamlitTradingApp()
        
        # Test saving API key
        test_key = "gsk_test_key_12345"
        print("Testing API key saving...")
        
        # Save the key
        if app.save_api_key('groq', test_key):
            print("✅ API key saved successfully")
        else:
            print("❌ Failed to save API key")
            return False
        
        # Load the key
        loaded_key = app.load_saved_api_key('groq')
        if loaded_key == test_key:
            print("✅ API key loaded successfully")
        else:
            print(f"❌ Failed to load API key. Expected: {test_key}, Got: {loaded_key}")
            return False
        
        # Delete the key
        if app.delete_saved_api_key('groq'):
            print("✅ API key deleted successfully")
        else:
            print("❌ Failed to delete API key")
            return False
        
        # Verify deletion
        loaded_key_after_delete = app.load_saved_api_key('groq')
        if loaded_key_after_delete == "":
            print("✅ API key deletion verified")
        else:
            print(f"❌ API key still exists after deletion: {loaded_key_after_delete}")
            return False
        
        print("\n🎉 All API key management tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_key_saving()
