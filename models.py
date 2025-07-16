from app import db
from datetime import datetime
from sqlalchemy import func

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # 'buy' or 'sell'
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_simulated = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'action': self.action,
            'quantity': self.quantity,
            'price': self.price,
            'confidence_score': self.confidence_score,
            'timestamp': self.timestamp.isoformat(),
            'is_simulated': self.is_simulated
        }

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    avg_price = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'avg_price': self.avg_price,
            'last_updated': self.last_updated.isoformat()
        }

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    alert_type = db.Column(db.String(20), nullable=False)  # 'buy', 'sell', 'watch'
    message = db.Column(db.Text, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'alert_type': self.alert_type,
            'message': self.message,
            'confidence_score': self.confidence_score,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
