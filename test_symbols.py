"""
Symbol Lookup Tester
"""
import sys
import os
import pandas as pd

# Add the parent directory to the path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import StreamlitTradingApp

def test_symbol_lookup():
    """Test the symbol lookup functionality."""
    print("=== Testing Symbol Lookup ===\n")
    
    # Initialize the app
    app = StreamlitTradingApp()
    
    # Test cases
    test_cases = [
        # (input, expected_symbol, description)
        ("RELIANCE", "RELIANCE.NS", "Standard NSE stock"),
        ("TATA MOTORS", "TATAMOTORS.NS", "Company name with space"),
        ("HDFC BANK", "HDFCBANK.NS", "Bank stock"),
        ("INFY.NS", "INFY.NS", "Already has .NS suffix"),
        ("TCS", "TCS.NS", "Standard NSE stock"),
        ("NONEXISTENT", None, "Non-existent symbol"),
        ("", None, "Empty string"),
        (None, None, "None input")
    ]
    
    # Add some random samples from EQUITY_L.csv
    equity_symbols = app._load_equity_symbols()
    samples = list(equity_symbols.items())[:3]  # Get first 3 items
    for company, symbol in samples:
        test_cases.append((company, f"{symbol}.NS", f"Company: {company}"))
        test_cases.append((symbol, f"{symbol}.NS", f"Symbol: {symbol}"))
    
    # Run tests
    passed = 0
    for i, (test_input, expected, description) in enumerate(test_cases, 1):
        print(f"Test {i}: {description}")
        print(f"  Input:    {test_input}")
        print(f"  Expected: {expected}")
        
        try:
            result = app._get_stock_symbol(test_input)
            print(f"  Result:   {result}")
            
            if result == expected or (expected is None and result is None):
                print("  ✅ PASSED")
                passed += 1
            else:
                print(f"  ❌ FAILED (expected {expected}, got {result})")
        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
        
        print()
    
    # Print summary
    print(f"\n=== Test Summary ===")
    print(f"Total tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(test_cases) - passed}")
    print(f"Success rate: {(passed/len(test_cases))*100:.1f}%")

if __name__ == "__main__":
    test_symbol_lookup()
