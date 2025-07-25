from app import db
from datetime import datetime
import json
import secrets
import pyotp
from sqlalchemy import func, ForeignKey
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Enhanced subscription fields for multiple tiers
    plan_type = db.Column(db.String(20), default='free')  # 'free', 'pro', 'enterprise'
    subscription_status = db.Column(db.String(20), default='inactive')  # 'active', 'trialing', 'past_due', 'canceled', 'incomplete'
    trial_end_date = db.Column(db.DateTime)
    subscription_start = db.Column(db.DateTime)
    subscription_end = db.Column(db.DateTime)
    
    # Stripe integration fields
    stripe_customer_id = db.Column(db.String(100), unique=True)
    stripe_subscription_id = db.Column(db.String(100), unique=True)
    stripe_price_id = db.Column(db.String(100))  # Current plan price ID
    
    # OAuth integration fields
    oauth_provider = db.Column(db.String(50))  # 'google', 'microsoft', 'github', None
    oauth_id = db.Column(db.String(100))  # External provider user ID
    
    # Two-Factor Authentication
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32))  # TOTP secret
    backup_codes = db.Column(db.Text)  # JSON array of backup codes
    
    # Team and role management for Enterprise
    team_id = db.Column(db.Integer, ForeignKey('team.id'), nullable=True)
    role = db.Column(db.String(20), default='user')  # 'admin', 'analyst', 'viewer', 'user'
    
    # Usage tracking for plan limits
    api_requests_today = db.Column(db.Integer, default=0)
    api_requests_reset_date = db.Column(db.Date, default=datetime.utcnow().date)
    
    # User preferences and onboarding
    preferred_markets = db.Column(db.Text)  # JSON array of preferred markets
    alert_preferences = db.Column(db.Text)  # JSON object of alert settings
    onboarding_completed = db.Column(db.Boolean, default=False)
    preferred_sectors = db.Column(db.Text)  # JSON string of preferred sectors
    analysis_settings = db.Column(db.Text)  # JSON string of user analysis preferences
    
    # Watchlist data stored as JSON for stock analysis tracking
    watchlists = db.Column(db.Text)
    
    # Relationships
    team = db.relationship('Team', back_populates='members', lazy='select')
    team_invitations = db.relationship('TeamInvitation', back_populates='user', lazy='select')
    subscription_history = db.relationship('SubscriptionHistory', back_populates='user', lazy='select')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_2fa_secret(self):
        """Generate and store TOTP secret for 2FA"""
        self.two_factor_secret = pyotp.random_base32()
        return self.two_factor_secret
    
    def get_2fa_uri(self, app_name="TradeWise AI"):
        """Get TOTP URI for QR code generation"""
        if not self.two_factor_secret:
            self.generate_2fa_secret()
        return pyotp.totp.TOTP(self.two_factor_secret).provisioning_uri(
            name=self.email,
            issuer_name=app_name
        )
    
    def verify_2fa_token(self, token):
        """Verify TOTP token"""
        if not self.two_factor_secret:
            return False
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self, count=8):
        """Generate backup codes for 2FA recovery"""
        codes = [secrets.token_hex(4).upper() for _ in range(count)]
        self.backup_codes = json.dumps(codes)
        return codes
    
    def verify_backup_code(self, code):
        """Verify and consume a backup code"""
        if not self.backup_codes:
            return False
        
        codes = json.loads(self.backup_codes)
        if code.upper() in codes:
            codes.remove(code.upper())
            self.backup_codes = json.dumps(codes)
            return True
        return False
    
    def is_plan_active(self):
        """Check if user has any active paid plan"""
        if self.plan_type == 'free':
            return True  # Free plan is always active
        
        if self.subscription_status not in ['active', 'trialing']:
            return False
            
        # Check trial period
        if self.subscription_status == 'trialing' and self.trial_end_date:
            if self.trial_end_date < datetime.utcnow():
                return False
                
        # Check subscription end date
        if self.subscription_end and self.subscription_end < datetime.utcnow():
            return False
            
        return True
    
    def is_premium_active(self):
        """Check if user has active premium (Pro or Enterprise) subscription"""
        return self.plan_type in ['pro', 'enterprise'] and self.is_plan_active()
    
    def has_plan_access(self, required_plan):
        """Check if user has access to features of a specific plan level"""
        if not self.is_plan_active():
            return False
            
        plan_hierarchy = {'free': 0, 'pro': 1, 'enterprise': 2}
        user_level = plan_hierarchy.get(self.plan_type, 0)
        required_level = plan_hierarchy.get(required_plan, 0)
        
        return user_level >= required_level
    
    def check_api_rate_limit(self, daily_limit):
        """Check and update API rate limiting"""
        from datetime import date
        today = date.today()
        
        # Reset counter if new day
        if self.api_requests_reset_date != today:
            self.api_requests_today = 0
            self.api_requests_reset_date = today
        
        # Check if within limit
        if self.api_requests_today >= daily_limit:
            return False
        
        # Increment counter
        self.api_requests_today += 1
        return True
    
    def can_invite_team_members(self):
        """Check if user can invite team members (Enterprise only)"""
        return self.plan_type == 'enterprise' and self.role in ['admin']
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'plan_type': self.plan_type,
            'subscription_status': self.subscription_status,
            'is_premium': self.is_premium_active(),
            'trial_end_date': self.trial_end_date.isoformat() if self.trial_end_date else None,
            'two_factor_enabled': self.two_factor_enabled,
            'oauth_provider': self.oauth_provider,
            'team_id': self.team_id,
            'role': self.role,
            'onboarding_completed': self.onboarding_completed
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

