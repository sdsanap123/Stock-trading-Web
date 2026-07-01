#!/usr/bin/env python3
"""
Fundamental Analyzer Component
Fundamental analysis for stocks using financial data.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class FundamentalAnalyzer:
    """Fundamental analysis for stocks."""
    
    def __init__(self):
        logger.info("Fundamental Analyzer initialized")
    
    def get_financial_data(self, symbol: str) -> Optional[Dict]:
        """Get financial data for a stock."""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get company info
            info = ticker.info
            
            # Get financial statements
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            cashflow = ticker.cashflow
            
            if financials.empty and balance_sheet.empty:
                return None
            
            # Extract key financial metrics
            financial_data = {
                'symbol': symbol,
                'company_name': info.get('longName', 'Unknown'),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'pb_ratio': info.get('priceToBook', 0),
                'ps_ratio': info.get('priceToSalesTrailing12Months', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'dividend_rate': info.get('dividendRate', 0),
                'payout_ratio': info.get('payoutRatio', 0),
                'beta': info.get('beta', 1.0),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0),
                'current_price': info.get('currentPrice', 0),
                'target_price': info.get('targetMeanPrice', 0),
                'recommendation': info.get('recommendationKey', 'hold'),
                'analyst_count': info.get('numberOfAnalystOpinions', 0),
                'revenue_growth': info.get('revenueGrowth', 0),
                'earnings_growth': info.get('earningsGrowth', 0),
                'profit_margins': info.get('profitMargins', 0),
                'operating_margins': info.get('operatingMargins', 0),
                'gross_margins': info.get('grossMargins', 0),
                'return_on_equity': info.get('returnOnEquity', 0),
                'return_on_assets': info.get('returnOnAssets', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'quick_ratio': info.get('quickRatio', 0),
                'cash_per_share': info.get('totalCashPerShare', 0),
                'book_value': info.get('bookValue', 0),
                'price_to_book': info.get('priceToBook', 0),
                'enterprise_to_revenue': info.get('enterpriseToRevenue', 0),
                'enterprise_to_ebitda': info.get('enterpriseToEbitda', 0),
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth', 0),
                'revenue_quarterly_growth': info.get('revenueQuarterlyGrowth', 0),
                'held_percent_insiders': info.get('heldPercentInsiders', 0),
                'held_percent_institutions': info.get('heldPercentInstitutions', 0),
                'float_shares': info.get('floatShares', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'shares_short': info.get('sharesShort', 0),
                'short_ratio': info.get('shortRatio', 0),
                'short_percent_of_float': info.get('shortPercentOfFloat', 0),
                'implied_shares_outstanding': info.get('impliedSharesOutstanding', 0),
                'last_split_date': info.get('lastSplitDate', None),
                'last_split_factor': info.get('lastSplitFactor', None),
                'last_dividend_date': info.get('lastDividendDate', None),
                'last_dividend_value': info.get('lastDividendValue', 0),
                'ex_dividend_date': info.get('exDividendDate', None),
                'next_dividend_date': info.get('nextDividendDate', None),
                'next_earnings_date': info.get('nextEarningsDate', None),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'NSE'),
                'timezone': info.get('timezone', 'Asia/Kolkata'),
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            # Add financial statement data if available
            if not financials.empty:
                try:
                    # Get latest year data
                    latest_year = financials.columns[0]
                    financial_data.update({
                        'total_revenue': financials.loc['Total Revenue', latest_year] if 'Total Revenue' in financials.index else 0,
                        'gross_profit': financials.loc['Gross Profit', latest_year] if 'Gross Profit' in financials.index else 0,
                        'operating_income': financials.loc['Operating Income', latest_year] if 'Operating Income' in financials.index else 0,
                        'net_income': financials.loc['Net Income', latest_year] if 'Net Income' in financials.index else 0,
                        'ebitda': financials.loc['EBITDA', latest_year] if 'EBITDA' in financials.index else 0,
                        'ebit': financials.loc['EBIT', latest_year] if 'EBIT' in financials.index else 0,
                        'research_development': financials.loc['Research Development', latest_year] if 'Research Development' in financials.index else 0,
                        'selling_general_administrative': financials.loc['Selling General Administrative', latest_year] if 'Selling General Administrative' in financials.index else 0,
                        'total_operating_expenses': financials.loc['Total Operating Expenses', latest_year] if 'Total Operating Expenses' in financials.index else 0,
                        'interest_expense': financials.loc['Interest Expense', latest_year] if 'Interest Expense' in financials.index else 0,
                        'income_before_tax': financials.loc['Income Before Tax', latest_year] if 'Income Before Tax' in financials.index else 0,
                        'income_tax_expense': financials.loc['Income Tax Expense', latest_year] if 'Income Tax Expense' in financials.index else 0,
                        'net_income_common': financials.loc['Net Income Common Stockholders', latest_year] if 'Net Income Common Stockholders' in financials.index else 0,
                        'diluted_eps': financials.loc['Diluted EPS', latest_year] if 'Diluted EPS' in financials.index else 0,
                        'basic_eps': financials.loc['Basic EPS', latest_year] if 'Basic EPS' in financials.index else 0,
                        'weighted_average_shares': financials.loc['Weighted Average Shares', latest_year] if 'Weighted Average Shares' in financials.index else 0,
                        'weighted_average_shares_diluted': financials.loc['Weighted Average Shares Diluted', latest_year] if 'Weighted Average Shares Diluted' in financials.index else 0
                    })
                except Exception as e:
                    logger.warning(f"Error extracting financials data: {str(e)}")
            
            if not balance_sheet.empty:
                try:
                    # Get latest year data
                    latest_year = balance_sheet.columns[0]
                    financial_data.update({
                        'total_cash': balance_sheet.loc['Total Cash', latest_year] if 'Total Cash' in balance_sheet.index else 0,
                        'total_cash_per_share': balance_sheet.loc['Total Cash Per Share', latest_year] if 'Total Cash Per Share' in balance_sheet.index else 0,
                        'total_debt': balance_sheet.loc['Total Debt', latest_year] if 'Total Debt' in balance_sheet.index else 0,
                        'total_debt_per_equity': balance_sheet.loc['Total Debt/Equity', latest_year] if 'Total Debt/Equity' in balance_sheet.index else 0,
                        'current_assets': balance_sheet.loc['Current Assets', latest_year] if 'Current Assets' in balance_sheet.index else 0,
                        'total_assets': balance_sheet.loc['Total Assets', latest_year] if 'Total Assets' in balance_sheet.index else 0,
                        'current_liabilities': balance_sheet.loc['Current Liabilities', latest_year] if 'Current Liabilities' in balance_sheet.index else 0,
                        'total_liabilities': balance_sheet.loc['Total Liabilities', latest_year] if 'Total Liabilities' in balance_sheet.index else 0,
                        'total_stockholder_equity': balance_sheet.loc['Total Stockholder Equity', latest_year] if 'Total Stockholder Equity' in balance_sheet.index else 0,
                        'retained_earnings': balance_sheet.loc['Retained Earnings', latest_year] if 'Retained Earnings' in balance_sheet.index else 0,
                        'common_stock': balance_sheet.loc['Common Stock', latest_year] if 'Common Stock' in balance_sheet.index else 0,
                        'treasury_stock': balance_sheet.loc['Treasury Stock', latest_year] if 'Treasury Stock' in balance_sheet.index else 0,
                        'capital_surplus': balance_sheet.loc['Capital Surplus', latest_year] if 'Capital Surplus' in balance_sheet.index else 0,
                        'other_stockholder_equity': balance_sheet.loc['Other Stockholder Equity', latest_year] if 'Other Stockholder Equity' in balance_sheet.index else 0,
                        'goodwill': balance_sheet.loc['Goodwill', latest_year] if 'Goodwill' in balance_sheet.index else 0,
                        'intangible_assets': balance_sheet.loc['Intangible Assets', latest_year] if 'Intangible Assets' in balance_sheet.index else 0,
                        'net_tangible_assets': balance_sheet.loc['Net Tangible Assets', latest_year] if 'Net Tangible Assets' in balance_sheet.index else 0,
                        'working_capital': balance_sheet.loc['Working Capital', latest_year] if 'Working Capital' in balance_sheet.index else 0,
                        'invested_capital': balance_sheet.loc['Invested Capital', latest_year] if 'Invested Capital' in balance_sheet.index else 0,
                        'tangible_book_value': balance_sheet.loc['Tangible Book Value', latest_year] if 'Tangible Book Value' in balance_sheet.index else 0,
                        'total_capitalization': balance_sheet.loc['Total Capitalization', latest_year] if 'Total Capitalization' in balance_sheet.index else 0,
                        'common_stock_shares_outstanding': balance_sheet.loc['Common Stock Shares Outstanding', latest_year] if 'Common Stock Shares Outstanding' in balance_sheet.index else 0,
                        'net_income': balance_sheet.loc['Net Income', latest_year] if 'Net Income' in balance_sheet.index else 0,
                        'net_income_common': balance_sheet.loc['Net Income Common Stockholders', latest_year] if 'Net Income Common Stockholders' in balance_sheet.index else 0,
                        'net_income_common_stockholders': balance_sheet.loc['Net Income Common Stockholders', latest_year] if 'Net Income Common Stockholders' in balance_sheet.index else 0,
                        'net_income_common_stockholders_attributable': balance_sheet.loc['Net Income Common Stockholders Attributable', latest_year] if 'Net Income Common Stockholders Attributable' in balance_sheet.index else 0,
                        'net_income_common_stockholders_attributable_to_parent': balance_sheet.loc['Net Income Common Stockholders Attributable To Parent', latest_year] if 'Net Income Common Stockholders Attributable To Parent' in balance_sheet.index else 0,
                        'net_income_common_stockholders_attributable_to_parent_common': balance_sheet.loc['Net Income Common Stockholders Attributable To Parent Common', latest_year] if 'Net Income Common Stockholders Attributable To Parent Common' in balance_sheet.index else 0,
                        'net_income_common_stockholders_attributable_to_parent_common_basic': balance_sheet.loc['Net Income Common Stockholders Attributable To Parent Common Basic', latest_year] if 'Net Income Common Stockholders Attributable To Parent Common Basic' in balance_sheet.index else 0,
                        'net_income_common_stockholders_attributable_to_parent_common_diluted': balance_sheet.loc['Net Income Common Stockholders Attributable To Parent Common Diluted', latest_year] if 'Net Income Common Stockholders Attributable To Parent Common Diluted' in balance_sheet.index else 0,
                        'net_income_common_stockholders_attributable_to_parent_common_diluted_eps': balance_sheet.loc['Net Income Common Stockholders Attributable To Parent Common Diluted EPS', latest_year] if 'Net Income Common Stockholders Attributable To Parent Common Diluted EPS' in balance_sheet.index else 0,
                        'net_income_common_stockholders_attributable_to_parent_common_diluted_eps_basic': balance_sheet.loc['Net Income Common Stockholders Attributable To Parent Common Diluted EPS Basic', latest_year] if 'Net Income Common Stockholders Attributable To Parent Common Diluted EPS Basic' in balance_sheet.index else 0,
                        'net_income_common_stockholders_attributable_to_parent_common_diluted_eps_diluted': balance_sheet.loc['Net Income Common Stockholders Attributable To Parent Common Diluted EPS Diluted', latest_year] if 'Net Income Common Stockholders Attributable To Parent Common Diluted EPS Diluted' in balance_sheet.index else 0
                    })
                except Exception as e:
                    logger.warning(f"Error extracting balance sheet data: {str(e)}")
            
            return financial_data
            
        except Exception as e:
            logger.error(f"Error getting financial data for {symbol}: {str(e)}")
            return None
    
    def calculate_fundamental_score(self, financial_data: Dict) -> Dict:
        """Calculate fundamental score based on financial metrics."""
        try:
            if not financial_data:
                return {'score': 0.0, 'ratings': {}}
            
            score = 0.0
            ratings = {}
            
            # Valuation Metrics (25% weight)
            valuation_score = 0.0
            
            # P/E Ratio
            pe_ratio = financial_data.get('pe_ratio', 0)
            if pe_ratio > 0:
                if pe_ratio < 15:
                    valuation_score += 0.8
                    ratings['P/E Ratio'] = 'Excellent (< 15)'
                elif pe_ratio < 25:
                    valuation_score += 0.6
                    ratings['P/E Ratio'] = 'Good (15-25)'
                elif pe_ratio < 35:
                    valuation_score += 0.4
                    ratings['P/E Ratio'] = 'Fair (25-35)'
                else:
                    valuation_score += 0.2
                    ratings['P/E Ratio'] = 'Expensive (> 35)'
            else:
                ratings['P/E Ratio'] = 'N/A'
            
            # P/B Ratio
            pb_ratio = financial_data.get('pb_ratio', 0)
            if pb_ratio > 0:
                if pb_ratio < 1.5:
                    valuation_score += 0.8
                    ratings['P/B Ratio'] = 'Excellent (< 1.5)'
                elif pb_ratio < 3:
                    valuation_score += 0.6
                    ratings['P/B Ratio'] = 'Good (1.5-3)'
                elif pb_ratio < 5:
                    valuation_score += 0.4
                    ratings['P/B Ratio'] = 'Fair (3-5)'
                else:
                    valuation_score += 0.2
                    ratings['P/B Ratio'] = 'Expensive (> 5)'
            else:
                ratings['P/B Ratio'] = 'N/A'
            
            # P/S Ratio
            ps_ratio = financial_data.get('ps_ratio', 0)
            if ps_ratio > 0:
                if ps_ratio < 2:
                    valuation_score += 0.8
                    ratings['P/S Ratio'] = 'Excellent (< 2)'
                elif ps_ratio < 5:
                    valuation_score += 0.6
                    ratings['P/S Ratio'] = 'Good (2-5)'
                elif ps_ratio < 10:
                    valuation_score += 0.4
                    ratings['P/S Ratio'] = 'Fair (5-10)'
                else:
                    valuation_score += 0.2
                    ratings['P/S Ratio'] = 'Expensive (> 10)'
            else:
                ratings['P/S Ratio'] = 'N/A'
            
            valuation_score = min(valuation_score, 1.0)
            score += valuation_score * 0.25
            
            # Profitability Metrics (30% weight)
            profitability_score = 0.0
            
            # ROE
            roe = financial_data.get('return_on_equity', 0)
            if roe > 0:
                if roe > 20:
                    profitability_score += 0.8
                    ratings['ROE'] = 'Excellent (> 20%)'
                elif roe > 15:
                    profitability_score += 0.6
                    ratings['ROE'] = 'Good (15-20%)'
                elif roe > 10:
                    profitability_score += 0.4
                    ratings['ROE'] = 'Fair (10-15%)'
                else:
                    profitability_score += 0.2
                    ratings['ROE'] = 'Poor (< 10%)'
            else:
                ratings['ROE'] = 'N/A'
            
            # ROA
            roa = financial_data.get('return_on_assets', 0)
            if roa > 0:
                if roa > 10:
                    profitability_score += 0.8
                    ratings['ROA'] = 'Excellent (> 10%)'
                elif roa > 5:
                    profitability_score += 0.6
                    ratings['ROA'] = 'Good (5-10%)'
                elif roa > 2:
                    profitability_score += 0.4
                    ratings['ROA'] = 'Fair (2-5%)'
                else:
                    profitability_score += 0.2
                    ratings['ROA'] = 'Poor (< 2%)'
            else:
                ratings['ROA'] = 'N/A'
            
            # Profit Margins
            profit_margins = financial_data.get('profit_margins', 0)
            if profit_margins > 0:
                if profit_margins > 15:
                    profitability_score += 0.8
                    ratings['Profit Margins'] = 'Excellent (> 15%)'
                elif profit_margins > 10:
                    profitability_score += 0.6
                    ratings['Profit Margins'] = 'Good (10-15%)'
                elif profit_margins > 5:
                    profitability_score += 0.4
                    ratings['Profit Margins'] = 'Fair (5-10%)'
                else:
                    profitability_score += 0.2
                    ratings['Profit Margins'] = 'Poor (< 5%)'
            else:
                ratings['Profit Margins'] = 'N/A'
            
            profitability_score = min(profitability_score, 1.0)
            score += profitability_score * 0.30
            
            # Growth Metrics (20% weight)
            growth_score = 0.0
            
            # Revenue Growth
            revenue_growth = financial_data.get('revenue_growth', 0)
            if revenue_growth > 0:
                if revenue_growth > 20:
                    growth_score += 0.8
                    ratings['Revenue Growth'] = 'Excellent (> 20%)'
                elif revenue_growth > 10:
                    growth_score += 0.6
                    ratings['Revenue Growth'] = 'Good (10-20%)'
                elif revenue_growth > 5:
                    growth_score += 0.4
                    ratings['Revenue Growth'] = 'Fair (5-10%)'
                else:
                    growth_score += 0.2
                    ratings['Revenue Growth'] = 'Poor (< 5%)'
            else:
                ratings['Revenue Growth'] = 'N/A'
            
            # Earnings Growth
            earnings_growth = financial_data.get('earnings_growth', 0)
            if earnings_growth > 0:
                if earnings_growth > 20:
                    growth_score += 0.8
                    ratings['Earnings Growth'] = 'Excellent (> 20%)'
                elif earnings_growth > 10:
                    growth_score += 0.6
                    ratings['Earnings Growth'] = 'Good (10-20%)'
                elif earnings_growth > 5:
                    growth_score += 0.4
                    ratings['Earnings Growth'] = 'Fair (5-10%)'
                else:
                    growth_score += 0.2
                    ratings['Earnings Growth'] = 'Poor (< 5%)'
            else:
                ratings['Earnings Growth'] = 'N/A'
            
            growth_score = min(growth_score, 1.0)
            score += growth_score * 0.20
            
            # Financial Health Metrics (25% weight)
            health_score = 0.0
            
            # Debt to Equity
            debt_to_equity = financial_data.get('debt_to_equity', 0)
            if debt_to_equity > 0:
                if debt_to_equity < 0.3:
                    health_score += 0.8
                    ratings['Debt/Equity'] = 'Excellent (< 0.3)'
                elif debt_to_equity < 0.6:
                    health_score += 0.6
                    ratings['Debt/Equity'] = 'Good (0.3-0.6)'
                elif debt_to_equity < 1.0:
                    health_score += 0.4
                    ratings['Debt/Equity'] = 'Fair (0.6-1.0)'
                else:
                    health_score += 0.2
                    ratings['Debt/Equity'] = 'Poor (> 1.0)'
            else:
                ratings['Debt/Equity'] = 'N/A'
            
            # Current Ratio
            current_ratio = financial_data.get('current_ratio', 0)
            if current_ratio > 0:
                if current_ratio > 2:
                    health_score += 0.8
                    ratings['Current Ratio'] = 'Excellent (> 2)'
                elif current_ratio > 1.5:
                    health_score += 0.6
                    ratings['Current Ratio'] = 'Good (1.5-2)'
                elif current_ratio > 1:
                    health_score += 0.4
                    ratings['Current Ratio'] = 'Fair (1-1.5)'
                else:
                    health_score += 0.2
                    ratings['Current Ratio'] = 'Poor (< 1)'
            else:
                ratings['Current Ratio'] = 'N/A'
            
            health_score = min(health_score, 1.0)
            score += health_score * 0.25
            
            # Ensure score is between 0 and 1
            score = max(0, min(1, score))
            
            return {
                'score': score,
                'ratings': ratings,
                'valuation_score': valuation_score,
                'profitability_score': profitability_score,
                'growth_score': growth_score,
                'health_score': health_score,
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating fundamental score: {str(e)}")
            return {'score': 0.0, 'ratings': {}}
