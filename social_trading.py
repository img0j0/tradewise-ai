# Social Trading & Community Features for TradeWise AI
from flask import Blueprint, jsonify, request
import json
import time
from datetime import datetime, timedelta

social_bp = Blueprint('social', __name__)

# Community data storage (use database in production)
SOCIAL_DATA = {
    'traders': {},
    'copy_trades': {},
    'leaderboard': [],
    'discussions': [],
    'insights': [],
    'performance_rankings': {}
}

@social_bp.route('/api/social/leaderboard')
def get_trading_leaderboard():
    """Get top performing traders for copy trading"""
    
    # Mock leaderboard data (in production, calculate from real trading data)
    leaderboard = [
        {
            'trader_id': 'alex_trader',
            'display_name': 'Alex T.',
            'avatar': '👨‍💼',
            'rank': 1,
            'total_return': 34.7,
            'monthly_return': 8.2,
            'win_rate': 73.5,
            'followers': 1247,
            'trades_count': 156,
            'ai_synergy_score': 94,
            'risk_level': 'moderate',
            'specialties': ['Tech Stocks', 'AI Trends'],
            'verified': True,
            'copy_fee': 2.5
        },
        {
            'trader_id': 'sarah_quant',
            'display_name': 'Sarah Q.',
            'avatar': '👩‍💻',
            'rank': 2,
            'total_return': 28.9,
            'monthly_return': 6.8,
            'win_rate': 68.2,
            'followers': 892,
            'trades_count': 203,
            'ai_synergy_score': 91,
            'risk_level': 'conservative',
            'specialties': ['Value Investing', 'Dividends'],
            'verified': True,
            'copy_fee': 2.0
        },
        {
            'trader_id': 'mike_growth',
            'display_name': 'Mike G.',
            'avatar': '🚀',
            'rank': 3,
            'total_return': 42.1,
            'monthly_return': 12.3,
            'win_rate': 61.8,
            'followers': 1456,
            'trades_count': 89,
            'ai_synergy_score': 87,
            'risk_level': 'aggressive',
            'specialties': ['Growth Stocks', 'Momentum'],
            'verified': True,
            'copy_fee': 3.0
        },
        {
            'trader_id': 'emma_ai',
            'display_name': 'Emma AI',
            'avatar': '🤖',
            'rank': 4,
            'total_return': 31.5,
            'monthly_return': 7.1,
            'win_rate': 71.2,
            'followers': 2103,
            'trades_count': 278,
            'ai_synergy_score': 98,
            'risk_level': 'moderate',
            'specialties': ['AI-Driven', 'Data Analysis'],
            'verified': True,
            'copy_fee': 1.5
        },
        {
            'trader_id': 'david_value',
            'display_name': 'David V.',
            'avatar': '💎',
            'rank': 5,
            'total_return': 19.8,
            'monthly_return': 4.2,
            'win_rate': 78.9,
            'followers': 567,
            'trades_count': 45,
            'ai_synergy_score': 83,
            'risk_level': 'conservative',
            'specialties': ['Value Picks', 'Long-term'],
            'verified': False,
            'copy_fee': 1.0
        }
    ]
    
    return jsonify({
        'success': True,
        'leaderboard': leaderboard,
        'total_traders': len(leaderboard),
        'last_updated': datetime.now().isoformat()
    })

@social_bp.route('/api/social/copy-trader', methods=['POST'])
def start_copy_trading():
    """Start copying a successful trader"""
    data = request.json
    user_id = data.get('user_id', 'demo_user')
    trader_id = data.get('trader_id')
    copy_amount = data.get('copy_amount', 1000)
    copy_percentage = data.get('copy_percentage', 100)
    
    copy_trade_id = f"copy_{int(time.time())}_{trader_id}"
    
    copy_config = {
        'id': copy_trade_id,
        'user_id': user_id,
        'trader_id': trader_id,
        'start_date': datetime.now().isoformat(),
        'copy_amount': copy_amount,
        'copy_percentage': copy_percentage,
        'status': 'active',
        'trades_copied': 0,
        'total_return': 0.0,
        'monthly_return': 0.0
    }
    
    SOCIAL_DATA['copy_trades'][copy_trade_id] = copy_config
    
    return jsonify({
        'success': True,
        'copy_trade_id': copy_trade_id,
        'message': f'Started copying {trader_id}',
        'config': copy_config
    })

