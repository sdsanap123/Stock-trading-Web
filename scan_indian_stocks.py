import os
import csv
import re
from typing import Set, List, Dict

def load_indian_stocks(csv_path: str) -> Set[str]:
    """
    Load and filter India-relevant stocks from EQUITY_L.csv
    
    Args:
        csv_path: Path to the EQUITY_L.csv file
        
    Returns:
        Set of stock symbols that are likely relevant to the Indian market
    """
    # List of keywords that indicate a stock is likely Indian
    indian_keywords = [
        'india', 'indian', 'bharat', 'hindustan', 'mahindra', 'tata', 'reliance', 'adani',
        'infosys', 'wipro', 'tcs', 'hdfc', 'icici', 'sbi', 'itc', 'lt', 'bajaj', 'hul',
        'ongc', 'coal india', 'ntpc', 'bhel', 'beml', 'sail', 'hindalco', 'vedanta',
        'jsw', 'jindal', 'jubilant', 'dr. reddy', 'sun pharma', 'cipla', 'lupin', 
        'divis', 'aurobindo', 'britannia', 'asian paints', 'ultratech', 'grasim',
        'aditya birla', 'ambuja', 'acc', 'bharti', 'airtel', 'axis bank', 'bajaj finance',
        'bajaj finserv', 'bajaj auto', 'bajaj holdings', 'bata', 'bayer', 'bharat forge',
        'bharti airtel', 'bharti infratel', 'bharti telecom', 'biocon', 'birlacorp',
        'birlasoft', 'bosch', 'bpcl', 'cadila', 'canara bank', 'castrol', 'ceat', 'central bank',
        'century', 'chambal', 'chennai petroleum', 'chola', 'cipla', 'coalindia', 'colgate',
        'container', 'coromandel', 'crompton', 'cummins', 'dabur', 'dcb bank', 'dhfl', 'dil',
        'divislab', 'dlf', 'drreddys', 'eicher', 'eicher motors', 'exide', 'federal bank',
        'federal-mogul', 'gail', 'glaxo', 'glenmark', 'gmdcl', 'godrej', 'grasim', 'gujarat gas',
        'gujarat state petronet', 'havells', 'hero motocorp', 'hexaware', 'hindalco', 'hindalco inds',
        'hindalco industries', 'hcl tech', 'hdfc bank', 'hdfc life', 'hero', 'hindalco', 'hindustan',
        'hindustan copper', 'hindustan petroleum', 'hindustan unilever', 'hul', 'hdfc amc',
        'icici bank', 'icici lombard', 'icici prudential', 'idbi bank', 'idfc', 'idfc first bank',
        'ifci', 'iifl', 'iifl securities', 'ioc', 'indian oil', 'indian bank', 'indian hotels',
        'indian oil corporation', 'indian overseas bank', 'indian railway', 'indian railway finance',
        'indian railway finance corporation', 'indian renais', 'indian renais finance',
        'indian renais finance corporation', 'indian renais finance ltd', 'indian renais ltd',
        'indian renais finance limited', 'indian renais finance ltd.', 'indian renais ltd.',
        'indian renais finance limited.'
    ]
    
    indian_stocks = set()
    
    if not os.path.exists(csv_path):
        print(f"Error: EQUITY_L.csv not found at {csv_path}")
        return indian_stocks
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                symbol = row.get('SYMBOL', '').strip().lower()
                name = row.get('NAME OF COMPANY', '').strip().lower()
                
                # Check if the stock name or symbol contains any Indian keyword
                if any(keyword in name or keyword in symbol for keyword in indian_keywords):
                    indian_stocks.add((symbol.upper(), name.title()))
        
        print(f"Found {len(indian_stocks)} India-relevant stocks in {csv_path}")
        
    except Exception as e:
        print(f"Error processing {csv_path}: {str(e)}")
    
    return indian_stocks

def save_indian_stocks(stocks: Set[tuple], output_file: str = 'indian_stocks.txt'):
    """Save the list of Indian stocks to a text file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Symbol,Company Name\n")
            for symbol, name in sorted(stocks, key=lambda x: x[0]):
                f.write(f"{symbol},{name}\n")
        print(f"Saved {len(stocks)} Indian stocks to {output_file}")
    except Exception as e:
        print(f"Error saving to {output_file}: {str(e)}")

if __name__ == "__main__":
    # Path to the EQUITY_L.csv file
    csv_path = os.path.join(os.path.dirname(__file__), 'EQUITY_L.csv')
    
    # Load and filter Indian stocks
    indian_stocks = load_indian_stocks(csv_path)
    
    # Print the first 20 stocks as a sample
    print("\nSample of India-relevant stocks:")
    print("-" * 80)
    print(f"{'Symbol':<10} | {'Company Name'}")
    print("-" * 80)
    for symbol, name in sorted(list(indian_stocks)[:20], key=lambda x: x[0]):
        print(f"{symbol:<10} | {name}")
    
    # Save the complete list to a file
    save_indian_stocks(indian_stocks, 'indian_stocks_list.csv')
    
    print("\nNote: The complete list has been saved to 'indian_stocks_list.csv' in the current directory.")
    print("You can import this file into Excel or any spreadsheet application for further analysis.")
