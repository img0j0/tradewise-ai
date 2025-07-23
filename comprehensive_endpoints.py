"""
Comprehensive Endpoints - Complete API coverage for all user-facing features
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
import logging
import json
from datetime import datetime, timedelta
from models import User, StockAnalysis, WatchlistItem, db
from preference_engine import preference_engine
from realtime_data_engine import realtime_engine
from ai_insights import AIInsightsEngine
from enhanced_ai_analyzer import EnhancedAIAnalyzer
import yfinance as yf

logger = logging.getLogger(__name__)

# Create comprehensive endpoints blueprint
comprehensive_bp = Blueprint('comprehensive', __name__)

# Initialize services
ai_engine = AIInsightsEngine()
enhanced_analyzer = EnhancedAIAnalyzer()

@comprehensive_bp.route('/api/portfolio/analytics')
def portfolio_analytics():
    """Comprehensive portfolio analytics with AI insights"""
    try:
        # Get user's holdings from watchlist (simplified portfolio)
        user_preferences = preference_engine.get_user_preferences()
        watchlist_symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA']  # Demo data
        
        portfolio_data = {
            'holdings': [],
            'total_value': 0,
            'total_gain_loss': 0,
            'diversification_score': 0,
            'risk_score': 0,
            'ai_recommendations': []
        }
        
        sector_allocation = {}
        total_portfolio_value = 0
        
        for symbol in watchlist_symbols:
            try:
                # Get current stock data
                analysis_result = enhanced_analyzer.get_enhanced_analysis(symbol)
                stock_data = {
                    'current_price': analysis_result.get('current_price', 0),
                    'price_change_percent': analysis_result.get('price_change_percent', 0),
                    'name': analysis_result.get('company_name', symbol),
                    'sector': 'Technology'  # Default sector for demo
                } if analysis_result.get('success') else None
                if stock_data:
                    # Simulate holding data
                    shares = 10  # Demo shares
                    avg_cost = stock_data['current_price'] * 0.95  # Demo cost basis
                    current_value = shares * stock_data['current_price']
                    gain_loss = current_value - (shares * avg_cost)
                    gain_loss_pct = (gain_loss / (shares * avg_cost)) * 100
                    
                    holding = {
                        'symbol': symbol,
                        'shares': shares,
                        'avg_cost': avg_cost,
                        'current_price': stock_data['current_price'],
                        'current_value': current_value,
                        'gain_loss': gain_loss,
                        'gain_loss_percent': gain_loss_pct,
                        'weight': 0  # Will calculate after total
                    }
                    
                    portfolio_data['holdings'].append(holding)
                    total_portfolio_value += current_value
                    
                    # Track sector allocation
                    sector = stock_data.get('sector', 'Other')
                    sector_allocation[sector] = sector_allocation.get(sector, 0) + current_value
                    
            except Exception as e:
                logger.error(f"Error processing {symbol} for portfolio: {e}")
        
        # Calculate weights and portfolio metrics
        portfolio_data['total_value'] = total_portfolio_value
        
        for holding in portfolio_data['holdings']:
            holding['weight'] = (holding['current_value'] / total_portfolio_value) * 100
            portfolio_data['total_gain_loss'] += holding['gain_loss']
        
        # Calculate diversification score (simplified)
        num_holdings = len(portfolio_data['holdings'])
        max_weight = max([h['weight'] for h in portfolio_data['holdings']]) if portfolio_data['holdings'] else 0
        portfolio_data['diversification_score'] = min(100, (num_holdings * 20) - max_weight)
        
        # Calculate risk score based on user preferences
        risk_tolerance = user_preferences.get('risk_tolerance', 'moderate')
        risk_scores = {'conservative': 25, 'moderate': 50, 'aggressive': 75}
        portfolio_data['risk_score'] = risk_scores.get(risk_tolerance, 50)
        
        # Generate AI recommendations
        portfolio_data['ai_recommendations'] = [
            {
                'type': 'rebalancing',
                'title': 'Portfolio Rebalancing Suggestion',
                'description': f'Consider rebalancing your portfolio. Your largest position is {max_weight:.1f}%',
                'action': 'Reduce concentration risk by diversifying into other sectors'
            },
            {
                'type': 'sector_allocation',
                'title': 'Sector Diversification',
                'description': 'Technology sector represents majority of holdings',
                'action': 'Consider adding exposure to healthcare, financials, or consumer staples'
            }
        ]
        
        # Add sector breakdown
        portfolio_data['sector_allocation'] = [
            {'sector': sector, 'value': value, 'percentage': (value/total_portfolio_value)*100}
            for sector, value in sector_allocation.items()
        ]
        
        return jsonify({
            'success': True,
            'data': portfolio_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f'Error generating portfolio analytics: {e}')
        return jsonify({'error': 'Portfolio analytics failed'}), 500

@comprehensive_bp.route('/api/watchlist/manage', methods=['GET', 'POST', 'DELETE'])
def manage_watchlist():
    """Complete watchlist management with preferences integration"""
    try:
        if request.method == 'GET':
            # Get user's watchlist with AI-enhanced data
            user_preferences = preference_engine.get_user_preferences()
            preferred_sectors = user_preferences.get('preferred_sectors', [])
            
            # Demo watchlist - in production, get from user's saved watchlist
            watchlist_symbols = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA']
            watchlist_data = []
            
            for symbol in watchlist_symbols:
                try:
                    stock_data = enhanced_analyzer.get_enhanced_analysis(symbol)
                    if stock_data:
                        # Get AI analysis with preferences
                        ai_analysis = ai_engine.get_insights(symbol, stock_data)
                        personalized_analysis = preference_engine.get_personalized_analysis(
                            symbol, ai_analysis, current_user.id if current_user and current_user.is_authenticated else None
                        )
                        
                        # Check if this is a preferred sector
                        is_preferred = stock_data.get('sector') in preferred_sectors
                        
                        watchlist_item = {
                            'symbol': symbol,
                            'name': stock_data.get('name', symbol),
                            'price': stock_data['current_price'],
                            'change': stock_data.get('change', 0),
                            'change_percent': stock_data.get('change_percent', 0),
                            'recommendation': personalized_analysis.get('recommendation', 'HOLD'),
                            'confidence': personalized_analysis.get('confidence', 50),
                            'sector': stock_data.get('sector', 'Other'),
                            'is_preferred_sector': is_preferred,
                            'ai_note': personalized_analysis.get('risk_note', ''),
                            'last_updated': datetime.now().isoformat()
                        }
                        
                        watchlist_data.append(watchlist_item)
                        
                except Exception as e:
                    logger.error(f"Error processing watchlist item {symbol}: {e}")
            
            return jsonify({
                'success': True,
                'watchlist': watchlist_data,
                'count': len(watchlist_data),
                'preferences_applied': True
            })
            
        elif request.method == 'POST':
            # Add to watchlist
            data = request.get_json()
            symbol = data.get('symbol', '').upper()
            
            if not symbol:
                return jsonify({'error': 'Symbol required'}), 400
            
            # Validate symbol exists
            stock_data = enhanced_analyzer.get_enhanced_analysis(symbol)
            if not stock_data:
                return jsonify({'error': 'Invalid stock symbol'}), 400
            
            # Add to user's watchlist (simplified - in production, save to database)
            return jsonify({
                'success': True,
                'message': f'Added {symbol} to watchlist',
                'symbol': symbol,
                'name': stock_data.get('name', symbol)
            })
            
        elif request.method == 'DELETE':
            # Remove from watchlist
            data = request.get_json()
            symbol = data.get('symbol', '').upper()
            
            if not symbol:
                return jsonify({'error': 'Symbol required'}), 400
            
            return jsonify({
                'success': True,
                'message': f'Removed {symbol} from watchlist',
                'symbol': symbol
            })
            
    except Exception as e:
        logger.error(f'Error managing watchlist: {e}')
        return jsonify({'error': 'Watchlist operation failed'}), 500

@comprehensive_bp.route('/api/ai/market-scanner')
def ai_market_scanner():
    """AI-powered market scanner with personalized filters"""
    try:
        user_preferences = preference_engine.get_user_preferences()
        risk_tolerance = user_preferences.get('risk_tolerance', 'moderate')
        preferred_sectors = user_preferences.get('preferred_sectors', [])
        
        # Popular stocks to scan
        scan_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX',
            'JPM', 'V', 'JNJ', 'WMT', 'PG', 'UNH', 'DIS', 'HD', 'MA', 'PYPL'
        ]
        
        opportunities = []
        alerts = []
        
        for symbol in scan_symbols:
            try:
                stock_data = enhanced_analyzer.get_enhanced_analysis(symbol)
                if stock_data:
                    # Get AI analysis
                    ai_analysis = ai_engine.get_insights(symbol, stock_data)
                    personalized_analysis = preference_engine.get_personalized_analysis(
                        symbol, ai_analysis, current_user.id if current_user.is_authenticated else None
                    )
                    
                    # Check for opportunities based on preferences
                    recommendation = personalized_analysis.get('recommendation', 'HOLD')
                    confidence = personalized_analysis.get('confidence', 0)
                    sector = stock_data.get('sector', 'Other')
                    
                    # Filter based on risk tolerance
                    min_confidence = {'conservative': 80, 'moderate': 70, 'aggressive': 60}
                    threshold = min_confidence.get(risk_tolerance, 70)
                    
                    if recommendation in ['BUY', 'STRONG_BUY'] and confidence >= threshold:
                        opportunity = {
                            'symbol': symbol,
                            'name': stock_data.get('name', symbol),
                            'price': stock_data['current_price'],
                            'recommendation': recommendation,
                            'confidence': confidence,
                            'sector': sector,
                            'reason': personalized_analysis.get('analysis', 'AI identified opportunity'),
                            'is_preferred_sector': sector in preferred_sectors,
                            'risk_level': personalized_analysis.get('risk_level', 'Medium')
                        }
                        opportunities.append(opportunity)
                    
                    # Check for alerts based on significant moves
                    change_percent = abs(stock_data.get('change_percent', 0))
                    if change_percent >= 5:  # Significant move
                        alert = {
                            'symbol': symbol,
                            'name': stock_data.get('name', symbol),
                            'change_percent': stock_data.get('change_percent', 0),
                            'price': stock_data['current_price'],
                            'alert_type': 'significant_move',
                            'description': f'{symbol} moved {change_percent:.1f}% today'
                        }
                        alerts.append(alert)
                        
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
        
        # Sort opportunities by confidence
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Sort alerts by magnitude of move
        alerts.sort(key=lambda x: abs(x['change_percent']), reverse=True)
        
        return jsonify({
            'success': True,
            'data': {
                'opportunities': opportunities[:10],  # Top 10
                'alerts': alerts[:5],  # Top 5 alerts
                'scan_time': datetime.now().isoformat(),
                'symbols_scanned': len(scan_symbols),
                'preferences': {
                    'risk_tolerance': risk_tolerance,
                    'preferred_sectors': preferred_sectors
                }
            }
        })
        
    except Exception as e:
        logger.error(f'Error running market scanner: {e}')
        return jsonify({'error': 'Market scanner failed'}), 500

@comprehensive_bp.route('/api/ai/sentiment-analysis/<symbol>')
def sentiment_analysis(symbol):
    """AI sentiment analysis for specific stock"""
    try:
        symbol = symbol.upper()
        
        # Get stock data
        stock_data = enhanced_analyzer.get_enhanced_analysis(symbol)
        if not stock_data:
            return jsonify({'error': 'Stock not found'}), 404
        
        # Get comprehensive AI analysis
        ai_analysis = ai_engine.get_insights(symbol, stock_data)
        
        # Apply user preferences if logged in
        if current_user and current_user.is_authenticated:
            ai_analysis = preference_engine.get_personalized_analysis(
                symbol, ai_analysis, current_user.id
            )
        
        # Generate sentiment data
        sentiment_data = {
            'symbol': symbol,
            'overall_sentiment': ai_analysis.get('market_sentiment', 'Neutral'),
            'sentiment_score': ai_analysis.get('confidence', 50),
            'technical_sentiment': 'Bullish' if ai_analysis.get('technical_score', 50) > 60 else 'Bearish',
            'fundamental_sentiment': 'Positive' if ai_analysis.get('fundamental_score', 50) > 60 else 'Negative',
            'recommendation': ai_analysis.get('recommendation', 'HOLD'),
            'confidence': ai_analysis.get('confidence', 50),
            'key_factors': [
                'Strong technical indicators' if ai_analysis.get('technical_score', 50) > 70 else 'Weak technical setup',
                'Solid fundamentals' if ai_analysis.get('fundamental_score', 50) > 70 else 'Fundamental concerns',
                f"Market sentiment: {ai_analysis.get('market_sentiment', 'Neutral')}"
            ],
            'risk_assessment': ai_analysis.get('risk_level', 'Medium'),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': sentiment_data
        })
        
    except Exception as e:
        logger.error(f'Error analyzing sentiment for {symbol}: {e}')
        return jsonify({'error': 'Sentiment analysis failed'}), 500

@comprehensive_bp.route('/api/tools/dcf-calculator', methods=['POST'])
def dcf_calculator():
    """Discounted Cash Flow calculator with AI insights"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        
        if not symbol:
            return jsonify({'error': 'Symbol required'}), 400
        
        # Get financial data
        ticker = yf.Ticker(symbol)
        info = ticker.info
        financials = ticker.financials
        
        # Extract key metrics for DCF
        free_cash_flow = info.get('freeCashflow', 0)
        revenue = info.get('totalRevenue', 0)
        market_cap = info.get('marketCap', 0)
        shares_outstanding = info.get('sharesOutstanding', 1)
        
        # Simple DCF calculation
        discount_rate = 0.10  # 10% discount rate
        terminal_growth = 0.03  # 3% terminal growth
        projection_years = 5
        
        # Project future cash flows (simplified growth model)
        growth_rate = 0.05  # Assume 5% growth
        projected_fcf = []
        current_fcf = free_cash_flow if free_cash_flow > 0 else revenue * 0.1  # Fallback
        
        for year in range(1, projection_years + 1):
            future_fcf = current_fcf * ((1 + growth_rate) ** year)
            discounted_fcf = future_fcf / ((1 + discount_rate) ** year)
            projected_fcf.append({
                'year': year,
                'projected_fcf': future_fcf,
                'discounted_fcf': discounted_fcf
            })
        
        # Terminal value
        terminal_fcf = current_fcf * ((1 + growth_rate) ** projection_years) * (1 + terminal_growth)
        terminal_value = terminal_fcf / (discount_rate - terminal_growth)
        discounted_terminal_value = terminal_value / ((1 + discount_rate) ** projection_years)
        
        # Calculate intrinsic value
        total_dcf_value = sum([fcf['discounted_fcf'] for fcf in projected_fcf]) + discounted_terminal_value
        intrinsic_value_per_share = total_dcf_value / shares_outstanding
        
        # Current price and valuation
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        upside_potential = ((intrinsic_value_per_share - current_price) / current_price) * 100 if current_price > 0 else 0
        
        dcf_result = {
            'symbol': symbol,
            'current_price': current_price,
            'intrinsic_value': intrinsic_value_per_share,
            'upside_potential_percent': upside_potential,
            'valuation_summary': 'Undervalued' if upside_potential > 10 else 'Overvalued' if upside_potential < -10 else 'Fair Value',
            'assumptions': {
                'discount_rate': discount_rate,
                'growth_rate': growth_rate,
                'terminal_growth': terminal_growth,
                'projection_years': projection_years
            },
            'projected_cash_flows': projected_fcf,
            'terminal_value': terminal_value,
            'total_enterprise_value': total_dcf_value,
            'ai_insights': [
                f"Based on current fundamentals, {symbol} appears {('undervalued' if upside_potential > 0 else 'overvalued')}",
                f"DCF model suggests {abs(upside_potential):.1f}% {'upside' if upside_potential > 0 else 'downside'} potential",
                "Model assumes conservative growth - actual results may vary"
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': dcf_result
        })
        
    except Exception as e:
        logger.error(f'Error calculating DCF for {symbol}: {e}')
        return jsonify({'error': 'DCF calculation failed'}), 500

