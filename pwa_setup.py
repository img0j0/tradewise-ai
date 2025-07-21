# Progressive Web App Setup for TradeWise AI
import os
from flask import Blueprint, send_from_directory, jsonify, render_template_string, request

pwa_bp = Blueprint('pwa', __name__)

# PWA Manifest Configuration
PWA_MANIFEST = {
    "name": "TradeWise AI - Smart Trading Platform",
    "short_name": "TradeWise AI",
    "description": "AI-powered trading platform with intelligent stock analysis",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#1a1a2e",
    "theme_color": "#8b5cf6",
    "orientation": "portrait-primary",
    "categories": ["finance", "business", "productivity"],
    "lang": "en-US",
    "scope": "/",
    "icons": [
        {
            "src": "/static/icons/icon-72x72.png",
            "sizes": "72x72",
            "type": "image/png",
            "purpose": "maskable any"
        },
        {
            "src": "/static/icons/icon-96x96.png",
            "sizes": "96x96",
            "type": "image/png",
            "purpose": "maskable any"
        },
        {
            "src": "/static/icons/icon-128x128.png",
            "sizes": "128x128",
            "type": "image/png",
            "purpose": "maskable any"
        },
        {
            "src": "/static/icons/icon-144x144.png",
            "sizes": "144x144",
            "type": "image/png",
            "purpose": "maskable any"
        },
        {
            "src": "/static/icons/icon-152x152.png",
            "sizes": "152x152",
            "type": "image/png",
            "purpose": "maskable any"
        },
        {
            "src": "/static/icons/icon-192x192.png",
            "sizes": "192x192",
            "type": "image/png",
            "purpose": "maskable any"
        },
        {
            "src": "/static/icons/icon-384x384.png",
            "sizes": "384x384",
            "type": "image/png",
            "purpose": "maskable any"
        },
        {
            "src": "/static/icons/icon-512x512.png",
            "sizes": "512x512",
            "type": "image/png",
            "purpose": "maskable any"
        }
    ],
    "shortcuts": [
        {
            "name": "Search Stocks",
            "short_name": "Search",
            "description": "Search and analyze stocks with AI",
            "url": "/?shortcut=search",
            "icons": [{"src": "/static/icons/search-icon.png", "sizes": "96x96"}]
        },
        {
            "name": "Portfolio",
            "short_name": "Portfolio",
            "description": "View your trading portfolio",
            "url": "/portfolio?shortcut=portfolio",
            "icons": [{"src": "/static/icons/portfolio-icon.png", "sizes": "96x96"}]
        },
        {
            "name": "Watchlist",
            "short_name": "Watchlist",
            "description": "Check your stock watchlist",
            "url": "/?shortcut=watchlist",
            "icons": [{"src": "/static/icons/watchlist-icon.png", "sizes": "96x96"}]
        }
    ],
    "screenshots": [
        {
            "src": "/static/screenshots/desktop-screenshot.png",
            "sizes": "1280x720",
            "type": "image/png",
            "form_factor": "wide",
            "label": "TradeWise AI Desktop Interface"
        },
        {
            "src": "/static/screenshots/mobile-screenshot.png",
            "sizes": "750x1334",
            "type": "image/png",
            "form_factor": "narrow",
            "label": "TradeWise AI Mobile Interface"
        }
    ]
}

@pwa_bp.route('/manifest.json')
def manifest():
    """Serve PWA manifest file"""
    return jsonify(PWA_MANIFEST)

@pwa_bp.route('/sw.js')
def service_worker():
    """Serve service worker for offline functionality"""
    return send_from_directory('static/js', 'sw.js', mimetype='application/javascript')

@pwa_bp.route('/offline')
def offline():
    """Offline page when no internet connection"""
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>TradeWise AI - Offline</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: white;
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                margin: 0;
                padding: 20px;
                text-align: center;
            }
            .offline-container {
                max-width: 400px;
            }
            .logo {
                font-size: 2.5rem;
                font-weight: 900;
                background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 1rem;
            }
            .offline-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
                opacity: 0.7;
            }
            .offline-message {
                font-size: 1.2rem;
                margin-bottom: 1rem;
                opacity: 0.9;
            }
            .offline-description {
                opacity: 0.7;
                line-height: 1.5;
                margin-bottom: 2rem;
            }
            .retry-btn {
                background: linear-gradient(135deg, #8b5cf6 0%, #06b6d4 100%);
                border: none;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 1rem;
                cursor: pointer;
                transition: transform 0.2s ease;
            }
            .retry-btn:hover {
                transform: scale(1.05);
            }
        </style>
    </head>
    <body>
        <div class="offline-container">
            <div class="logo">TradeWise AI</div>
            <div class="offline-icon">📶</div>
            <div class="offline-message">You're offline</div>
            <div class="offline-description">
                No internet connection detected. You can still view your watchlist and portfolio data from your last session.
            </div>
            <button class="retry-btn" onclick="window.location.reload()">
                Try Again
            </button>
        </div>
    </body>
    </html>
    ''')

def install_pwa_features(app):
    """Install PWA features into Flask app"""
    app.register_blueprint(pwa_bp)
    
    @app.after_request
    def add_pwa_headers(response):
        """Add PWA-friendly headers"""
        # Add PWA headers
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # Add cache headers for PWA resources
        if request.endpoint in ['pwa.manifest', 'pwa.service_worker']:
            response.headers['Cache-Control'] = 'no-cache'
        
        return response
    
    return app