@social_bp.route('/api/social/stop-copy-trading', methods=['POST'])
def stop_copy_trading():
    """Stop copying a trader"""
    data = request.json
    copy_trade_id = data.get('copy_trade_id')
    
    if copy_trade_id in SOCIAL_DATA['copy_trades']:
        SOCIAL_DATA['copy_trades'][copy_trade_id]['status'] = 'stopped'
        SOCIAL_DATA['copy_trades'][copy_trade_id]['end_date'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Copy trading stopped'
        })
    
    return jsonify({'error': 'Copy trade not found'}), 404

@social_bp.route('/api/social/community-insights')
def get_community_insights():
    """Get community-shared insights and analysis"""
    
    insights = [
        {
            'id': 'insight_001',
            'author': 'Alex T.',
            'avatar': '👨‍💼',
            'timestamp': '2025-07-21T10:30:00Z',
            'symbol': 'NVDA',
            'insight_type': 'technical_analysis',
            'title': 'NVDA Breakout Pattern Confirmed',
            'content': 'Strong volume breakout above $480 resistance. AI models showing 78% confidence for continued upward momentum.',
            'ai_confidence': 78,
            'likes': 342,
            'comments': 45,
            'tags': ['breakout', 'ai_stocks', 'technical'],
            'performance_prediction': '+15% in 30 days',
            'risk_assessment': 'Moderate'
        },
        {
            'id': 'insight_002',
            'author': 'Sarah Q.',
            'avatar': '👩‍💻',
            'timestamp': '2025-07-21T09:15:00Z',
            'symbol': 'AAPL',
            'insight_type': 'fundamental_analysis',
            'title': 'Apple Services Growth Undervalued',
            'content': 'Q3 services revenue growth of 14% YoY suggests current P/E of 28x is conservative. AI integration could drive multiple expansion.',
            'ai_confidence': 82,
            'likes': 198,
            'comments': 23,
            'tags': ['fundamentals', 'services', 'value'],
            'performance_prediction': '+8% in 90 days',
            'risk_assessment': 'Low'
        },
        {
            'id': 'insight_003',
            'author': 'Mike G.',
            'avatar': '🚀',
            'timestamp': '2025-07-21T08:45:00Z',
            'symbol': 'TSLA',
            'insight_type': 'momentum_play',
            'title': 'Tesla Momentum Building',
            'content': 'Cybertruck delivery acceleration + FSD improvements creating positive sentiment shift. Options flow heavily bullish.',
            'ai_confidence': 71,
            'likes': 267,
            'comments': 67,
            'tags': ['momentum', 'ev', 'options'],
            'performance_prediction': '+25% in 60 days',
            'risk_assessment': 'High'
        }
    ]
    
    return jsonify({
        'success': True,
        'insights': insights,
        'total_insights': len(insights),
        'trending_tags': ['ai_stocks', 'breakout', 'earnings', 'momentum'],
        'top_contributors': ['Alex T.', 'Sarah Q.', 'Mike G.']
    })

@social_bp.route('/api/social/share-insight', methods=['POST'])
def share_insight():
    """Share trading insight with community"""
    data = request.json
    
    insight = {
        'id': f"insight_{int(time.time())}",
        'author': data.get('author', 'Anonymous'),
        'avatar': data.get('avatar', '👤'),
        'timestamp': datetime.now().isoformat(),
        'symbol': data.get('symbol'),
        'insight_type': data.get('insight_type', 'general'),
        'title': data.get('title'),
        'content': data.get('content'),
        'ai_confidence': data.get('ai_confidence', 0),
        'likes': 0,
        'comments': 0,
        'tags': data.get('tags', []),
        'performance_prediction': data.get('performance_prediction'),
        'risk_assessment': data.get('risk_assessment', 'Unknown')
    }
    
    SOCIAL_DATA['insights'].append(insight)
    
    return jsonify({
        'success': True,
        'insight_id': insight['id'],
        'message': 'Insight shared with community'
    })

