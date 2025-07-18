
# Database Query Optimization
from sqlalchemy import event
from sqlalchemy.engine import Engine
import time
import logging

# Add query logging for production optimization
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 0.1:  # Log slow queries
        logger.warning(f"Slow query: {total:.2f}s - {statement[:100]}...")

# Enhanced database connection with optimization
from app import app, db

class DatabaseOptimizer:
    @staticmethod
    def optimize_portfolio_queries():
        """Optimize portfolio queries for real-time updates"""
        from models import Portfolio
        
        # Add index on user_id for faster lookups
        try:
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_user_id ON portfolio(user_id)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_portfolio_symbol ON portfolio(symbol)")
        except Exception as e:
            logger.info(f"Index creation skipped: {e}")
    
    @staticmethod
    def optimize_trade_queries():
        """Optimize trade queries for performance"""
        from models import Trade
        
        # Add indexes for common queries
        try:
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_trade_user_id ON trade(user_id)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_trade_symbol ON trade(symbol)")
            db.engine.execute("CREATE INDEX IF NOT EXISTS idx_trade_timestamp ON trade(timestamp)")
        except Exception as e:
            logger.info(f"Index creation skipped: {e}")
    
    @staticmethod
    def apply_optimizations():
        """Apply all database optimizations"""
        with app.app_context():
            DatabaseOptimizer.optimize_portfolio_queries()
            DatabaseOptimizer.optimize_trade_queries()
            logger.info("Database optimizations applied")

# Initialize optimizer
if __name__ == "__main__":
    DatabaseOptimizer.apply_optimizations()
