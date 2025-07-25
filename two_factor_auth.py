"""
Two-Factor Authentication Module for TradeWise AI
TOTP-based 2FA with backup codes and recovery options
"""

import pyotp
import qrcode
import io
import base64
from flask import Blueprint, request, jsonify, session, render_template_string
from flask_login import login_required, current_user
from models import User, db
import logging
import json

logger = logging.getLogger(__name__)

twofa_bp = Blueprint('twofa', __name__, url_prefix='/2fa')

@twofa_bp.route('/setup', methods=['GET'])
@login_required
def setup_2fa():
    """Initialize 2FA setup for user"""
    try:
        if current_user.two_factor_enabled:
            return jsonify({
                'success': False,
                'error': '2FA is already enabled',
                'status': 'already_enabled'
            }), 400
        
        # Generate secret if not exists
        if not current_user.two_factor_secret:
            secret = current_user.generate_2fa_secret()
            db.session.commit()
        else:
            secret = current_user.two_factor_secret
        
        # Generate QR code
        qr_uri = current_user.get_2fa_uri()
        qr_code = generate_qr_code(qr_uri)
        
        return jsonify({
            'success': True,
            'setup_data': {
                'secret': secret,
                'qr_code': qr_code,
                'manual_entry_key': secret,
                'app_name': 'TradeWise AI',
                'account_name': current_user.email
            }
        })
        
    except Exception as e:
        logger.error(f"2FA setup error: {e}")
        return jsonify({'success': False, 'error': 'Failed to setup 2FA'}), 500

@twofa_bp.route('/verify-setup', methods=['POST'])
@login_required
def verify_2fa_setup():
    """Verify 2FA setup with initial token"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({'success': False, 'error': 'Token required'}), 400
        
        if not current_user.two_factor_secret:
            return jsonify({'success': False, 'error': '2FA not initialized'}), 400
        
        # Verify token
        if not current_user.verify_2fa_token(token):
            return jsonify({'success': False, 'error': 'Invalid token'}), 400
        
        # Enable 2FA
        current_user.two_factor_enabled = True
        
        # Generate backup codes
        backup_codes = current_user.generate_backup_codes()
        
        db.session.commit()
        
        logger.info(f"2FA enabled for user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': '2FA enabled successfully',
            'backup_codes': backup_codes
        })
        
    except Exception as e:
        logger.error(f"2FA verification error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to verify 2FA'}), 500

@twofa_bp.route('/disable', methods=['POST'])
@login_required
def disable_2fa():
    """Disable 2FA for user"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        # Verify password
        if not current_user.check_password(password):
            return jsonify({'success': False, 'error': 'Invalid password'}), 400
        
        # Disable 2FA
        current_user.two_factor_enabled = False
        current_user.two_factor_secret = None
        current_user.backup_codes = None
        
        db.session.commit()
        
        logger.info(f"2FA disabled for user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': '2FA disabled successfully'
        })
        
    except Exception as e:
        logger.error(f"2FA disable error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to disable 2FA'}), 500

@twofa_bp.route('/verify', methods=['POST'])
def verify_2fa_login():
    """Verify 2FA token during login"""
    try:
        data = request.get_json()
        user_id = session.get('2fa_user_id')
        token = data.get('token', '').strip()
        use_backup = data.get('use_backup', False)
        
        if not user_id:
            return jsonify({'success': False, 'error': '2FA session expired'}), 400
        
        if not token:
            return jsonify({'success': False, 'error': 'Token required'}), 400
        
        user = User.query.get(user_id)
        if not user or not user.two_factor_enabled:
            return jsonify({'success': False, 'error': 'Invalid 2FA session'}), 400
        
        # Verify token or backup code
        valid = False
        if use_backup:
            valid = user.verify_backup_code(token)
            if valid:
                db.session.commit()  # Save updated backup codes
        else:
            valid = user.verify_2fa_token(token)
        
        if not valid:
            return jsonify({'success': False, 'error': 'Invalid token'}), 400
        
        # Complete login
        from flask_login import login_user
        login_user(user, remember=True)
        session['user_id'] = user.id
        session.pop('2fa_user_id', None)  # Clean up 2FA session
        
        logger.info(f"2FA login successful for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'redirect_url': '/dashboard'
        })
        
    except Exception as e:
        logger.error(f"2FA login verification error: {e}")
        return jsonify({'success': False, 'error': 'Verification failed'}), 500

@twofa_bp.route('/backup-codes', methods=['GET'])
@login_required
def get_backup_codes():
    """Get current backup codes (requires password)"""
    try:
        password = request.args.get('password', '')
        
        # Verify password
        if not current_user.check_password(password):
            return jsonify({'success': False, 'error': 'Invalid password'}), 400
        
        if not current_user.two_factor_enabled:
            return jsonify({'success': False, 'error': '2FA not enabled'}), 400
        
        backup_codes = json.loads(current_user.backup_codes) if current_user.backup_codes else []
        
        return jsonify({
            'success': True,
            'backup_codes': backup_codes,
            'codes_remaining': len(backup_codes)
        })
        
    except Exception as e:
        logger.error(f"Backup codes retrieval error: {e}")
        return jsonify({'success': False, 'error': 'Failed to get backup codes'}), 500