@social_bp.route('/api/social/discussions/<symbol>')
def get_stock_discussions(symbol):
    """Get community discussions for a specific stock"""
    
    # Mock discussions data
    discussions = [
        {
            'id': 'disc_001',
            'symbol': symbol.upper(),
            'title': f'Bullish on {symbol.upper()} - Here\'s why',
            'author': 'TechInvestor92',
            'timestamp': '2025-07-21T11:20:00Z',
            'replies': 15,
            'sentiment': 'bullish',
            'preview': 'The recent AI developments and strong earnings guidance make this a solid long-term play...',
            'likes': 28,
            'ai_relevance_score': 87
        },
        {
            'id': 'disc_002',
            'symbol': symbol.upper(),
            'title': f'{symbol.upper()} Technical Analysis - Resistance levels',
            'author': 'ChartMaster',
            'timestamp': '2025-07-21T10:45:00Z',
            'replies': 8,
            'sentiment': 'neutral',
            'preview': 'Looking at the daily chart, we have strong resistance at $X and support at $Y...',
            'likes': 19,
            'ai_relevance_score': 92
        },
        {
            'id': 'disc_003',
            'symbol': symbol.upper(),
            'title': f'Concerns about {symbol.upper()} valuation',
            'author': 'ValueSeeker',
            'timestamp': '2025-07-21T09:30:00Z',
            'replies': 22,
            'sentiment': 'bearish',
            'preview': 'Current P/E ratio seems stretched given the growth prospects...',
            'likes': 12,
            'ai_relevance_score': 78
        }
    ]
    
    return jsonify({
        'success': True,
        'symbol': symbol.upper(),
        'discussions': discussions,
        'total_discussions': len(discussions),
        'sentiment_breakdown': {
            'bullish': 40,
            'neutral': 35,
            'bearish': 25
        }
    })

@social_bp.route('/api/social/trader-profile/<trader_id>')
def get_trader_profile(trader_id):
    """Get detailed trader profile for copy trading"""
    
    # Mock trader profile
    profile = {
        'trader_id': trader_id,
        'display_name': 'Alex T.',
        'avatar': '👨‍💼',
        'verified': True,
        'member_since': '2024-03-15',
        'followers': 1247,
        'following': 89,
        'total_return': 34.7,
        'monthly_return': 8.2,
        'yearly_return': 34.7,
        'win_rate': 73.5,
        'max_drawdown': -8.2,
        'sharpe_ratio': 1.45,
        'trades_count': 156,
        'ai_synergy_score': 94,
        'risk_level': 'moderate',
        'copy_fee': 2.5,
        'min_copy_amount': 500,
        'specialties': ['Tech Stocks', 'AI Trends', 'Growth Investing'],
        'trading_style': 'AI-Enhanced Technical Analysis',
        'avg_hold_time': '12 days',
        'favorite_sectors': ['Technology', 'Healthcare', 'Clean Energy'],
        'recent_trades': [
            {
                'symbol': 'NVDA',
                'action': 'BUY',
                'date': '2025-07-20',
                'price': 485.20,
                'return': '+12.3%',
                'status': 'open'
            },
            {
                'symbol': 'MSFT',
                'action': 'SELL',
                'date': '2025-07-18',
                'price': 445.80,
                'return': '+8.7%',
                'status': 'closed'
            },
            {
                'symbol': 'AAPL',
                'action': 'BUY',
                'date': '2025-07-15',
                'price': 192.30,
                'return': '+3.2%',
                'status': 'open'
            }
        ],
        'monthly_performance': [
            {'month': 'Jan 2025', 'return': 12.3},
            {'month': 'Feb 2025', 'return': 8.7},
            {'month': 'Mar 2025', 'return': -2.1},
            {'month': 'Apr 2025', 'return': 15.4},
            {'month': 'May 2025', 'return': 6.8},
            {'month': 'Jun 2025', 'return': 9.2},
            {'month': 'Jul 2025', 'return': 8.2}
        ],
        'bio': 'Quantitative analyst with 8+ years experience. Focus on AI-driven stock selection and technical analysis. Conservative risk management with consistent returns.',
        'strategy_description': 'Combines AI predictions with technical analysis for 60-70% accuracy. Typical hold period 1-3 weeks with 2% stop losses.',
        'transparency_score': 98
    }
    
    return jsonify({
        'success': True,
        'profile': profile
    })

