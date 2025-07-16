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

class UserAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False, unique=True)  # For future user system
    balance = db.Column(db.Float, default=0.0)
    total_deposited = db.Column(db.Float, default=0.0)
    total_withdrawn = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'balance': self.balance,
            'total_deposited': self.total_deposited,
            'total_withdrawn': self.total_withdrawn,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'deposit', 'withdrawal', 'stock_purchase', 'stock_sale'
    amount = db.Column(db.Float, nullable=False)
    symbol = db.Column(db.String(10), nullable=True)  # For stock transactions
    quantity = db.Column(db.Integer, nullable=True)  # For stock transactions
    price_per_share = db.Column(db.Float, nullable=True)  # For stock transactions
    stripe_payment_intent_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed', 'failed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'transaction_type': self.transaction_type,
            'amount': self.amount,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'price_per_share': self.price_per_share,
            'stripe_payment_intent_id': self.stripe_payment_intent_id,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
