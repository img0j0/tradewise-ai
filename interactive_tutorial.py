# Interactive Tutorial System for TradeWise AI
from flask import Blueprint, jsonify, request, render_template_string
import json
import os

tutorial_bp = Blueprint('tutorial', __name__)

# Tutorial Steps Configuration
TUTORIAL_STEPS = [
    {
        "id": "welcome",
        "title": "Welcome to TradeWise AI!",
        "description": "Let's take a quick tour of your new AI-powered trading platform",
        "target": "body",
        "content": "TradeWise AI uses artificial intelligence to help you make smarter investment decisions. Ready to get started?",
        "position": "center",
        "buttons": [{"text": "Let's Begin!", "action": "next"}],
        "duration": 0
    },
    {
        "id": "search_introduction",
        "title": "Smart Stock Search",
        "description": "This is where the magic happens - search any stock and get AI-powered analysis",
        "target": ".search-input",
        "content": "Type any stock symbol (like AAPL, TSLA, or NVDA) and our AI will provide instant analysis with buy/sell recommendations.",
        "position": "bottom",
        "buttons": [{"text": "Try it now", "action": "demo"}, {"text": "Next", "action": "next"}],
        "demo_action": "search_demo",
        "duration": 8000
    },
    {
        "id": "ai_analysis",
        "title": "AI-Powered Analysis", 
        "description": "Our AI analyzes real market data to give you confidence scores and recommendations",
        "target": ".stock-analysis-overlay",
        "content": "Each analysis includes risk assessment, confidence scores, and clear buy/hold/sell recommendations based on current market conditions.",
        "position": "left",
        "buttons": [{"text": "Got it!", "action": "next"}],
        "duration": 6000
    },
    {
        "id": "tools_dropdown",
        "title": "Your Trading Tools",
        "description": "Access all your trading tools from this convenient dropdown menu",
        "target": ".tools-dropdown",
        "content": "Here you'll find your portfolio, watchlist, alerts, market news, and account settings.",
        "position": "bottom-left",
        "buttons": [{"text": "Show me", "action": "demo"}, {"text": "Next", "action": "next"}],
        "demo_action": "tools_demo",
        "duration": 5000
    },
    {
        "id": "watchlist_feature",
        "title": "Build Your Watchlist",
        "description": "Save stocks you're interested in to track them easily",
        "target": ".watch-btn",
        "content": "Click the star button on any stock analysis to add it to your watchlist for easy monitoring.",
        "position": "top",
        "buttons": [{"text": "Try it", "action": "demo"}, {"text": "Next", "action": "next"}],
        "demo_action": "watchlist_demo",
        "duration": 4000
    },
    {
        "id": "alerts_system",
        "title": "Smart Price Alerts",
        "description": "Get notified when stocks hit your target prices or show unusual activity",
        "target": ".alert-btn",
        "content": "Our AI can suggest smart alerts based on technical analysis and market conditions.",
        "position": "top",
        "buttons": [{"text": "Set an alert", "action": "demo"}, {"text": "Next", "action": "next"}],
        "demo_action": "alert_demo",
        "duration": 5000
    },
    {
        "id": "buying_stocks",
        "title": "Paper Trading",
        "description": "Practice trading with virtual money before risking real capital",
        "target": ".buy-btn",
        "content": "Start with paper trading to test strategies and learn how our AI recommendations perform.",
        "position": "top",
        "buttons": [{"text": "Try buying", "action": "demo"}, {"text": "Next", "action": "next"}],
        "demo_action": "buy_demo", 
        "duration": 6000
    },
    {
        "id": "portfolio_tracking",
        "title": "Track Your Performance",
        "description": "Monitor your portfolio performance with real-time updates",
        "target": ".portfolio-link",
        "content": "Your portfolio shows current holdings, profit/loss, and performance metrics updated in real-time.",
        "position": "bottom",
        "buttons": [{"text": "View portfolio", "action": "demo"}, {"text": "Next", "action": "next"}],
        "demo_action": "portfolio_demo",
        "duration": 4000
    },
    {
        "id": "ai_confidence",
        "title": "Understanding AI Confidence",
        "description": "Learn how to interpret AI confidence scores for better decision making",
        "target": ".confidence-score",
        "content": "Higher confidence scores (80%+) indicate stronger AI conviction. Use these scores to size your positions appropriately.",
        "position": "right",
        "buttons": [{"text": "Got it!", "action": "next"}],
        "duration": 6000
    },
    {
        "id": "completion",
        "title": "You're All Set!",
        "description": "You now know the basics of TradeWise AI",
        "target": "body",
        "content": "You're ready to start making smarter investment decisions with AI. Remember: start with paper trading, build a watchlist, and pay attention to confidence scores!",
        "position": "center",
        "buttons": [{"text": "Start Trading!", "action": "complete"}],
        "duration": 0
    }
]

