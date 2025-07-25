"""
Peer Comparison & Sector Benchmarking Engine
Provides competitive analysis and sector-wide performance benchmarks
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from functools import lru_cache
import logging
from flask import current_app
import json

logger = logging.getLogger(__name__)

class PeerComparisonEngine:
    def __init__(self):
        # Industry peer mappings
        self.peer_mappings = {
            # Technology
            'AAPL': ['MSFT', 'GOOGL', 'META', 'AMZN'],
            'MSFT': ['AAPL', 'GOOGL', 'CRM', 'ORCL'],
            'GOOGL': ['META', 'AAPL', 'MSFT', 'AMZN'],
            'META': ['GOOGL', 'SNAP', 'TWTR', 'PINS'],
            'NVDA': ['AMD', 'INTC', 'QCOM', 'AVGO'],
            'AMD': ['NVDA', 'INTC', 'QCOM', 'MU'],
            'CRM': ['MSFT', 'ORCL', 'SNOW', 'WORK'],
            
            # Electric Vehicles
            'TSLA': ['RIVN', 'LCID', 'NIO', 'XPEV'],
            'RIVN': ['TSLA', 'LCID', 'F', 'GM'],
            'LCID': ['TSLA', 'RIVN', 'NIO', 'XPEV'],
            
            # Streaming/Entertainment
            'NFLX': ['DIS', 'ROKU', 'PARA', 'WBD'],
            'DIS': ['NFLX', 'PARA', 'CMCSA', 'WBD'],
            
            # Cloud/SaaS
            'SNOW': ['CRM', 'PLTR', 'DBX', 'ZM'],
            'PLTR': ['SNOW', 'C3AI', 'AI', 'PATH'],
            
            # Fintech/Payments
            'PYPL': ['V', 'MA', 'SQ', 'COIN'],
            'COIN': ['PYPL', 'HOOD', 'SQ', 'MSTR'],
            'SQ': ['PYPL', 'V', 'MA', 'COIN'],
            
            # Traditional Auto
            'F': ['GM', 'TSLA', 'RIVN', 'TM'],
            'GM': ['F', 'TSLA', 'RIVN', 'TM'],
            
            # Banks
            'JPM': ['BAC', 'WFC', 'C', 'GS'],
            'BAC': ['JPM', 'WFC', 'C', 'USB'],
            
            # Biotech
            'MRNA': ['PFE', 'BNTX', 'JNJ', 'GILD'],
            'PFE': ['MRNA', 'JNJ', 'MRK', 'ABBV']
        }
        
        # Sector mappings for broader analysis
        self.sector_symbols = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'AMD', 'CRM', 'ORCL', 'INTC', 'QCOM'],
            'Healthcare': ['JNJ', 'PFE', 'ABBV', 'MRK', 'UNH', 'LLY', 'TMO', 'GILD', 'MRNA', 'BNTX'],
            'Financial Services': ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'V', 'MA', 'PYPL', 'AXP'],
            'Consumer Discretionary': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'F', 'GM'],
            'Communication Services': ['GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'TMUS'],
            'Energy': ['XOM', 'CVX', 'COP', 'EOG', 'SLB', 'MPC', 'PSX', 'VLO', 'KMI', 'OKE'],
            'Industrials': ['BA', 'CAT', 'GE', 'MMM', 'HON', 'UPS', 'RTX', 'LMT', 'DE', 'EMR'],
            'Consumer Staples': ['PG', 'KO', 'PEP', 'WMT', 'COST', 'CL', 'KHC', 'MDLZ', 'MO', 'EL']
        }

    def get_peer_comparison(self, symbol):
        """Get comprehensive peer comparison analysis"""
        try:
            symbol = symbol.upper()
            peers = self.peer_mappings.get(symbol, [])
            
            if not peers:
                # Try to find peers by sector
                peers = self._find_peers_by_sector(symbol)
            
            if not peers:
                return {
                    'success': False,
                    'error': f'No peer data available for {symbol}',
                    'symbol': symbol
                }
            
            # Get financial data for target and peers
            target_data = self._get_stock_metrics(symbol)
            peer_data = {}
            
            for peer in peers[:4]:  # Limit to top 4 peers
                peer_metrics = self._get_stock_metrics(peer)
                if peer_metrics:
                    peer_data[peer] = peer_metrics
            
            # Calculate peer rankings and comparisons
            comparison_analysis = self._analyze_peer_performance(symbol, target_data, peer_data)
            
            return {
                'success': True,
                'symbol': symbol,
                'target_company': target_data.get('company_name', symbol),
                'target_metrics': target_data,
                'peers': peer_data,
                'comparison_analysis': comparison_analysis,
                'peer_count': len(peer_data),
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Peer comparison error for {symbol}: {e}")
            return {
                'success': False,
                'error': 'Peer comparison service temporarily unavailable',
                'details': str(e)
            }

    def get_sector_benchmark(self, sector):
        """Get sector-wide performance benchmarks"""
        try:
            if sector not in self.sector_symbols:
                available_sectors = list(self.sector_symbols.keys())
                return {
                    'success': False,
                    'error': f'Sector "{sector}" not available',
                    'available_sectors': available_sectors
                }
            
            sector_stocks = self.sector_symbols[sector]
            sector_data = {}
            
            # Get metrics for all stocks in sector
            for symbol in sector_stocks:
                metrics = self._get_stock_metrics(symbol)
                if metrics:
                    sector_data[symbol] = metrics
            
            # Calculate sector benchmarks
            benchmarks = self._calculate_sector_benchmarks(sector_data)
            
            # Rank stocks within sector
            rankings = self._rank_sector_stocks(sector_data)
            
            return {
                'success': True,
                'sector': sector,
                'benchmarks': benchmarks,
                'rankings': rankings,
                'stock_count': len(sector_data),
                'top_performers': rankings['performance'][:5],
                'value_opportunities': rankings['value'][:5],
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Sector benchmark error for {sector}: {e}")
            return {
                'success': False,
                'error': 'Sector benchmark service temporarily unavailable',
                'details': str(e)
            }

    @lru_cache(maxsize=200)
    def _get_stock_metrics(self, symbol):
        """Get comprehensive stock metrics (cached)"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            history = ticker.history(period='1y')
            
            if history.empty:
                return None
            
            # Calculate key metrics
            current_price = history['Close'].iloc[-1]
            year_high = history['High'].max()
            year_low = history['Low'].min()
            
            # Price performance
            returns_1m = self._calculate_return(history, 30)
            returns_3m = self._calculate_return(history, 90)
            returns_6m = self._calculate_return(history, 180)
            returns_1y = self._calculate_return(history, 252)
            
            # Volatility
            volatility = history['Close'].pct_change().std() * np.sqrt(252) * 100
            
            # Volume metrics
            avg_volume = history['Volume'].tail(30).mean()
            
            return {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'current_price': float(current_price),
                'year_high': float(year_high),
                'year_low': float(year_low),
                'price_to_52w_high': (current_price / year_high - 1) * 100,
                'price_to_52w_low': (current_price / year_low - 1) * 100,
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),
                'debt_to_equity': info.get('debtToEquity'),
                'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else None,
                'roa': info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else None,
                'profit_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else None,
                'revenue_growth': info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else None,
                'earnings_growth': info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else None,
                'returns_1m': returns_1m,
                'returns_3m': returns_3m,
                'returns_6m': returns_6m,
                'returns_1y': returns_1y,
                'volatility': volatility,
                'avg_volume': int(avg_volume),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                'beta': info.get('beta'),
                'analyst_target': info.get('targetMeanPrice'),
                'recommendation': info.get('recommendationMean')
            }
            
        except Exception as e:
            logger.debug(f"Error getting metrics for {symbol}: {e}")
            return None

    def _calculate_return(self, history, days):
        """Calculate return over specified number of days"""
        try:
            if len(history) <= days:
                return None
            
            current_price = history['Close'].iloc[-1]
            past_price = history['Close'].iloc[-days-1]
            return ((current_price / past_price) - 1) * 100
            
        except Exception:
            return None

    def _analyze_peer_performance(self, target_symbol, target_data, peer_data):
        """Analyze target stock performance vs peers"""
        try:
            analysis = {
                'valuation_vs_peers': {},
                'performance_vs_peers': {},
                'financial_strength_vs_peers': {},
                'overall_ranking': {}
            }
            
            # Gather all metrics for comparison
            all_stocks = {target_symbol: target_data}
            all_stocks.update(peer_data)
            
            # Valuation comparison
            metrics_to_compare = ['pe_ratio', 'forward_pe', 'price_to_book', 'price_to_sales', 'peg_ratio']
            for metric in metrics_to_compare:
                values = [data.get(metric) for data in all_stocks.values() if data.get(metric) is not None]
                if values and target_data.get(metric) is not None:
                    target_value = target_data[metric]
                    percentile = (sum(1 for v in values if v > target_value) / len(values)) * 100
                    analysis['valuation_vs_peers'][metric] = {
                        'target_value': target_value,
                        'peer_median': np.median(values),
                        'percentile_rank': percentile,
                        'interpretation': self._interpret_valuation_metric(metric, percentile)
                    }
            
            # Performance comparison
            performance_metrics = ['returns_1m', 'returns_3m', 'returns_6m', 'returns_1y']
            for metric in performance_metrics:
                values = [data.get(metric) for data in all_stocks.values() if data.get(metric) is not None]
                if values and target_data.get(metric) is not None:
                    target_value = target_data[metric]
                    percentile = (sum(1 for v in values if v < target_value) / len(values)) * 100
                    analysis['performance_vs_peers'][metric] = {
                        'target_value': target_value,
                        'peer_median': np.median(values),
                        'percentile_rank': percentile,
                        'rank': f"{int((100-percentile)/20) + 1}/5"
                    }
            
            # Financial strength comparison
            strength_metrics = ['roe', 'roa', 'profit_margin', 'revenue_growth']
            for metric in strength_metrics:
                values = [data.get(metric) for data in all_stocks.values() if data.get(metric) is not None]
                if values and target_data.get(metric) is not None:
                    target_value = target_data[metric]
                    percentile = (sum(1 for v in values if v < target_value) / len(values)) * 100
                    analysis['financial_strength_vs_peers'][metric] = {
                        'target_value': target_value,
                        'peer_median': np.median(values),
                        'percentile_rank': percentile,
                        'grade': self._grade_metric(percentile)
                    }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing peer performance: {e}")
            return {}

    def _calculate_sector_benchmarks(self, sector_data):
        """Calculate sector-wide benchmarks"""
        try:
            benchmarks = {}
            
            all_metrics = ['pe_ratio', 'price_to_book', 'price_to_sales', 'roe', 'roa', 
                          'profit_margin', 'revenue_growth', 'returns_1y', 'volatility', 'dividend_yield']
            
            for metric in all_metrics:
                values = [data.get(metric) for data in sector_data.values() if data.get(metric) is not None]
                if values:
                    benchmarks[metric] = {
                        'median': np.median(values),
                        'mean': np.mean(values),
                        'percentile_25': np.percentile(values, 25),
                        'percentile_75': np.percentile(values, 75),
                        'min': min(values),
                        'max': max(values),
                        'count': len(values)
                    }
            
            return benchmarks
            
        except Exception as e:
            logger.error(f"Error calculating sector benchmarks: {e}")
            return {}

    def _rank_sector_stocks(self, sector_data):
        """Rank stocks within sector by different criteria"""
        try:
            rankings = {
                'performance': [],
                'value': [],
                'growth': [],
                'dividend': []
            }
            
            # Performance ranking (1-year return)
            performance_data = [(symbol, data.get('returns_1y', 0)) 
                              for symbol, data in sector_data.items() 
                              if data.get('returns_1y') is not None]
            performance_data.sort(key=lambda x: x[1], reverse=True)
            
            for symbol, return_1y in performance_data:
                stock_data = sector_data[symbol]
                rankings['performance'].append({
                    'symbol': symbol,
                    'name': stock_data.get('company_name', symbol),
                    'metric_value': return_1y,
                    'metric_name': '1-Year Return (%)'
                })
            
            # Value ranking (P/E ratio - lower is better)
            value_data = [(symbol, data.get('pe_ratio', float('inf'))) 
                         for symbol, data in sector_data.items() 
                         if data.get('pe_ratio') is not None and data.get('pe_ratio') > 0]
            value_data.sort(key=lambda x: x[1])
            
            for symbol, pe_ratio in value_data:
                stock_data = sector_data[symbol]
                rankings['value'].append({
                    'symbol': symbol,
                    'name': stock_data.get('company_name', symbol),
                    'metric_value': pe_ratio,
                    'metric_name': 'P/E Ratio'
                })
            
            # Growth ranking (revenue growth)
            growth_data = [(symbol, data.get('revenue_growth', 0)) 
                          for symbol, data in sector_data.items() 
                          if data.get('revenue_growth') is not None]
            growth_data.sort(key=lambda x: x[1], reverse=True)
            
            for symbol, growth in growth_data:
                stock_data = sector_data[symbol]
                rankings['growth'].append({
                    'symbol': symbol,
                    'name': stock_data.get('company_name', symbol),
                    'metric_value': growth,
                    'metric_name': 'Revenue Growth (%)'
                })
            
            # Dividend ranking
            dividend_data = [(symbol, data.get('dividend_yield', 0)) 
                            for symbol, data in sector_data.items() 
                            if data.get('dividend_yield') is not None]
            dividend_data.sort(key=lambda x: x[1], reverse=True)
            
            for symbol, dividend in dividend_data:
                stock_data = sector_data[symbol]
                rankings['dividend'].append({
                    'symbol': symbol,
                    'name': stock_data.get('company_name', symbol),
                    'metric_value': dividend,
                    'metric_name': 'Dividend Yield (%)'
                })
            
            return rankings
            
        except Exception as e:
            logger.error(f"Error ranking sector stocks: {e}")
            return {}

    def _find_peers_by_sector(self, symbol):
        """Find peer stocks by sector when direct mapping unavailable"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            sector = info.get('sector')
            
            if sector and sector in self.sector_symbols:
                sector_stocks = self.sector_symbols[sector]
                # Remove the target symbol and return top peers
                peers = [s for s in sector_stocks if s != symbol]
                return peers[:4]
            
            return []
            
        except Exception:
            return []

    def _interpret_valuation_metric(self, metric, percentile):
        """Interpret valuation metric percentile"""
        if metric in ['pe_ratio', 'forward_pe', 'price_to_book', 'price_to_sales']:
            # Lower is better for valuation metrics
            if percentile > 80:
                return 'Undervalued vs peers'
            elif percentile > 60:
                return 'Fairly valued vs peers'
            elif percentile > 40:
                return 'At premium vs peers'
            else:
                return 'Significantly overvalued vs peers'
        else:
            # Higher is better
            if percentile > 80:
                return 'Excellent vs peers'
            elif percentile > 60:
                return 'Above average vs peers'
            elif percentile > 40:
                return 'Average vs peers'
            else:
                return 'Below average vs peers'

    def _grade_metric(self, percentile):
        """Convert percentile to letter grade"""
        if percentile >= 90:
            return 'A+'
        elif percentile >= 80:
            return 'A'
        elif percentile >= 70:
            return 'B+'
        elif percentile >= 60:
            return 'B'
        elif percentile >= 50:
            return 'C+'
        elif percentile >= 40:
            return 'C'
        elif percentile >= 30:
            return 'D+'
        elif percentile >= 20:
            return 'D'
        else:
            return 'F'

# Global instance
peer_comparison_engine = PeerComparisonEngine()