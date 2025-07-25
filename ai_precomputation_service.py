"""
AI Pre-computation Service for TradeWise AI
Periodically computes AI analysis for popular stocks to reduce response times
"""

import threading
import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
from app import cache, db
from models import StockAnalysis
from ai_insights import AIInsightsEngine
from simple_personalization import SimplePersonalization
from external_api_optimizer import yahoo_optimizer
from performance_monitor import performance_optimized
from sqlalchemy import text

logger = logging.getLogger(__name__)

class AIPrecomputationService:
    """Background service for pre-computing AI analysis on popular stocks"""
    
    def __init__(self):
        self.ai_engine = AIInsightsEngine()
        self.personalization = SimplePersonalization()
        self.is_running = False
        self.popular_symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 
            'NFLX', 'AMD', 'CRM', 'RIVN', 'PLTR', 'SNOW', 'COIN',
            'PYPL', 'SQ', 'UBER', 'LYFT', 'ZM', 'SHOP'
        ]
        self.strategies = ['growth_investor', 'value_investor', 'dividend_investor', 'momentum_investor']
        
    def start_background_service(self):
        """Start the background pre-computation service"""
        if self.is_running:
            logger.info("Pre-computation service already running")
            return
        
        self.is_running = True
        
        # Schedule periodic updates
        schedule.every(5).minutes.do(self._precompute_popular_stocks)
        schedule.every(15).minutes.do(self._precompute_trending_stocks)
        schedule.every(30).minutes.do(self._cleanup_old_cache)
        
        # Start scheduler in background thread
        def run_scheduler():
            logger.info("AI Pre-computation service started")
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Error in pre-computation scheduler: {e}")
                    time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # Run initial pre-computation
        self._initial_precomputation()
    
    def stop_service(self):
        """Stop the pre-computation service"""
        self.is_running = False
        schedule.clear()
        logger.info("AI Pre-computation service stopped")
    
    @performance_optimized()
    def _initial_precomputation(self):
        """Initial pre-computation of top 10 most popular stocks"""
        logger.info("Starting initial pre-computation...")
        
        # Pre-compute top 10 stocks for all strategies
        top_stocks = self.popular_symbols[:10]
        
        for symbol in top_stocks:
            for strategy in self.strategies:
                try:
                    self._precompute_single_analysis(symbol, strategy)
                    time.sleep(0.5)  # Rate limiting
                except Exception as e:
                    logger.error(f"Error pre-computing {symbol} for {strategy}: {e}")
        
        logger.info(f"Initial pre-computation completed for {len(top_stocks)} stocks")
    
    @performance_optimized()
    def _precompute_popular_stocks(self):
        """Periodic pre-computation of popular stocks"""
        logger.info("Running periodic pre-computation of popular stocks...")
        
        try:
            # Get fresh market data for popular stocks
            market_data = yahoo_optimizer.get_market_data_batch(self.popular_symbols)
            
            # Pre-compute for each strategy
            for strategy in self.strategies:
                for symbol in self.popular_symbols[:15]:  # Top 15 stocks
                    if symbol in market_data and market_data[symbol]:
                        try:
                            self._precompute_single_analysis(symbol, strategy, market_data[symbol])
                        except Exception as e:
                            logger.error(f"Error pre-computing {symbol}: {e}")
            
            logger.info(f"Pre-computed analysis for {len(self.popular_symbols)} stocks")
            
        except Exception as e:
            logger.error(f"Error in periodic pre-computation: {e}")
    
    def _precompute_single_analysis(self, symbol: str, strategy: str, stock_data: Dict = None):
        """Pre-compute AI analysis for a single stock and strategy"""
        try:
            # Get stock data if not provided
            if not stock_data:
                stock_data = yahoo_optimizer._fetch_single_stock(symbol)
                if not stock_data:
                    return
            
            # Generate AI insights
            base_insights = self.ai_engine.get_insights(symbol, stock_data)
            
            # Apply strategy personalization
            self.personalization.current_strategy = strategy
            personalized_insights = self.personalization.personalize_analysis(symbol, base_insights)
            
            # Create comprehensive analysis result
            analysis_result = {
                'success': True,
                'symbol': symbol,
                'stock_info': stock_data,
                'analysis': personalized_insights,
                'competitive_features': {
                    'ai_explanations': personalized_insights.get('ai_explanation', {}),
                    'smart_alerts': personalized_insights.get('smart_alerts', []),
                    'educational_insights': personalized_insights.get('educational_insights', {})
                },
                'strategy': strategy,
                'precomputed': True,
                'computation_time': datetime.now().isoformat(),
                'cache_ttl': 300  # 5 minutes
            }
            
            # Cache the result with strategy-specific key
            cache_key = f"precomputed_analysis:{symbol}:{strategy}"
            try:
                from app import app, cache
                with app.app_context():
                    cache.set(cache_key, analysis_result, timeout=300)
            except Exception as e:
                logger.warning(f"Cache storage error: {e}")
            
            # Store in database for persistence
            self._store_precomputed_analysis(symbol, strategy, analysis_result)
            
            logger.debug(f"Pre-computed analysis for {symbol} ({strategy})")
            
        except Exception as e:
            logger.error(f"Error in single analysis pre-computation for {symbol}: {e}")
    
    def _store_precomputed_analysis(self, symbol: str, strategy: str, analysis_result: Dict):
        """Store pre-computed analysis in database"""
        try:
            # Check if record exists
            existing = db.session.query(StockAnalysis).filter_by(
                symbol=symbol,
                analysis_details=json.dumps({'strategy': strategy})
            ).first()
            
            if existing:
                # Update existing record
                existing.price_at_analysis = analysis_result['stock_info']['current_price']
                existing.recommendation = analysis_result['analysis']['recommendation']
                existing.confidence_score = analysis_result['analysis']['confidence']
                existing.updated_at = datetime.utcnow()
            else:
                # Create new record
                analysis = StockAnalysis()
                analysis.symbol = symbol
                analysis.price_at_analysis = analysis_result['stock_info']['current_price']
                analysis.recommendation = analysis_result['analysis']['recommendation']
                analysis.confidence_score = analysis_result['analysis']['confidence']
                analysis.analysis_details = json.dumps({
                    'strategy': strategy,
                    'precomputed': True,
                    'full_analysis': analysis_result['analysis']
                })
                db.session.add(analysis)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error storing pre-computed analysis: {e}")
            db.session.rollback()
    
    def _precompute_trending_stocks(self):
        """Pre-compute analysis for trending/volatile stocks"""
        try:
            # Get market movers (simulated - in production, use real market data)
            trending_symbols = ['RIVN', 'PLTR', 'SNOW', 'COIN', 'SQ']
            
            logger.info("Pre-computing trending stocks...")
            
            for symbol in trending_symbols:
                for strategy in self.strategies[:2]:  # Just growth and value for trending
                    try:
                        self._precompute_single_analysis(symbol, strategy)
                        time.sleep(0.3)
                    except Exception as e:
                        logger.error(f"Error pre-computing trending {symbol}: {e}")
                        
        except Exception as e:
            logger.error(f"Error in trending pre-computation: {e}")
    
    def _cleanup_old_cache(self):
        """Clean up old pre-computed cache entries"""
        try:
            # Note: Flask-Caching simple backend doesn't support pattern deletion
            # In production with Redis, implement proper cache cleanup
            logger.info("Cache cleanup completed (using TTL expiration)")
            
        except Exception as e:
            logger.error(f"Error in cache cleanup: {e}")
    
    def get_precomputed_analysis(self, symbol: str, strategy: str = 'growth_investor') -> Dict:
        """Get pre-computed analysis if available"""
        try:
            cache_key = f"precomputed_analysis:{symbol}:{strategy}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                logger.info(f"Found pre-computed analysis for {symbol} ({strategy})")
                return cached_result
            
            # Fallback to database
            db_result = db.session.query(StockAnalysis).filter_by(
                symbol=symbol
            ).filter(
                StockAnalysis.analysis_details.contains(f'"strategy": "{strategy}"')
            ).order_by(StockAnalysis.updated_at.desc()).first()
            
            if db_result and db_result.updated_at > datetime.utcnow() - timedelta(minutes=10):
                # Reconstruct result from database
                analysis_details = json.loads(db_result.analysis_details)
                if analysis_details.get('precomputed'):
                    logger.info(f"Found database pre-computed analysis for {symbol}")
                    return analysis_details.get('full_analysis', {})
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving pre-computed analysis: {e}")
            return None
    
    def get_service_stats(self) -> Dict:
        """Get pre-computation service statistics"""
        try:
            stats = {
                'service_running': self.is_running,
                'popular_symbols_count': len(self.popular_symbols),
                'strategies_count': len(self.strategies),
                'last_update': datetime.now().isoformat(),
                'cache_status': 'active'
            }
            
            # Count pre-computed entries in database
            precomputed_count = db.session.query(StockAnalysis).filter(
                StockAnalysis.analysis_details.contains('"precomputed": true')
            ).count()
            
            stats['precomputed_analyses'] = precomputed_count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting service stats: {e}")
            return {'error': str(e)}

# Global service instance
precomputation_service = AIPrecomputationService()