# Tutorial Progress Tracking
USER_TUTORIAL_PROGRESS = {}

@tutorial_bp.route('/api/tutorial/start')
def start_tutorial():
    """Start the interactive tutorial"""
    user_id = request.args.get('user_id', 'demo_user')
    
    # Reset progress
    USER_TUTORIAL_PROGRESS[user_id] = {
        'current_step': 0,
        'completed_steps': [],
        'started_at': None,
        'completed_at': None
    }
    
    return jsonify({
        'success': True,
        'tutorial_steps': TUTORIAL_STEPS,
        'current_step': TUTORIAL_STEPS[0],
        'total_steps': len(TUTORIAL_STEPS)
    })

@tutorial_bp.route('/api/tutorial/next', methods=['POST'])
def next_tutorial_step():
    """Move to next tutorial step"""
    user_id = request.json.get('user_id', 'demo_user')
    current_step_id = request.json.get('current_step_id')
    
    if user_id not in USER_TUTORIAL_PROGRESS:
        return jsonify({'error': 'Tutorial not started'}), 400
    
    progress = USER_TUTORIAL_PROGRESS[user_id]
    
    # Mark current step as completed
    if current_step_id and current_step_id not in progress['completed_steps']:
        progress['completed_steps'].append(current_step_id)
    
    # Move to next step
    progress['current_step'] += 1
    
    if progress['current_step'] >= len(TUTORIAL_STEPS):
        # Tutorial completed
        progress['completed_at'] = True
        return jsonify({
            'success': True,
            'completed': True,
            'message': 'Tutorial completed successfully!',
            'completed_steps': len(progress['completed_steps']),
            'total_steps': len(TUTORIAL_STEPS)
        })
    
    next_step = TUTORIAL_STEPS[progress['current_step']]
    
    return jsonify({
        'success': True,
        'current_step': next_step,
        'step_number': progress['current_step'] + 1,
        'total_steps': len(TUTORIAL_STEPS),
        'progress_percentage': round((progress['current_step'] / len(TUTORIAL_STEPS)) * 100)
    })

@tutorial_bp.route('/api/tutorial/skip')
def skip_tutorial():
    """Skip the tutorial"""
    user_id = request.args.get('user_id', 'demo_user')
    
    USER_TUTORIAL_PROGRESS[user_id] = {
        'current_step': len(TUTORIAL_STEPS),
        'completed_steps': [],
        'started_at': None,
        'completed_at': True,
        'skipped': True
    }
    
    return jsonify({
        'success': True,
        'skipped': True,
        'message': 'Tutorial skipped'
    })

@tutorial_bp.route('/api/tutorial/demo/<action>')
def tutorial_demo_action(action):
    """Handle tutorial demo actions"""
    
    demo_responses = {
        'search_demo': {
            'action': 'search_demo',
            'symbol': 'AAPL',
            'data': {
                'symbol': 'AAPL',
                'company_name': 'Apple Inc.',
                'current_price': 189.25,
                'change': '+2.15',
                'change_percent': '+1.15%',
                'ai_recommendation': 'BUY',
                'confidence_score': 87,
                'risk_level': 'Moderate',
                'key_points': [
                    'Strong earnings growth expected',
                    'Positive technical indicators', 
                    'Market leadership in technology sector'
                ]
            }
        },
        'tools_demo': {
            'action': 'tools_demo',
            'message': 'Opening tools dropdown to show available features'
        },
        'watchlist_demo': {
            'action': 'watchlist_demo',
            'message': 'Adding AAPL to your watchlist',
            'symbol': 'AAPL'
        },
        'alert_demo': {
            'action': 'alert_demo',
            'message': 'Creating a smart price alert for AAPL',
            'alert': {
                'symbol': 'AAPL',
                'type': 'price_target',
                'target_price': 195.00,
                'current_price': 189.25
            }
        },
        'buy_demo': {
            'action': 'buy_demo',
            'message': 'Opening buy modal for paper trading',
            'symbol': 'AAPL',
            'quantity': 10,
            'total_cost': 1892.50
        },
        'portfolio_demo': {
            'action': 'portfolio_demo',
            'message': 'Showing your portfolio performance',
            'portfolio_value': 50000,
            'day_change': '+2.3%'
        }
    }
    
    return jsonify(demo_responses.get(action, {'error': 'Demo action not found'}))