@comprehensive_bp.route('/api/analysis/compare', methods=['POST'])
def compare_stocks():
    """AI-powered stock comparison with preference weighting"""
    try:
        data = request.get_json()
        symbols = [s.upper() for s in data.get('symbols', [])]
        
        if len(symbols) < 2:
            return jsonify({'error': 'At least 2 symbols required for comparison'}), 400
        
        comparison_data = {
            'symbols': symbols,
            'comparison_matrix': [],
            'winner': None,
            'ai_summary': '',
            'timestamp': datetime.now().isoformat()
        }
        
        stock_analyses = []
        
        # Get analysis for each stock
        for symbol in symbols:
            stock_data = enhanced_analyzer.get_enhanced_analysis(symbol)
            if stock_data:
                ai_analysis = ai_engine.get_insights(symbol, stock_data)
                
                # Apply user preferences if logged in
                if current_user and current_user.is_authenticated:
                    ai_analysis = preference_engine.get_personalized_analysis(
                        symbol, ai_analysis, current_user.id
                    )
                
                stock_analysis = {
                    'symbol': symbol,
                    'name': stock_data.get('name', symbol),
                    'price': stock_data['current_price'],
                    'recommendation': ai_analysis.get('recommendation', 'HOLD'),
                    'confidence': ai_analysis.get('confidence', 50),
                    'technical_score': ai_analysis.get('technical_score', 50),
                    'fundamental_score': ai_analysis.get('fundamental_score', 50),
                    'risk_level': ai_analysis.get('risk_level', 'Medium'),
                    'pe_ratio': stock_data.get('pe_ratio'),
                    'market_cap': stock_data.get('market_cap'),
                    'sector': stock_data.get('sector', 'Other'),
                    'overall_score': (ai_analysis.get('technical_score', 50) + ai_analysis.get('fundamental_score', 50)) / 2
                }
                stock_analyses.append(stock_analysis)
        
        # Create comparison matrix
        for analysis in stock_analyses:
            comparison_data['comparison_matrix'].append(analysis)
        
        # Determine winner based on overall score and user preferences
        if stock_analyses:
            winner = max(stock_analyses, key=lambda x: x['overall_score'])
            comparison_data['winner'] = winner['symbol']
            
            # Generate AI summary
            comparison_data['ai_summary'] = f"""
            Based on our AI analysis, {winner['symbol']} emerges as the top choice with an overall score of {winner['overall_score']:.1f}. 
            Key advantages include a {winner['recommendation']} recommendation with {winner['confidence']:.1f}% confidence. 
            {winner['symbol']} shows strong {'technical' if winner['technical_score'] > winner['fundamental_score'] else 'fundamental'} characteristics.
            Risk level is assessed as {winner['risk_level']}.
            """.strip()
        
        return jsonify({
            'success': True,
            'data': comparison_data
        })
        
    except Exception as e:
        logger.error(f'Error comparing stocks: {e}')
        return jsonify({'error': 'Stock comparison failed'}), 500

# Export the blueprint
__all__ = ['comprehensive_bp']