import sqlite3
from typing import List, Dict, Optional
import os
import csv
import logging

# Set up logging
logger = logging.getLogger(__name__)

class CompanyDatabase:
    def __init__(self, db_path: str = 'data/company_database.db'):
        """
        Initialize the company database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Create companies table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    symbol TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    sector TEXT,
                    industry TEXT,
                    isin TEXT,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Create index for faster lookups
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_company_name ON companies(name)')
            conn.commit()
            logger.info("Initialized company database")

    def import_from_csv(self, csv_path: str) -> int:
        """
        Import company data from EQUITY_L.csv
        
        Args:
            csv_path: Path to the CSV file containing company data
            
        Returns:
            int: Number of records imported
        """
        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            return 0

        imported = 0
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        cursor.execute('''
                            INSERT OR REPLACE INTO companies 
                            (symbol, name, isin) 
                            VALUES (?, ?, ?)
                        ''', (
                            row['SYMBOL'].strip().upper(),
                            row['NAME OF COMPANY'].strip(),
                            row.get('ISIN NUMBER', '').strip()
                        ))
                        imported += 1
                    except Exception as e:
                        logger.error(f"Error importing {row.get('SYMBOL')}: {str(e)}")
            conn.commit()
        logger.info(f"Imported {imported} companies from {csv_path}")
        return imported

    def get_company_by_symbol(self, symbol: str) -> Optional[Dict]:
        """
        Get company details by symbol
        
        Args:
            symbol: Stock symbol to look up
            
        Returns:
            Optional[Dict]: Company details or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM companies WHERE symbol = ?', (symbol.upper(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def search_companies(self, search_term: str, limit: int = 10) -> List[Dict]:
        """
        Search companies by name or symbol
        
        Args:
            search_term: Term to search for in company names or symbols
            limit: Maximum number of results to return
            
        Returns:
            List[Dict]: List of matching companies
        """
        search_term = f"%{search_term}%"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM companies 
                WHERE name LIKE ? OR symbol LIKE ?
                LIMIT ?
            ''', (search_term, search_term.upper(), limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_symbols(self) -> List[str]:
        """
        Get list of all company symbols
        
        Returns:
            List[str]: List of all company symbols
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT symbol FROM companies')
            return [row[0] for row in cursor.fetchall()]

    def update_company_info(self, symbol: str, **kwargs) -> bool:
        """
        Update company information
        
        Args:
            symbol: Stock symbol to update
            **kwargs: Fields to update and their new values
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        if not kwargs:
            return False

        set_clause = ', '.join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values())
        values.append(symbol.upper())

        with sqlite3.connect(self.db_path) as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    f'UPDATE companies SET {set_clause} WHERE symbol = ?',
                    values
                )
                conn.commit()
                updated = cursor.rowcount > 0
                if updated:
                    logger.info(f"Updated company info for {symbol}")
                return updated
            except Exception as e:
                logger.error(f"Error updating company {symbol}: {str(e)}")
                return False
