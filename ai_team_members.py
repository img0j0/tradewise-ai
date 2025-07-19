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
        """Handle trading-related queries"""
        template = random.choice(self.response_templates['trading'])
        
        # Analyze query for stock symbols or market terms
        query_upper = query.upper()
        stock_mentions = []
        
        common_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
        for stock in common_stocks:
            if stock in query_upper:
                stock_mentions.append(stock)
        
        if stock_mentions:
            message = f"{template} I notice you're asking about {', '.join(stock_mentions)}. "
            message += "Let me pull up the latest analysis and market data for you."
        else:
            message = f"{template} I can help you analyze specific stocks, market trends, or portfolio strategies."
        
        return {
            'message': message,
            'member': self.name,
            'role': self.role,
            'suggested_actions': [
                'Search for specific stocks',
                'View market overview',
                'Check portfolio analysis',
                'Get AI trading signals'
            ],
            'stocks_mentioned': stock_mentions
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
        """Handle technical problems"""
        common_issues = {
            'login': "I can help with login issues. First, let's try clearing your browser cache...",
            'slow': "If the platform is running slowly, this might help...",
            'error': "I see you're getting an error. Let me help troubleshoot this...",
            'chart': "Chart display issues are usually related to browser compatibility..."
        }
        
        query_lower = query.lower()
        issue_response = None
        
        for issue, response in common_issues.items():
            if issue in query_lower:
                issue_response = response
                break
        
        if issue_response:
            message = issue_response
        else:
            message = "I'm here to help with any technical issues you're experiencing. Can you describe what's happening in more detail?"
        
        return {
            'message': message,
            'member': self.name,
            'role': self.role,
            'troubleshooting_steps': [
                'Clear browser cache and cookies',
                'Try a different browser',
                'Check internet connection',
                'Refresh the page'
            ],
            'escalation_available': True
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
        """Handle learning and how-to queries"""
        learning_topics = {
            'portfolio': "Building a portfolio is one of my favorite topics! Let me show you our AI Portfolio Builder...",
            'search': "Our ChatGPT-style search is incredibly powerful. You can search by company name...",
            'analysis': "Getting stock analysis is easy! Here's how to interpret our AI recommendations...",
            'trading': "Ready to start trading? I'll walk you through your first trade step-by-step..."
        }
        
        query_lower = query.lower()
        topic_response = None
        
        for topic, response in learning_topics.items():
            if topic in query_lower:
                topic_response = response
                break
        
        if topic_response:
            message = topic_response
        else:
            message = "I love helping users get the most out of TradeWise AI! What feature would you like to learn about?"
        
        return {
            'message': message,
            'member': self.name,
            'role': self.role,
            'quick_guides': [
                'First Trade Walkthrough',
                'Portfolio Building Guide', 
                'AI Search Tutorial',
                'Watchlist Setup',
                'Alert Configuration'
            ]
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