@twofa_bp.route('/backup-codes/regenerate', methods=['POST'])
@login_required
def regenerate_backup_codes():
    """Regenerate backup codes"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        # Verify password
        if not current_user.check_password(password):
            return jsonify({'success': False, 'error': 'Invalid password'}), 400
        
        if not current_user.two_factor_enabled:
            return jsonify({'success': False, 'error': '2FA not enabled'}), 400
        
        # Generate new backup codes
        backup_codes = current_user.generate_backup_codes()
        db.session.commit()
        
        logger.info(f"Backup codes regenerated for user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Backup codes regenerated',
            'backup_codes': backup_codes
        })
        
    except Exception as e:
        logger.error(f"Backup codes regeneration error: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to regenerate backup codes'}), 500

@twofa_bp.route('/status', methods=['GET'])
@login_required
def get_2fa_status():
    """Get 2FA status for current user"""
    try:
        backup_codes_count = 0
        if current_user.backup_codes:
            backup_codes = json.loads(current_user.backup_codes)
            backup_codes_count = len(backup_codes)
        
        return jsonify({
            'success': True,
            'status': {
                'enabled': current_user.two_factor_enabled,
                'secret_configured': bool(current_user.two_factor_secret),
                'backup_codes_remaining': backup_codes_count,
                'needs_backup_codes': current_user.two_factor_enabled and backup_codes_count < 3
            }
        })
        
    except Exception as e:
        logger.error(f"2FA status error: {e}")
        return jsonify({'success': False, 'error': 'Failed to get 2FA status'}), 500

def generate_qr_code(uri):
    """Generate QR code for 2FA setup"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for web display
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
        
    except Exception as e:
        logger.error(f"QR code generation error: {e}")
        return None

# 2FA enforcement decorator
def require_2fa_if_enabled(f):
    """Decorator to enforce 2FA if user has it enabled"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.two_factor_enabled:
            # Check if 2FA was completed in this session
            if not session.get('2fa_verified'):
                return jsonify({
                    'success': False,
                    'error': '2FA verification required',
                    'requires_2fa': True
                }), 403
        
        return f(*args, **kwargs)
    return decorated_function

# 2FA login template
TWOFA_LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Two-Factor Authentication - TradeWise AI</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #1a1a1a; color: white; margin: 0; padding: 20px; }
        .container { max-width: 400px; margin: 50px auto; padding: 30px; background: #2a2a2a; border-radius: 10px; }
        .header { text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: 500; }
        input { width: 100%; padding: 12px; border: 1px solid #444; background: #333; color: white; border-radius: 5px; font-size: 16px; }
        .submit-btn { background: #6366f1; color: white; border: none; padding: 12px 20px; border-radius: 5px; cursor: pointer; width: 100%; font-size: 16px; }
        .submit-btn:hover { background: #5855eb; }
        .backup-link { text-align: center; margin-top: 15px; }
        .backup-link a { color: #6366f1; text-decoration: none; }
        .backup-link a:hover { text-decoration: underline; }
        .error { color: #ef4444; margin-top: 10px; }
        .success { color: #10b981; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🔐 Two-Factor Authentication</h2>
            <p>Enter your authentication code to continue</p>
        </div>
        
        <form id="twofa-form" method="post">
            <div class="form-group">
                <label for="token">Authentication Code</label>
                <input type="text" id="token" name="token" maxlength="6" placeholder="123456" required autofocus>
            </div>
            
            <button type="submit" class="submit-btn">Verify</button>
        </form>
        
        <div class="backup-link">
            <a href="#" onclick="toggleBackupMode()">Use backup code instead</a>
        </div>
        
        <div id="message"></div>
    </div>
    
    <script>
        let useBackup = false;
        
        function toggleBackupMode() {
            useBackup = !useBackup;
            const tokenInput = document.getElementById('token');
            const label = document.querySelector('label[for="token"]');
            const link = document.querySelector('.backup-link a');
            
            if (useBackup) {
                tokenInput.placeholder = 'ABCD-1234';
                tokenInput.maxLength = 9;
                label.textContent = 'Backup Code';
                link.textContent = 'Use authenticator app instead';
            } else {
                tokenInput.placeholder = '123456';
                tokenInput.maxLength = 6;
                label.textContent = 'Authentication Code';
                link.textContent = 'Use backup code instead';
            }
            tokenInput.focus();
        }
        
        document.getElementById('twofa-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const token = document.getElementById('token').value;
            const messageDiv = document.getElementById('message');
            
            try {
                const response = await fetch('/2fa/verify', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        token: token,
                        use_backup: useBackup
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    messageDiv.innerHTML = '<div class="success">Login successful! Redirecting...</div>';
                    setTimeout(() => {
                        window.location.href = data.redirect_url || '/';
                    }, 1000);
                } else {
                    messageDiv.innerHTML = '<div class="error">' + data.error + '</div>';
                }
            } catch (error) {
                messageDiv.innerHTML = '<div class="error">Verification failed. Please try again.</div>';
            }
        });
    </script>
</body>
</html>
"""

@twofa_bp.route('/login')
def twofa_login_page():
    """2FA login page"""
    if not session.get('2fa_user_id'):
        return redirect(url_for('main.login'))
    
    return render_template_string(TWOFA_LOGIN_TEMPLATE)