class FavoriteStock(db.Model):
    """User favorite stocks for quick access"""
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, index=True)
    company_name = db.Column(db.String(255))
    sector = db.Column(db.String(100))
    user_session = db.Column(db.String(100), index=True)  # Track by session for now
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'company_name': self.company_name,
            'sector': self.sector,
            'timestamp': self.timestamp.isoformat()
        }

class SearchHistory(db.Model):
    """Track user search history for quick re-access"""
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False, index=True)
    company_name = db.Column(db.String(255))
    search_query = db.Column(db.String(100))  # What user typed to find this stock
    user_session = db.Column(db.String(100), index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    access_count = db.Column(db.Integer, default=1)  # How many times accessed
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'company_name': self.company_name,
            'search_query': self.search_query,
            'timestamp': self.timestamp.isoformat(),
            'access_count': self.access_count
        }

class Team(db.Model):
    """Team model for Enterprise plan multi-user access"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    max_seats = db.Column(db.Integer, default=10)  # Based on Enterprise plan
    
    # Relationships
    owner = db.relationship('User', foreign_keys=[owner_id], lazy='select')
    members = db.relationship('User', foreign_keys='User.team_id', back_populates='team', lazy='select')
    invitations = db.relationship('TeamInvitation', back_populates='team', lazy='select')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'owner_id': self.owner_id,
            'max_seats': self.max_seats,
            'current_members': len(self.members) if hasattr(self, '_members_loaded') and self.members else 0
        }
    
    def can_add_member(self):
        """Check if team can add more members"""
        current_count = User.query.filter_by(team_id=self.id).count()
        return current_count < self.max_seats

class TeamInvitation(db.Model):
    """Team invitation model for inviting users to Enterprise teams"""
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, ForeignKey('team.id'), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='analyst')  # 'admin', 'analyst', 'viewer'
    invited_by = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    invited_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # Invitation expiry
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'rejected', 'expired'
    invitation_token = db.Column(db.String(100), unique=True)
    
    # For existing users
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=True)
    
    # Relationships
    team = db.relationship('Team', back_populates='invitations', lazy='select')
    inviter = db.relationship('User', foreign_keys=[invited_by], lazy='select')
    user = db.relationship('User', foreign_keys=[user_id], back_populates='team_invitations', lazy='select')
    
    def generate_token(self):
        """Generate unique invitation token"""
        self.invitation_token = secrets.token_urlsafe(32)
        return self.invitation_token
    
    def is_expired(self):
        """Check if invitation is expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'team_id': self.team_id,
            'email': self.email,
            'role': self.role,
            'invited_at': self.invited_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'status': self.status,
            'is_expired': self.is_expired()
        }

class SubscriptionHistory(db.Model):
    """Track subscription changes and billing history"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    plan_type = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 'subscribed', 'upgraded', 'downgraded', 'canceled', 'renewed'
    amount = db.Column(db.Float)  # Amount charged/refunded
    currency = db.Column(db.String(3), default='USD')
    stripe_invoice_id = db.Column(db.String(100))
    stripe_payment_intent_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    additional_data = db.Column(db.Text)  # JSON string for additional data
    
    # Relationships
    user = db.relationship('User', back_populates='subscription_history', lazy='select')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_type': self.plan_type,
            'action': self.action,
            'amount': self.amount,
            'currency': self.currency,
            'created_at': self.created_at.isoformat(),
            'additional_data': json.loads(self.additional_data) if self.additional_data and isinstance(self.additional_data, str) else {}
        }

class PlanConfiguration(db.Model):
    """Store plan configurations and pricing"""
    id = db.Column(db.Integer, primary_key=True)
    plan_name = db.Column(db.String(50), unique=True, nullable=False)  # 'free', 'pro', 'enterprise'
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    monthly_price = db.Column(db.Float, default=0)
    annual_price = db.Column(db.Float, default=0)
    stripe_monthly_price_id = db.Column(db.String(100))
    stripe_annual_price_id = db.Column(db.String(100))
    
    # Feature limits
    api_requests_per_day = db.Column(db.Integer, default=100)
    max_alerts = db.Column(db.Integer, default=5)
    max_watchlist_items = db.Column(db.Integer, default=20)
    team_seats = db.Column(db.Integer, default=1)
    
    # Feature flags
    features = db.Column(db.Text)  # JSON object of enabled features
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'plan_name': self.plan_name,
            'display_name': self.display_name,
            'description': self.description,
            'monthly_price': self.monthly_price,
            'annual_price': self.annual_price,
            'api_requests_per_day': self.api_requests_per_day,
            'max_alerts': self.max_alerts,
            'max_watchlist_items': self.max_watchlist_items,
            'team_seats': self.team_seats,
            'features': json.loads(self.features) if self.features else {}
        }