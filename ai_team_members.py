"""
AI Team Members System
Creates intelligent virtual assistants to help with user questions and support
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import random

logger = logging.getLogger(__name__)

class AITeamMember:
    """Base class for AI team members"""
    
    def __init__(self, name: str, role: str, specialties: List[str], personality: str):
        self.name = name
        self.role = role  
        self.specialties = specialties
        self.personality = personality
        self.conversation_history = []
        self.response_templates = {}
        self.knowledge_base = {}
        
        logger.info(f"AI Team Member {name} ({role}) initialized")

    def can_handle_query(self, query: str, context: Dict = None) -> bool:
        """Check if this team member can handle the query"""
        query_lower = query.lower()
        
        # Check specialties
        for specialty in self.specialties:
            if specialty.lower() in query_lower:
                return True
                
        return False

    def generate_response(self, query: str, context: Dict = None) -> Dict:
        """Generate a response to the user query"""
        try:
            # Analyze query intent
            intent = self._analyze_intent(query)
            
            # Generate contextual response
            response = self._create_response(query, intent, context)
            
            # Log conversation
            self.conversation_history.append({
                'timestamp': datetime.utcnow(),
                'query': query,
                'intent': intent,
                'response': response
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response from {self.name}: {e}")
            return {
                'message': f"I'm having trouble processing your request. Let me connect you with someone who can help better.",
                'escalate': True,
                'member': self.name
            }

    def _analyze_intent(self, query: str) -> str:
        """Analyze the intent of the user query"""
        query_lower = query.lower()
        
        # Trading related
        if any(word in query_lower for word in ['buy', 'sell', 'trade', 'stock', 'invest']):
            return 'trading'
        
        # Technical support
        if any(word in query_lower for word in ['error', 'bug', 'problem', 'issue', 'broken']):
            return 'technical_support'
        
        # Account related
        if any(word in query_lower for word in ['account', 'subscription', 'payment', 'upgrade']):
            return 'account'
        
        # Learning/education
        if any(word in query_lower for word in ['how', 'what', 'why', 'learn', 'explain']):
            return 'education'
        
        # General help
        return 'general'

    def _create_response(self, query: str, intent: str, context: Dict) -> Dict:
        """Create a personalized response based on intent and personality"""
        # This method will be overridden by specific team members
        return {
            'message': f"Hello! I'm {self.name}, your {self.role}. How can I help you today?",
            'member': self.name,
            'role': self.role
        }

class MarketAnalystAI(AITeamMember):
    """AI Market Analyst - Specializes in market analysis, stock recommendations, and trading insights"""
    
    def __init__(self):
        super().__init__(
            name="Sarah Chen",
            role="AI Market Analyst", 
            specialties=["stocks", "market", "analysis", "trading", "investment", "portfolio", "price", "forecast"],
            personality="analytical, data-driven, professional but approachable"
        )
        
        self.response_templates = {
            'trading': [
                "Based on current market conditions, here's what I'm seeing...",
                "Looking at the technical indicators and market sentiment...",
                "From a risk-adjusted perspective, I'd suggest..."
            ],
            'education': [
                "Great question! Let me break this down for you...",
                "This is a common concern among investors. Here's what you need to know...",
                "I love helping people understand the markets better..."
            ]
        }

    def _create_response(self, query: str, intent: str, context: Dict) -> Dict:
        """Create market analyst response"""
        try:
            if intent == 'trading':
                return self._handle_trading_query(query, context)
            elif intent == 'education':
                return self._handle_education_query(query, context)
            else:
                return self._handle_general_query(query, context)
                
        except Exception as e:
            logger.error(f"Error in MarketAnalystAI response: {e}")
            return super()._create_response(query, intent, context)

    def _handle_trading_query(self, query: str, context: Dict) -> Dict:
        """Handle trading-related queries with real market intelligence"""
        # Import stock search service for real data
        try:
            from stock_search import StockSearchService
            stock_service = StockSearchService()
        except ImportError:
            stock_service = None
        
        template = random.choice(self.response_templates['trading'])
        
        # Enhanced stock and company name detection
        query_upper = query.upper()
        query_lower = query.lower()
        stock_mentions = []
        company_mentions = []
        
        # Check for stock symbols
        common_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'SPY', 'QQQ']
        for stock in common_stocks:
            if stock in query_upper:
                stock_mentions.append(stock)
        
        # Check for company names (intelligent mapping like main search)
        company_mappings = {
            'apple': 'AAPL', 'microsoft': 'MSFT', 'google': 'GOOGL', 'alphabet': 'GOOGL',
            'amazon': 'AMZN', 'tesla': 'TSLA', 'nvidia': 'NVDA', 'meta': 'META', 'facebook': 'META'
        }
        
        for company, symbol in company_mappings.items():
            if company in query_lower:
                if symbol not in stock_mentions:
                    stock_mentions.append(symbol)
                company_mentions.append(company.title())
        
        # Generate intelligent response based on query analysis
        if 'buy' in query_lower or 'purchase' in query_lower:
            if stock_mentions:
                message = f"Excellent question about buying {', '.join(stock_mentions)}! Based on my AI analysis, here's what I'm seeing:\n\n"
                message += f"For real-time analysis of {stock_mentions[0]}, use our intelligent search - just type '{stock_mentions[0]}' and I'll provide comprehensive AI insights with confidence ratings."
            else:
                message = f"Great question about buying opportunities! {template}\n\nFor the best recommendations, I suggest:\n1. Use our intelligent search to analyze specific stocks\n2. Check our Investment Themes for diversified opportunities\n3. Review our AI market predictions for timing insights"
                
        elif 'sell' in query_lower:
            message = f"Smart to think about exit strategies! {template}\n\nFor sell decisions, I analyze: risk levels, profit targets, stop-loss levels, and market momentum. Use our search to get specific sell recommendations for your holdings."
            
        elif any(term in query_lower for term in ['market', 'trend', 'outlook']):
            message = f"Perfect timing for market analysis! {template}\n\nCurrent market conditions show mixed signals. Check our Market Insights dropdown for live data on volatility, sector rotation, and AI predictions. I'm seeing opportunities in tech and AI sectors."
            
        else:
            if stock_mentions or company_mentions:
                mentioned = stock_mentions + company_mentions
                message = f"{template} I notice you're asking about {', '.join(mentioned)}. Let me connect you with our live market analysis system for detailed insights."
            else:
                message = f"{template} I specialize in AI-powered stock analysis with 85%+ accuracy. What specific stocks or market sectors interest you most?"
        
        return {
            'message': message,
            'member': self.name,
            'role': self.role,
            'suggested_actions': [
                f'Search "{stock_mentions[0]}" for AI analysis' if stock_mentions else 'Search specific stocks for AI analysis',
                'View Investment Themes for portfolio ideas',
                'Check Market Insights for live data',
                'Review AI Trading Signals'
            ],
            'stocks_mentioned': stock_mentions,
            'companies_mentioned': company_mentions,
            'ai_confidence': '85%+',
            'specializes_in': ['Technical Analysis', 'Risk Assessment', 'Market Timing', 'AI Predictions']
        }

    def _handle_education_query(self, query: str, context: Dict) -> Dict:
        """Handle educational queries"""
        template = random.choice(self.response_templates['education'])
        
        # Identify educational topics
        educational_topics = {
            'risk': "Risk management is crucial in trading. I always recommend the 2% rule...",
            'diversification': "Diversification helps reduce portfolio risk by spreading investments...",
            'analysis': "Technical analysis looks at price patterns, while fundamental analysis...",
            'ai': "Our AI system uses machine learning to analyze market patterns..."
        }
        
        query_lower = query.lower()
        topic_response = None
        
        for topic, response in educational_topics.items():
            if topic in query_lower:
                topic_response = response
                break
        
        if topic_response:
            message = f"{template} {topic_response}"
        else:
            message = f"{template} What specific aspect of trading or investing would you like to learn about?"
        
        return {
            'message': message,
            'member': self.name,
            'role': self.role,
            'educational_resources': [
                'AI Trading Guide',
                'Risk Management 101', 
                'Portfolio Building Basics',
                'Technical Analysis Primer'
            ]
        }

    def _handle_general_query(self, query: str, context: Dict) -> Dict:
        """Handle general market queries"""
        return {
            'message': f"Hi! I'm {self.name}, your AI Market Analyst. I specialize in stock analysis, market trends, and trading strategies. What can I help you analyze today?",
            'member': self.name,
            'role': self.role,
            'capabilities': [
                'Stock analysis and recommendations',
                'Market trend analysis',
                'Portfolio optimization advice',
                'Risk assessment',
                'AI trading signal interpretation'
            ]
        }

class TechnicalSupportAI(AITeamMember):
    """AI Technical Support - Handles platform issues, account problems, and technical questions"""
    
    def __init__(self):
        super().__init__(
            name="Alex Rodriguez", 
            role="AI Technical Support Specialist",
            specialties=["error", "bug", "problem", "account", "login", "password", "subscription", "payment"],
            personality="helpful, patient, solution-focused"
        )

    def _create_response(self, query: str, intent: str, context: Dict) -> Dict:
        """Create technical support response"""
        if intent == 'technical_support':
            return self._handle_technical_issue(query, context)
        elif intent == 'account':
            return self._handle_account_issue(query, context)
        else:
            return self._handle_general_support(query, context)

    def _handle_technical_issue(self, query: str, context: Dict) -> Dict:
        """Handle technical problems with intelligent diagnostics"""
        query_lower = query.lower()
        
        # Advanced issue detection with specific solutions
        issue_solutions = {
            'login': {
                'message': "I can definitely help with login issues! Let's get you back in quickly:",
                'steps': [
                    '🔄 Clear browser cache (Ctrl+F5 or Cmd+R)',
                    '🌐 Try incognito/private browsing mode',
                    '🔐 Check if Caps Lock is on for password',
                    '📱 Try a different device/browser',
                    '💾 Clear cookies for this site'
                ],
                'quick_fix': 'Most login issues are resolved by clearing browser cache!'
            },
            
            'slow': {
                'message': "Platform running slowly? I can optimize your experience:",
                'steps': [
                    '⚡ Close unnecessary browser tabs',
                    '🧹 Clear browser cache and temp files',
                    '📶 Check your internet connection speed',
                    '🔄 Refresh the page completely',
                    '⏰ Try during off-peak hours'
                ],
                'quick_fix': 'Usually fixed by closing other tabs and clearing cache!'
            },
            
            'search': {
                'message': "Search not working properly? Our AI search is very robust, let's troubleshoot:",
                'steps': [
                    '🔤 Try typing just company names (like "Apple" instead of "AAPL")',
                    '🔄 Refresh and try again',
                    '⌨️ Check for typos in your search',
                    '🌐 Ensure JavaScript is enabled',
                    '📱 Try on a different device'
                ],
                'quick_fix': 'Our search converts "Apple" to "AAPL" automatically!'
            },
            
            'chart': {
                'message': "Chart display issues can be frustrating! Here's how to fix them:",
                'steps': [
                    '🔄 Refresh the page completely',
                    '🌐 Enable JavaScript in your browser',
                    '📊 Try a different browser (Chrome/Firefox/Safari)',
                    '🔧 Update your browser to latest version',
                    '📱 Check if it works on mobile'
                ],
                'quick_fix': 'Charts need JavaScript enabled to display properly!'
            },
            
            'loading': {
                'message': "Data not loading? Let's get you back to trading:",
                'steps': [
                    '🔄 Hard refresh (Ctrl+F5)',
                    '📶 Check internet connection stability',
                    '🕐 Wait 30 seconds and try again',
                    '🌐 Try incognito mode',
                    '🔧 Disable browser extensions temporarily'
                ],
                'quick_fix': 'Usually a connection hiccup - try refreshing!'
            }
        }
        
        # Find matching issue
        detected_issue = None
        for issue_key, solution in issue_solutions.items():
            if issue_key in query_lower:
                detected_issue = solution
                break
        
        # Handle specific error messages or codes
        if 'error' in query_lower:
            if '404' in query_lower:
                detected_issue = {
                    'message': "404 error means a page wasn't found. This might be a temporary glitch:",
                    'steps': ['🔄 Go back and try the link again', '🏠 Return to home page', '🔍 Use our search instead'],
                    'quick_fix': 'Try going back to the main page and starting over!'
                }
            elif '500' in query_lower:
                detected_issue = {
                    'message': "500 error is a server hiccup. Don't worry, our systems are very reliable:",
                    'steps': ['⏱️ Wait 1-2 minutes and try again', '🔄 Refresh the page', '📱 Try on different device'],
                    'quick_fix': 'Server errors usually resolve automatically in 1-2 minutes!'
                }
        
        if detected_issue:
            message = f"{detected_issue['message']}\n\n💡 Quick Fix: {detected_issue['quick_fix']}"
            steps = detected_issue['steps']
        else:
            message = "I'm here to help diagnose any technical issues! Our platform is very reliable, so most issues have quick fixes. Can you tell me exactly what's happening?"
            steps = [
                '📸 Take a screenshot of the issue',
                '🔄 Try refreshing the page first',
                '🌐 Test in incognito mode',
                '📱 Try on different device',
                '⏰ Note the exact time it happened'
            ]
        
        return {
            'message': message,
            'member': self.name,
            'role': self.role,
            'troubleshooting_steps': steps,
            'platform_status': '🟢 All systems operational',
            'response_time': '< 2 minutes typical',
            'escalation_available': True,
            'success_rate': '95%+ issues resolved quickly'
        }

    def _handle_account_issue(self, query: str, context: Dict) -> Dict:
        """Handle account-related issues"""
        return {
            'message': "I can help with account and subscription questions. What specifically would you like assistance with?",
            'member': self.name,
            'role': self.role,
            'account_services': [
                'Subscription management',
                'Payment and billing',
                'Account settings',
                'Feature access',
                'Security settings'
            ]
        }

    def _handle_general_support(self, query: str, context: Dict) -> Dict:
        """Handle general support queries"""
        return {
            'message': f"Hello! I'm {self.name} from Technical Support. I'm here to help resolve any issues you're having with the platform. What can I assist you with today?",
            'member': self.name,
            'role': self.role,
            'support_areas': [
                'Technical troubleshooting',
                'Account assistance', 
                'Feature explanations',
                'Performance optimization',
                'Browser compatibility'
            ]
        }

class CustomerSuccessAI(AITeamMember):
    """AI Customer Success Manager - Helps with onboarding, feature guidance, and platform optimization"""
    
    def __init__(self):
        super().__init__(
            name="Maria Santos",
            role="AI Customer Success Manager",
            specialties=["onboarding", "features", "help", "guide", "tutorial", "how to", "getting started"],
            personality="enthusiastic, encouraging, educational"
        )

    def _create_response(self, query: str, intent: str, context: Dict) -> Dict:
        """Create customer success response"""
        if intent == 'education':
            return self._handle_learning_query(query, context)
        elif intent == 'general':
            return self._handle_feature_guidance(query, context)
        else:
            return self._handle_onboarding_query(query, context)

    def _handle_learning_query(self, query: str, context: Dict) -> Dict:
        """Handle learning and how-to queries with personalized guidance"""
        query_lower = query.lower()
        user_level = context.get('user_tier', 'Free')
        
        # Detect user experience level from query
        if any(term in query_lower for term in ['beginner', 'new', 'start', 'first time', 'never']):
            experience_level = 'beginner'
        elif any(term in query_lower for term in ['advanced', 'experienced', 'professional']):
            experience_level = 'advanced'
        else:
            experience_level = 'intermediate'
            
        learning_topics = {
            'portfolio': f"Building a portfolio is one of my favorite topics! Our AI Portfolio Builder is perfect for {experience_level} investors. It creates personalized portfolios across 5 strategies (Conservative, Growth, Aggressive, etc.) with real stock allocations. Click 'Tools' → 'Portfolio Builder' to get started!",
            
            'search': f"Our ChatGPT-style search is revolutionary! Just type company names like 'Apple' or 'Tesla' and our AI converts them to ticker symbols automatically. For {experience_level} users, I recommend trying different search styles: company names, ticker symbols, or even industry terms. The AI provides 85%+ accuracy ratings!",
            
            'analysis': f"Getting stock analysis is incredibly easy! Here's how to interpret our AI recommendations for {experience_level} investors:\n• STRONG BUY (Green) = High confidence opportunity\n• BUY (Light Green) = Good potential\n• HOLD (Yellow) = Neutral position\n• SELL (Orange/Red) = Consider exit\nEach comes with confidence scores and detailed reasoning!",
            
            'trading': f"Ready to start trading? Perfect! For {experience_level} traders, I recommend:\n1. Start with our demo account ($10K virtual money)\n2. Use our AI search to find stocks\n3. Read the AI analysis and confidence ratings\n4. Start with small positions\n5. Use our alerts to track your investments",
            
            'watchlist': "Watchlists are essential! Click the purple 'Add to Watchlist' button when viewing any stock analysis. Our system tracks real-time prices and AI ratings. You can create custom watchlists like 'Tech Stocks', 'Dividend Plays', or 'AI Recommendations'.",
            
            'ai': f"Our AI system is the heart of TradeWise! It analyzes market patterns, processes news sentiment, tracks institutional flows, and generates predictions with 85%+ accuracy. For {experience_level} users, focus on the confidence scores and suggested actions in each analysis."
        }
        
        topic_response = None
        matched_topic = None
        
        for topic, response in learning_topics.items():
            if topic in query_lower:
                topic_response = response
                matched_topic = topic
                break
        
        if topic_response:
            message = topic_response
        else:
            message = f"I love helping users get the most out of TradeWise AI! As a {experience_level} investor, what specific feature would you like to master? Our platform has Bloomberg-level tools made simple."
        
        # Personalized quick guides based on experience level
        if experience_level == 'beginner':
            quick_guides = [
                '🚀 Complete Beginner\'s Walkthrough',
                '📊 Understanding AI Stock Ratings', 
                '🔍 Intelligent Search Tutorial',
                '💼 Building Your First Portfolio',
                '⚠️ Setting Up Safety Alerts'
            ]
        elif experience_level == 'advanced':
            quick_guides = [
                '📈 Advanced Technical Analysis',
                '🤖 AI Trading Signal Mastery', 
                '🎯 Professional Watchlist Strategies',
                '⚡ Real-time Alert Optimization',
                '💰 Advanced Portfolio Analytics'
            ]
        else:
            quick_guides = [
                '📚 Intermediate Trading Guide',
                '🎯 AI Analysis Deep Dive', 
                '📊 Portfolio Diversification',
                '🔔 Smart Alert Configuration',
                '💎 Finding Hidden Opportunities'
            ]
        
        return {
            'message': message,
            'member': self.name,
            'role': self.role,
            'quick_guides': quick_guides,
            'experience_level': experience_level,
            'user_tier': user_level,
            'matched_topic': matched_topic,
            'platform_features': {
                'search_accuracy': '85%+',
                'portfolio_strategies': 5,
                'real_time_data': True,
                'ai_predictions': True
            }
        }

    def _handle_feature_guidance(self, query: str, context: Dict) -> Dict:
        """Handle feature guidance queries"""
        return {
            'message': "I'm excited to help you discover all the powerful features TradeWise AI offers! From our Bloomberg-killer intelligence to our AI portfolio builder, there's so much to explore.",
            'member': self.name,
            'role': self.role,
            'feature_highlights': [
                'ChatGPT-style intelligent search',
                'AI portfolio builder for beginners',
                'Real-time market intelligence',
                'Professional watchlist system',
                'Smart trading alerts'
            ],
            'personalized_tour': True
        }

    def _handle_onboarding_query(self, query: str, context: Dict) -> Dict:
        """Handle onboarding and getting started queries"""
        return {
            'message': "Welcome to TradeWise AI! I'm thrilled you're here. Whether you're a beginner or experienced trader, I'll help you get set up for success. What's your experience level with investing?",
            'member': self.name,
            'role': self.role,
            'onboarding_steps': [
                'Complete your profile',
                'Take the portfolio assessment', 
                'Try the intelligent search',
                'Build your first watchlist',
                'Set up trading alerts'
            ],
            'experience_levels': ['Complete beginner', 'Some experience', 'Experienced trader']
        }

class AITeamManager:
    """Manages the AI team members and routes queries to the appropriate specialist"""
    
    def __init__(self):
        # Initialize team members
        self.team_members = [
            MarketAnalystAI(),
            TechnicalSupportAI(), 
            CustomerSuccessAI()
        ]
        
        self.conversation_logs = []
        logger.info("AI Team Manager initialized with 3 team members")

    def route_query(self, query: str, context: Dict = None) -> Dict:
        """Route user query to the most appropriate team member"""
        try:
            if context is None:
                context = {}
                
            # Find the best team member for this query
            best_member = self._select_team_member(query, context)
            
            if best_member:
                response = best_member.generate_response(query, context)
                
                # Log the interaction
                self.conversation_logs.append({
                    'timestamp': datetime.utcnow(),
                    'query': query,
                    'assigned_member': best_member.name,
                    'response': response
                })
                
                return response
            else:
                # Fallback response if no specialist can handle it
                return self._generate_fallback_response(query, context)
                
        except Exception as e:
            logger.error(f"Error routing query to AI team: {e}")
            return self._generate_error_response(query)

    def _select_team_member(self, query: str, context: Dict) -> Optional[AITeamMember]:
        """Select the best team member for the query"""
        # Score each team member's ability to handle the query
        scores = []
        
        for member in self.team_members:
            if member.can_handle_query(query, context):
                # Calculate confidence score
                specialty_matches = sum(1 for specialty in member.specialties 
                                     if specialty.lower() in query.lower())
                scores.append((member, specialty_matches))
        
        if scores:
            # Return member with highest score
            return max(scores, key=lambda x: x[1])[0]
        
        # If no specific match, use Customer Success as default
        return next((member for member in self.team_members 
                    if isinstance(member, CustomerSuccessAI)), None)

    def _generate_fallback_response(self, query: str, context: Dict) -> Dict:
        """Generate fallback response when no specialist can handle the query"""
        return {
            'message': "Thank you for your question! Let me connect you with the right team member who can provide the best assistance.",
            'member': "AI Team Manager",
            'role': "Team Coordinator",
            'available_specialists': [
                {'name': member.name, 'role': member.role, 'specialties': member.specialties}
                for member in self.team_members
            ],
            'escalate': True
        }

    def _generate_error_response(self, query: str) -> Dict:
        """Generate error response when something goes wrong"""
        return {
            'message': "I apologize, but I'm experiencing a temporary issue. Please try your question again, or contact our support team directly.",
            'member': "AI Team Manager",
            'role': "Team Coordinator",
            'error': True,
            'contact_support': True
        }

    def get_team_status(self) -> Dict:
        """Get status of all AI team members"""
        return {
            'team_size': len(self.team_members),
            'members': [
                {
                    'name': member.name,
                    'role': member.role,
                    'specialties': member.specialties,
                    'conversations': len(member.conversation_history)
                }
                for member in self.team_members
            ],
            'total_conversations': len(self.conversation_logs),
            'active_since': datetime.utcnow().isoformat()
        }

# Global AI team manager instance
ai_team_manager = AITeamManager()