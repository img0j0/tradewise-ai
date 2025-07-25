"""
OAuth Authentication Module for TradeWise AI
Support for Google, Microsoft, and GitHub OAuth providers
"""

from flask import Blueprint, redirect, url_for, session, flash, request, jsonify
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from flask_login import login_user, current_user
from sqlalchemy.orm.exc import NoResultFound
from models import User, db
import os
import logging

logger = logging.getLogger(__name__)

# OAuth Consumer model for flask-dance
class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

# Create OAuth blueprints
def create_oauth_blueprints(app):
    """Create and configure OAuth blueprints"""
    
    # Google OAuth
    google_bp = make_google_blueprint(
        client_id=os.environ.get('GOOGLE_OAUTH_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET'),
        scope=['openid', 'email', 'profile'],
        storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
    )
    
    # Microsoft OAuth - Simplified for now (uncomment when needed)
    # microsoft_bp = make_microsoft_blueprint(
    #     client_id=os.environ.get('MICROSOFT_OAUTH_CLIENT_ID'),
    #     client_secret=os.environ.get('MICROSOFT_OAUTH_CLIENT_SECRET'),
    #     scope=['openid', 'email', 'profile'],
    #     storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
    # )
    
    # GitHub OAuth
    github_bp = make_github_blueprint(
        client_id=os.environ.get('GITHUB_OAUTH_CLIENT_ID'),
        client_secret=os.environ.get('GITHUB_OAUTH_CLIENT_SECRET'),
        scope='user:email',
        storage=SQLAlchemyStorage(OAuth, db.session, user=current_user)
    )
    
    # Register blueprints
    app.register_blueprint(google_bp, url_prefix='/auth')
    # app.register_blueprint(microsoft_bp, url_prefix='/auth')  # Disabled for now
    app.register_blueprint(github_bp, url_prefix='/auth')
    
    return google_bp, None, github_bp

# OAuth authorization handlers
@oauth_authorized.connect_via(make_google_blueprint())
def google_logged_in(blueprint, token):
    """Handle Google OAuth login"""
    if not token:
        flash('Failed to log in with Google.', 'error')
        return False
    
    try:
        resp = blueprint.session.get('/oauth2/v1/userinfo')
        if not resp.ok:
            flash('Failed to fetch user info from Google.', 'error')
            return False
        
        google_info = resp.json()
        return handle_oauth_login(
            provider='google',
            provider_id=google_info['id'],
            email=google_info['email'],
            name=google_info.get('name', ''),
            avatar_url=google_info.get('picture', '')
        )
        
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        flash('Google login failed.', 'error')
        return False

# Microsoft OAuth handler disabled for now
# @oauth_authorized.connect_via(make_microsoft_blueprint())
# def microsoft_logged_in(blueprint, token):
#     """Handle Microsoft OAuth login"""
#     # Implementation here when Microsoft OAuth is enabled

@oauth_authorized.connect_via(make_github_blueprint())
def github_logged_in(blueprint, token):
    """Handle GitHub OAuth login"""
    if not token:
        flash('Failed to log in with GitHub.', 'error')
        return False
    
    try:
        resp = blueprint.session.get('/user')
        if not resp.ok:
            flash('Failed to fetch user info from GitHub.', 'error')
            return False
        
        github_info = resp.json()
        
        # Get email if not public
        email = github_info.get('email')
        if not email:
            email_resp = blueprint.session.get('/user/emails')
            if email_resp.ok:
                emails = email_resp.json()
                primary_email = next((e for e in emails if e['primary']), None)
                if primary_email:
                    email = primary_email['email']
        
        if not email:
            flash('Could not access email from GitHub. Please make your email public.', 'error')
            return False
        
        return handle_oauth_login(
            provider='github',
            provider_id=github_info['id'],
            email=email,
            name=github_info.get('name', github_info.get('login', '')),
            avatar_url=github_info.get('avatar_url', '')
        )
        
    except Exception as e:
        logger.error(f"GitHub OAuth error: {e}")
        flash('GitHub login failed.', 'error')
        return False