@social_bp.route('/api/social/copy-trading-stats/<user_id>')
def get_copy_trading_stats(user_id):
    """Get user's copy trading performance"""
    
    # Mock copy trading stats
    stats = {
        'active_copies': 2,
        'total_copied_trades': 45,
        'total_investment': 2500,
        'total_return': 18.7,
        'monthly_return': 6.2,
        'best_copy': {
            'trader': 'Alex T.',
            'return': 23.4,
            'duration': '3 months'
        },
        'worst_copy': {
            'trader': 'Mike G.',
            'return': -5.2,
            'duration': '1 month'
        },
        'current_copies': [
            {
                'trader_id': 'alex_trader',
                'trader_name': 'Alex T.',
                'copy_amount': 1500,
                'start_date': '2025-05-15',
                'return': 23.4,
                'trades_copied': 28,
                'status': 'active'
            },
            {
                'trader_id': 'sarah_quant',
                'trader_name': 'Sarah Q.',
                'copy_amount': 1000,
                'start_date': '2025-06-20',
                'return': 12.8,
                'trades_copied': 17,
                'status': 'active'
            }
        ]
    }
    
    return jsonify({
        'success': True,
        'stats': stats
    })

@social_bp.route('/api/social/trending-stocks')
def get_trending_stocks():
    """Get stocks trending in the community"""
    
    trending = [
        {
            'symbol': 'NVDA',
            'mentions': 1247,
            'sentiment_score': 0.78,
            'trend_direction': 'up',
            'top_insight': 'AI chip demand exceeding expectations',
            'community_rating': 4.6
        },
        {
            'symbol': 'TSLA',
            'mentions': 892,
            'sentiment_score': 0.65,
            'trend_direction': 'up',
            'top_insight': 'Cybertruck production ramping faster than expected',
            'community_rating': 4.2
        },
        {
            'symbol': 'AAPL',
            'mentions': 756,
            'sentiment_score': 0.58,
            'trend_direction': 'neutral',
            'top_insight': 'iPhone 16 sales meeting expectations',
            'community_rating': 4.1
        },
        {
            'symbol': 'MSFT',
            'mentions': 634,
            'sentiment_score': 0.72,
            'trend_direction': 'up',
            'top_insight': 'Azure AI services driving growth',
            'community_rating': 4.4
        },
        {
            'symbol': 'AMZN',
            'mentions': 523,
            'sentiment_score': 0.45,
            'trend_direction': 'down',
            'top_insight': 'Cloud competition intensifying',
            'community_rating': 3.8
        }
    ]
    
    return jsonify({
        'success': True,
        'trending_stocks': trending,
        'last_updated': datetime.now().isoformat()
    })

