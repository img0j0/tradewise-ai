from app import db
from datetime import datetime
from sqlalchemy import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Analysis preferences
    preferred_sectors = db.Column(db.Text)  # JSON string of preferred sectors
    analysis_settings = db.Column(db.Text)  # JSON string of user analysis preferences
    
    # Watchlist data stored as JSON for stock analysis tracking
    watchlists = db.Column(db.Text)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class StockAnalysis(db.Model):
    """Store historical stock analysis results for comparison and tracking"""
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, index=True)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    price_at_analysis = db.Column(db.Float, nullable=False)
    
    # AI Analysis Results
    recommendation = db.Column(db.String(10), nullable=False)  # BUY, SELL, HOLD
    confidence_score = db.Column(db.Float, nullable=False)
    fundamental_score = db.Column(db.Float, nullable=False)
    technical_score = db.Column(db.Float, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    
    # Analysis Details (stored as JSON)
    analysis_details = db.Column(db.Text)  # JSON string with detailed analysis
    market_conditions = db.Column(db.Text)  # JSON string with market context
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'analysis_date': self.analysis_date.isoformat(),
            'price_at_analysis': self.price_at_analysis,
            'recommendation': self.recommendation,
            'confidence_score': self.confidence_score,
            'fundamental_score': self.fundamental_score,
            'technical_score': self.technical_score,
            'risk_level': self.risk_level
        }

class WatchlistItem(db.Model):
    """Simple watchlist for tracking stocks of interest"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Optional user association
    symbol = db.Column(db.String(10), nullable=False, index=True)
    added_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)  # User notes about why they're watching this stock
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'added_date': self.added_date.isoformat(),
            'notes': self.notes
        }