def handle_oauth_login(provider, provider_id, email, name, avatar_url=None):
    """Handle OAuth login for any provider"""
    try:
        # Check if user exists with this OAuth provider
        oauth_user = db.session.query(OAuth).filter_by(
            provider=provider,
            provider_user_id=str(provider_id)
        ).first()
        
        if oauth_user:
            # User exists, log them in
            user = oauth_user.user
            login_user(user, remember=True)
            session['user_id'] = user.id
            flash(f'Successfully logged in with {provider.title()}!', 'success')
            return False  # Don't redirect
        
        # Check if user exists with this email
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            # Link OAuth account to existing user
            oauth_entry = OAuth(
                provider=provider,
                provider_user_id=str(provider_id),
                user=existing_user
            )
            db.session.add(oauth_entry)
            
            # Update OAuth fields
            existing_user.oauth_provider = provider
            existing_user.oauth_id = str(provider_id)
            
            db.session.commit()
            
            login_user(existing_user, remember=True)
            session['user_id'] = existing_user.id
            flash(f'{provider.title()} account linked successfully!', 'success')
            return False
        
        # Create new user
        username = email.split('@')[0]
        # Ensure username is unique
        counter = 1
        original_username = username
        while User.query.filter_by(username=username).first():
            username = f"{original_username}{counter}"
            counter += 1
        
        new_user = User(
            username=username,
            email=email,
            oauth_provider=provider,
            oauth_id=str(provider_id),
            plan_type='free',
            subscription_status='active',  # Free plan is always active
            onboarding_completed=False  # Trigger onboarding flow
        )
        
        db.session.add(new_user)
        db.session.flush()  # Get user ID
        
        # Create OAuth entry
        oauth_entry = OAuth(
            provider=provider,
            provider_user_id=str(provider_id),
            user=new_user
        )
        db.session.add(oauth_entry)
        db.session.commit()
        
        login_user(new_user, remember=True)
        session['user_id'] = new_user.id
        session['show_onboarding'] = True  # Trigger onboarding
        
        flash(f'Account created successfully with {provider.title()}!', 'success')
        logger.info(f"New user created via {provider} OAuth: {email}")
        
        return False
        
    except Exception as e:
        logger.error(f"OAuth login error: {e}")
        db.session.rollback()
        flash('Login failed. Please try again.', 'error')
        return False

# OAuth routes blueprint
oauth_bp = Blueprint('oauth', __name__, url_prefix='/oauth')

@oauth_bp.route('/disconnect/<provider>')
def disconnect_oauth(provider):
    """Disconnect OAuth provider from account"""
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        # Remove OAuth entry
        oauth_entry = db.session.query(OAuth).filter_by(
            provider=provider,
            user_id=current_user.id
        ).first()
        
        if oauth_entry:
            db.session.delete(oauth_entry)
            
            # Clear OAuth fields if this was the only provider
            if current_user.oauth_provider == provider:
                current_user.oauth_provider = None
                current_user.oauth_id = None
            
            db.session.commit()
            flash(f'{provider.title()} account disconnected.', 'success')
        else:
            flash(f'{provider.title()} account not found.', 'warning')
        
        return redirect(url_for('main.settings'))
        
    except Exception as e:
        logger.error(f"OAuth disconnect error: {e}")
        db.session.rollback()
        flash('Failed to disconnect account.', 'error')
        return redirect(url_for('main.settings'))

@oauth_bp.route('/status')
def oauth_status():
    """Get OAuth connection status for current user"""
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 401
    
    try:
        oauth_connections = db.session.query(OAuth).filter_by(
            user_id=current_user.id
        ).all()
        
        connected_providers = {
            oauth.provider: {
                'provider': oauth.provider,
                'connected_at': oauth.created_at.isoformat() if hasattr(oauth, 'created_at') else None
            }
            for oauth in oauth_connections
        }
        
        return jsonify({
            'success': True,
            'oauth_connections': connected_providers,
            'available_providers': ['google', 'github']
        })
        
    except Exception as e:
        logger.error(f"OAuth status error: {e}")
        return jsonify({'success': False, 'error': 'Failed to get OAuth status'}), 500