def get_social_trading_javascript():
    """Return JavaScript for social trading functionality"""
    return '''
    class SocialTrading {
        constructor() {
            this.userId = 'demo_user';
        }

        async loadLeaderboard() {
            try {
                const response = await fetch('/api/social/leaderboard');
                const data = await response.json();
                
                if (data.success) {
                    this.displayLeaderboard(data.leaderboard);
                }
            } catch (error) {
                console.error('Error loading leaderboard:', error);
            }
        }

        displayLeaderboard(traders) {
            const container = document.getElementById('leaderboard-container');
            if (!container) return;

            container.innerHTML = traders.map(trader => `
                <div class="trader-card" data-trader-id="${trader.trader_id}">
                    <div class="trader-header">
                        <span class="trader-avatar">${trader.avatar}</span>
                        <div class="trader-info">
                            <h4>${trader.display_name} ${trader.verified ? '✓' : ''}</h4>
                            <p>Rank #${trader.rank} • ${trader.followers} followers</p>
                        </div>
                        <div class="trader-returns">
                            <span class="total-return">+${trader.total_return}%</span>
                            <span class="monthly-return">${trader.monthly_return}% this month</span>
                        </div>
                    </div>
                    <div class="trader-stats">
                        <div class="stat">
                            <label>Win Rate</label>
                            <span>${trader.win_rate}%</span>
                        </div>
                        <div class="stat">
                            <label>AI Synergy</label>
                            <span>${trader.ai_synergy_score}</span>
                        </div>
                        <div class="stat">
                            <label>Risk Level</label>
                            <span>${trader.risk_level}</span>
                        </div>
                    </div>
                    <div class="trader-specialties">
                        ${trader.specialties.map(s => `<span class="specialty-tag">${s}</span>`).join('')}
                    </div>
                    <div class="trader-actions">
                        <button class="btn-copy" onclick="socialTrading.showCopyModal('${trader.trader_id}')">
                            Copy Trader
                        </button>
                        <button class="btn-profile" onclick="socialTrading.showTraderProfile('${trader.trader_id}')">
                            View Profile
                        </button>
                    </div>
                </div>
            `).join('');
        }

        async showCopyModal(traderId) {
            // Show copy trading modal
            const modal = document.createElement('div');
            modal.className = 'copy-modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <h3>Copy Trader</h3>
                    <div class="copy-settings">
                        <label>Copy Amount ($)</label>
                        <input type="number" id="copy-amount" value="1000" min="100">
                        
                        <label>Copy Percentage (%)</label>
                        <input type="range" id="copy-percentage" value="100" min="10" max="100">
                        <span id="percentage-display">100%</span>
                    </div>
                    <div class="modal-actions">
                        <button onclick="socialTrading.startCopyTrading('${traderId}')">Start Copying</button>
                        <button onclick="this.closest('.copy-modal').remove()">Cancel</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
        }

        async startCopyTrading(traderId) {
            const amount = document.getElementById('copy-amount').value;
            const percentage = document.getElementById('copy-percentage').value;
            
            try {
                const response = await fetch('/api/social/copy-trader', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: this.userId,
                        trader_id: traderId,
                        copy_amount: parseInt(amount),
                        copy_percentage: parseInt(percentage)
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.showNotification('Copy trading started successfully!', 'success');
                    document.querySelector('.copy-modal').remove();
                }
            } catch (error) {
                console.error('Error starting copy trading:', error);
                this.showNotification('Error starting copy trading', 'error');
            }
        }

        async loadCommunityInsights() {
            try {
                const response = await fetch('/api/social/community-insights');
                const data = await response.json();
                
                if (data.success) {
                    this.displayCommunityInsights(data.insights);
                }
            } catch (error) {
                console.error('Error loading insights:', error);
            }
        }

        displayCommunityInsights(insights) {
            const container = document.getElementById('insights-container');
            if (!container) return;

            container.innerHTML = insights.map(insight => `
                <div class="insight-card">
                    <div class="insight-header">
                        <span class="author-avatar">${insight.avatar}</span>
                        <div class="insight-meta">
                            <span class="author">${insight.author}</span>
                            <span class="timestamp">${new Date(insight.timestamp).toLocaleString()}</span>
                        </div>
                        <span class="confidence-badge">${insight.ai_confidence}% AI</span>
                    </div>
                    <h4>${insight.title}</h4>
                    <p>${insight.content}</p>
                    <div class="insight-tags">
                        ${insight.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                    </div>
                    <div class="insight-stats">
                        <span>❤️ ${insight.likes}</span>
                        <span>💬 ${insight.comments}</span>
                        <span>📈 ${insight.performance_prediction}</span>
                    </div>
                </div>
            `).join('');
        }

        showNotification(message, type) {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => notification.remove(), 3000);
        }
    }

    // Initialize social trading
    const socialTrading = new SocialTrading();
    '''

class SocialTradingEngine:
    """Social Trading Engine for community features"""
    
    def __init__(self):
        self.leaderboard_cache = None
        self.insights_cache = None
        self.cache_timeout = 300  # 5 minutes
        
    def get_leaderboard(self):
        """Get cached leaderboard data"""
        # Implementation would go here for production
        return []
    
    def get_community_insights(self):
        """Get cached community insights"""
        # Implementation would go here for production
        return []
    
    def calculate_trader_score(self, trader_data):
        """Calculate comprehensive trader score"""
        # Implementation would go here for production
        return 0.0

def install_social_trading(app):
    """Install social trading features into Flask app"""
    app.register_blueprint(social_bp)
    return app