@tutorial_bp.route('/api/tutorial/progress')
def get_tutorial_progress():
    """Get current tutorial progress"""
    user_id = request.args.get('user_id', 'demo_user')
    
    if user_id not in USER_TUTORIAL_PROGRESS:
        return jsonify({
            'tutorial_completed': False,
            'progress': 0,
            'current_step': None
        })
    
    progress = USER_TUTORIAL_PROGRESS[user_id]
    
    return jsonify({
        'tutorial_completed': progress.get('completed_at', False),
        'progress': round((len(progress['completed_steps']) / len(TUTORIAL_STEPS)) * 100),
        'current_step': progress.get('current_step', 0),
        'completed_steps': progress['completed_steps'],
        'total_steps': len(TUTORIAL_STEPS)
    })

def get_tutorial_javascript():
    """Return JavaScript code for tutorial functionality"""
    return '''
    class InteractiveTutorial {
        constructor() {
            this.currentStep = null;
            this.tutorialOverlay = null;
            this.userId = 'demo_user';
            this.isRunning = false;
        }

        async startTutorial() {
            if (this.isRunning) return;
            
            try {
                const response = await fetch(`/api/tutorial/start?user_id=${this.userId}`);
                const data = await response.json();
                
                if (data.success) {
                    this.isRunning = true;
                    this.createTutorialOverlay();
                    this.showStep(data.current_step);
                }
            } catch (error) {
                console.error('Error starting tutorial:', error);
            }
        }

        createTutorialOverlay() {
            // Create overlay container
            this.tutorialOverlay = document.createElement('div');
            this.tutorialOverlay.className = 'tutorial-overlay';
            this.tutorialOverlay.innerHTML = `
                <div class="tutorial-backdrop"></div>
                <div class="tutorial-content">
                    <div class="tutorial-step-counter">
                        <span class="current-step">1</span> / <span class="total-steps">10</span>
                    </div>
                    <div class="tutorial-close" onclick="tutorial.skipTutorial()">×</div>
                    <div class="tutorial-highlight"></div>
                    <div class="tutorial-tooltip">
                        <h3 class="tutorial-title"></h3>
                        <p class="tutorial-description"></p>
                        <div class="tutorial-buttons"></div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(this.tutorialOverlay);
            this.addTutorialStyles();
        }

        addTutorialStyles() {
            if (document.getElementById('tutorial-styles')) return;
            
            const styles = document.createElement('style');
            styles.id = 'tutorial-styles';
            styles.textContent = `
                .tutorial-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 10000;
                    pointer-events: none;
                }
                
                .tutorial-backdrop {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.7);
                    pointer-events: auto;
                }
                
                .tutorial-content {
                    position: relative;
                    width: 100%;
                    height: 100%;
                    pointer-events: none;
                }
                
                .tutorial-step-counter {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: rgba(139, 92, 246, 0.9);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: 600;
                    pointer-events: auto;
                    backdrop-filter: blur(10px);
                }
                
                .tutorial-close {
                    position: fixed;
                    top: 20px;
                    right: 100px;
                    width: 30px;
                    height: 30px;
                    background: rgba(255, 255, 255, 0.2);
                    color: white;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    font-size: 18px;
                    font-weight: bold;
                    pointer-events: auto;
                    transition: background 0.2s ease;
                }
                
                .tutorial-close:hover {
                    background: rgba(255, 255, 255, 0.3);
                }
                
                .tutorial-highlight {
                    position: absolute;
                    border: 3px solid #8b5cf6;
                    border-radius: 8px;
                    box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.7);
                    pointer-events: none;
                    z-index: 9999;
                    transition: all 0.3s ease;
                }
                
                .tutorial-tooltip {
                    position: absolute;
                    background: white;
                    border-radius: 12px;
                    padding: 20px;
                    max-width: 300px;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
                    pointer-events: auto;
                    z-index: 10001;
                }
                
                .tutorial-title {
                    color: #1a1a2e;
                    font-size: 18px;
                    font-weight: 700;
                    margin: 0 0 8px 0;
                }
                
                .tutorial-description {
                    color: #4a5568;
                    font-size: 14px;
                    line-height: 1.5;
                    margin: 0 0 16px 0;
                }
                
                .tutorial-buttons {
                    display: flex;
                    gap: 8px;
                    justify-content: flex-end;
                }
                
                .tutorial-btn {
                    padding: 8px 16px;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }
                
                .tutorial-btn-primary {
                    background: #8b5cf6;
                    color: white;
                }
                
                .tutorial-btn-primary:hover {
                    background: #7c3aed;
                }
                
                .tutorial-btn-secondary {
                    background: #e2e8f0;
                    color: #4a5568;
                }
                
                .tutorial-btn-secondary:hover {
                    background: #cbd5e0;
                }
                
                @media (max-width: 768px) {
                    .tutorial-tooltip {
                        max-width: calc(100vw - 40px);
                        left: 20px !important;
                        right: 20px !important;
                    }
                    
                    .tutorial-step-counter {
                        top: 10px;
                        right: 10px;
                        font-size: 12px;
                        padding: 6px 12px;
                    }
                    
                    .tutorial-close {
                        top: 10px;
                        right: 80px;
                        width: 25px;
                        height: 25px;
                        font-size: 16px;
                    }
                }
            `;
            
            document.head.appendChild(styles);
        }

        showStep(step) {
            this.currentStep = step;
            
            // Update step counter
            const currentStepEl = this.tutorialOverlay.querySelector('.current-step');
            const totalStepsEl = this.tutorialOverlay.querySelector('.total-steps');
            
            if (currentStepEl) currentStepEl.textContent = step.id === 'welcome' ? '1' : '2';
            if (totalStepsEl) totalStepsEl.textContent = '10';
            
            // Update tooltip content
            const title = this.tutorialOverlay.querySelector('.tutorial-title');
            const description = this.tutorialOverlay.querySelector('.tutorial-description');
            const buttonsContainer = this.tutorialOverlay.querySelector('.tutorial-buttons');
            
            title.textContent = step.title;
            description.textContent = step.content;
            
            // Create buttons
            buttonsContainer.innerHTML = '';
            step.buttons.forEach(button => {
                const btn = document.createElement('button');
                btn.className = `tutorial-btn ${button.action === 'next' || button.action === 'complete' ? 'tutorial-btn-primary' : 'tutorial-btn-secondary'}`;
                btn.textContent = button.text;
                btn.onclick = () => this.handleButtonClick(button.action, step);
                buttonsContainer.appendChild(btn);
            });
            
            // Position tooltip and highlight
            this.positionTutorialElements(step);
            
            // Auto-advance if duration is set
            if (step.duration > 0) {
                setTimeout(() => {
                    this.nextStep();
                }, step.duration);
            }
        }

        positionTutorialElements(step) {
            const highlight = this.tutorialOverlay.querySelector('.tutorial-highlight');
            const tooltip = this.tutorialOverlay.querySelector('.tutorial-tooltip');
            
            if (step.target === 'body') {
                // Center tooltip for body target
                highlight.style.display = 'none';
                tooltip.style.position = 'fixed';
                tooltip.style.top = '50%';
                tooltip.style.left = '50%';
                tooltip.style.transform = 'translate(-50%, -50%)';
                return;
            }
            
            const targetElement = document.querySelector(step.target);
            if (!targetElement) {
                console.warn(`Tutorial target not found: ${step.target}`);
                return;
            }
            
            const rect = targetElement.getBoundingClientRect();
            
            // Position highlight
            highlight.style.display = 'block';
            highlight.style.left = (rect.left - 5) + 'px';
            highlight.style.top = (rect.top - 5) + 'px';
            highlight.style.width = (rect.width + 10) + 'px';
            highlight.style.height = (rect.height + 10) + 'px';
            
            // Position tooltip based on position preference
            let tooltipTop, tooltipLeft;
            
            switch (step.position) {
                case 'bottom':
                    tooltipTop = rect.bottom + 15;
                    tooltipLeft = rect.left + (rect.width / 2) - 150;
                    break;
                case 'top':
                    tooltipTop = rect.top - 15;
                    tooltipLeft = rect.left + (rect.width / 2) - 150;
                    tooltip.style.transform = 'translateY(-100%)';
                    break;
                case 'left':
                    tooltipTop = rect.top + (rect.height / 2) - 75;
                    tooltipLeft = rect.left - 315;
                    break;
                case 'right':
                    tooltipTop = rect.top + (rect.height / 2) - 75;
                    tooltipLeft = rect.right + 15;
                    break;
                case 'bottom-left':
                    tooltipTop = rect.bottom + 15;
                    tooltipLeft = rect.left;
                    break;
                default:
                    tooltipTop = rect.bottom + 15;
                    tooltipLeft = rect.left;
            }
            
            // Ensure tooltip stays within viewport
            const maxLeft = window.innerWidth - 320;
            const maxTop = window.innerHeight - 200;
            
            tooltipLeft = Math.max(20, Math.min(tooltipLeft, maxLeft));
            tooltipTop = Math.max(20, Math.min(tooltipTop, maxTop));
            
            tooltip.style.position = 'fixed';
            tooltip.style.top = tooltipTop + 'px';
            tooltip.style.left = tooltipLeft + 'px';
            tooltip.style.transform = 'none';
        }

        async handleButtonClick(action, step) {
            switch (action) {
                case 'next':
                    await this.nextStep();
                    break;
                case 'demo':
                    await this.playDemo(step.demo_action);
                    break;
                case 'complete':
                    this.completeTutorial();
                    break;
            }
        }

        async nextStep() {
            try {
                const response = await fetch('/api/tutorial/next', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: this.userId,
                        current_step_id: this.currentStep?.id
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    if (data.completed) {
                        this.completeTutorial();
                    } else {
                        this.showStep(data.current_step);
                    }
                }
            } catch (error) {
                console.error('Error advancing tutorial:', error);
            }
        }

        async playDemo(demoAction) {
            try {
                const response = await fetch(`/api/tutorial/demo/${demoAction}`);
                const data = await response.json();
                
                // Execute demo action based on type
                switch (demoAction) {
                    case 'search_demo':
                        this.simulateSearch(data.data);
                        break;
                    case 'tools_demo':
                        this.simulateToolsOpen();
                        break;
                    case 'watchlist_demo':
                        this.simulateWatchlistAdd();
                        break;
                    case 'alert_demo':
                        this.simulateAlertCreation();
                        break;
                    case 'buy_demo':
                        this.simulateBuyAction();
                        break;
                    case 'portfolio_demo':
                        this.simulatePortfolioView();
                        break;
                }
                
                // Auto-advance to next step after demo
                setTimeout(() => {
                    this.nextStep();
                }, 2000);
                
            } catch (error) {
                console.error('Error playing demo:', error);
            }
        }

        simulateSearch(data) {
            const searchInput = document.querySelector('.search-input input');
            if (searchInput) {
                searchInput.value = data.symbol;
                // Trigger search if function exists
                if (typeof searchStock === 'function') {
                    searchStock(data.symbol);
                }
            }
        }

        simulateToolsOpen() {
            const toolsDropdown = document.querySelector('.tools-dropdown');
            if (toolsDropdown && typeof toggleTools === 'function') {
                toggleTools();
            }
        }

        simulateWatchlistAdd() {
            // Show notification
            this.showTutorialNotification('AAPL added to your watchlist!', 'success');
        }

        simulateAlertCreation() {
            this.showTutorialNotification('Smart alert created for AAPL at $195.00', 'success');
        }

        simulateBuyAction() {
            // Show buy modal if function exists
            if (typeof showBuyModal === 'function') {
                showBuyModal('AAPL');
            }
        }

        simulatePortfolioView() {
            // Open portfolio if function exists
            if (typeof togglePortfolio === 'function') {
                togglePortfolio();
            }
        }

        showTutorialNotification(message, type) {
            const notification = document.createElement('div');
            notification.className = `tutorial-notification ${type}`;
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                background: ${type === 'success' ? '#10b981' : '#8b5cf6'};
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: 600;
                z-index: 10002;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                animation: slideInRight 0.3s ease;
            `;
            
            document.body.appendChild(notification);
            
            setTimeout(() => {
                notification.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }, 2000);
        }

        async skipTutorial() {
            try {
                await fetch(`/api/tutorial/skip?user_id=${this.userId}`);
                this.completeTutorial();
            } catch (error) {
                console.error('Error skipping tutorial:', error);
            }
        }

        completeTutorial() {
            this.isRunning = false;
            if (this.tutorialOverlay) {
                this.tutorialOverlay.remove();
                this.tutorialOverlay = null;
            }
            
            // Remove tutorial styles
            const styles = document.getElementById('tutorial-styles');
            if (styles) styles.remove();
            
            // Show completion message
            this.showTutorialNotification('Tutorial completed! Happy trading! 🎉', 'success');
        }
    }

    // Initialize tutorial
    const tutorial = new InteractiveTutorial();
    
    // Add tutorial start button or auto-start logic
    document.addEventListener('DOMContentLoaded', function() {
        // Check if user has completed tutorial
        fetch(`/api/tutorial/progress?user_id=demo_user`)
            .then(response => response.json())
            .then(data => {
                if (!data.tutorial_completed) {
                    // Show tutorial prompt
                    setTimeout(() => {
                        if (confirm('Welcome to TradeWise AI! Would you like to take a quick tutorial to learn how to use the platform?')) {
                            tutorial.startTutorial();
                        }
                    }, 2000);
                }
            })
            .catch(error => console.error('Error checking tutorial progress:', error));
    });
    '''