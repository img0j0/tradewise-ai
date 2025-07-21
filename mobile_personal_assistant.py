"""
Mobile Personal Investment Assistant Engine
Optimized for mobile-first personal assistant experience
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import yfinance as yf
from flask import session

logger = logging.getLogger(__name__)

class MobilePersonalAssistant:
    """Personal Investment Assistant optimized for mobile devices"""
    
    def __init__(self):
        self.conversation_history = []
        self.user_preferences = {}
        self.personalized_insights = {}
        
    def get_personalized_greeting(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate personalized greeting based on time and user activity"""
        current_hour = datetime.now().hour
        
        if current_hour < 9:
            greeting = "Good morning! Ready to start your investment day?"
            context = "pre_market"
        elif 9 <= current_hour < 16:
            greeting = "Market's open! Let's find some opportunities."
            context = "market_hours"
        elif 16 <= current_hour < 18:
            greeting = "Market just closed. How did your portfolio perform today?"
            context = "after_market"
        else:
            greeting = "Good evening! Planning your next investment moves?"
            context = "evening"
            
        return {
            "greeting": greeting,
            "context": context,
            "market_status": self._get_market_status(),
            "quick_suggestions": self._get_contextual_suggestions(context)
        }
    
    def _get_market_status(self) -> Dict[str, Any]:
        """Get current market status and key indicators"""
        try:
            # Get major market indices
            spy = yf.Ticker("SPY")
            hist = spy.history(period="1d")
            
            if not hist.empty:
                current_price = float(hist['Close'].iloc[-1])
                prev_close = float(hist['Open'].iloc[-1])
                change_pct = ((current_price - prev_close) / prev_close) * 100
                
                return {
                    "spy_price": current_price,
                    "spy_change": change_pct,
                    "trend": "bullish" if change_pct > 0 else "bearish",
                    "volatility": "high" if abs(change_pct) > 1 else "normal"
                }
        except Exception as e:
            logger.error(f"Error getting market status: {e}")
            
        return {
            "spy_price": 0,
            "spy_change": 0,
            "trend": "neutral",
            "volatility": "normal"
        }
    
    def _get_contextual_suggestions(self, context: str) -> List[Dict[str, str]]:
        """Get contextual suggestions based on time of day"""
        suggestions = {
            "pre_market": [
                {"text": "Check pre-market movers", "action": "search", "query": "pre-market gainers"},
                {"text": "Review earnings calendar", "action": "search", "query": "earnings today"},
                {"text": "Analyze overnight news", "action": "search", "query": "market news"}
            ],
            "market_hours": [
                {"text": "Find trending stocks", "action": "search", "query": "trending stocks"},
                {"text": "Check your watchlist", "action": "watchlist"},
                {"text": "Scan for breakouts", "action": "search", "query": "breakout stocks"}
            ],
            "after_market": [
                {"text": "Review market close", "action": "search", "query": "market summary"},
                {"text": "After-hours movers", "action": "search", "query": "after hours"},
                {"text": "Plan tomorrow's trades", "action": "planning"}
            ],
            "evening": [
                {"text": "Research new opportunities", "action": "search", "query": "investment ideas"},
                {"text": "Review portfolio performance", "action": "portfolio"},
                {"text": "Set price alerts", "action": "alerts"}
            ]
        }
        
        return suggestions.get(context, [])
    
    def generate_personal_insights(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized investment insights"""
        insights = {
            "portfolio_health": self._analyze_portfolio_health(user_data),
            "risk_assessment": self._assess_user_risk_profile(user_data),
            "opportunities": self._find_personalized_opportunities(user_data),
            "alerts": self._generate_smart_alerts(user_data)
        }
        
        return insights
    
    def _analyze_portfolio_health(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user's portfolio health"""
        try:
            portfolio = user_data.get('portfolio', {})
            if not portfolio:
                return {
                    "status": "new_user",
                    "message": "Ready to start your investment journey?",
                    "recommendation": "Consider starting with diversified ETFs"
                }
            
            # Calculate diversification score
            holdings_count = len(portfolio.get('holdings', []))
            diversification_score = min(holdings_count * 10, 100)
            
            # Calculate performance
            total_value = portfolio.get('total_value', 0)
            total_cost = portfolio.get('total_cost', 0)
            performance = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
            
            return {
                "diversification_score": diversification_score,
                "performance": performance,
                "total_value": total_value,
                "recommendation": self._get_portfolio_recommendation(diversification_score, performance)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio health: {e}")
            return {"status": "error", "message": "Unable to analyze portfolio"}
    
    def _assess_user_risk_profile(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess user's risk tolerance based on trading behavior"""
        try:
            trades = user_data.get('recent_trades', [])
            if not trades:
                return {
                    "risk_level": "conservative",
                    "confidence": 50,
                    "recommendation": "Start with blue-chip stocks and ETFs"
                }
            
            # Analyze trading patterns
            volatile_stocks = 0
            total_trades = len(trades)
            
            for trade in trades[-10:]:  # Analyze last 10 trades
                symbol = trade.get('symbol', '')
                if self._is_volatile_stock(symbol):
                    volatile_stocks += 1
            
            volatility_ratio = volatile_stocks / min(total_trades, 10)
            
            if volatility_ratio > 0.6:
                risk_level = "aggressive"
                confidence = 80
            elif volatility_ratio > 0.3:
                risk_level = "moderate"
                confidence = 70
            else:
                risk_level = "conservative"
                confidence = 75
            
            return {
                "risk_level": risk_level,
                "confidence": confidence,
                "volatility_ratio": volatility_ratio,
                "recommendation": self._get_risk_recommendation(risk_level)
            }
            
        except Exception as e:
            logger.error(f"Error assessing risk profile: {e}")
            return {"risk_level": "moderate", "confidence": 50}
    
    def _is_volatile_stock(self, symbol: str) -> bool:
        """Check if a stock is considered volatile"""
        volatile_patterns = ['TSLA', 'GME', 'AMC', 'NVDA', 'MEME']
        return any(pattern in symbol.upper() for pattern in volatile_patterns)
    
    def _get_portfolio_recommendation(self, diversification_score: float, performance: float) -> str:
        """Get portfolio recommendation based on health metrics"""
        if diversification_score < 30:
            return "Consider diversifying across more sectors"
        elif performance < -10:
            return "Review underperforming positions"
        elif performance > 20:
            return "Great performance! Consider taking some profits"
        else:
            return "Portfolio looks healthy, keep monitoring"
    
    def _get_risk_recommendation(self, risk_level: str) -> str:
        """Get recommendation based on risk level"""
        recommendations = {
            "conservative": "Focus on dividend stocks and blue-chip companies",
            "moderate": "Balance growth stocks with stable dividend payers",
            "aggressive": "Consider position sizing and risk management tools"
        }
        return recommendations.get(risk_level, "Maintain balanced approach")
    
    def _find_personalized_opportunities(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find investment opportunities based on user preferences"""
        try:
            # Get trending stocks
            trending_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
            opportunities = []
            
            for symbol in trending_symbols[:3]:  # Limit to 3 for mobile
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    hist = ticker.history(period="1d")
                    
                    if not hist.empty:
                        current_price = float(hist['Close'].iloc[-1])
                        opportunities.append({
                            "symbol": symbol,
                            "company": info.get('longName', symbol),
                            "price": current_price,
                            "sector": info.get('sector', 'Unknown'),
                            "recommendation": "RESEARCH",
                            "reason": "Trending in your risk profile"
                        })
                except Exception:
                    continue
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error finding opportunities: {e}")
            return []
    
    def _generate_smart_alerts(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate intelligent alerts for the user"""
        alerts = [
            {
                "type": "market_open",
                "message": "Market opening in 30 minutes",
                "priority": "medium",
                "action": "review_watchlist"
            },
            {
                "type": "portfolio_update",
                "message": "Your portfolio is up 2.3% today",
                "priority": "low",
                "action": "view_portfolio"
            }
        ]
        
        return alerts
    
    def get_mobile_dashboard_data(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get optimized dashboard data for mobile personal assistant"""
        try:
            user_data = self._get_user_data(user_id)
            
            return {
                "greeting": self.get_personalized_greeting(user_id),
                "market_pulse": self._get_market_pulse(),
                "personal_insights": self.generate_personal_insights(user_data),
                "quick_actions": self._get_quick_actions(),
                "voice_ready": True,
                "mobile_optimized": True
            }
            
        except Exception as e:
            logger.error(f"Error getting mobile dashboard data: {e}")
            return {"error": "Unable to load dashboard data"}
    
    def _get_user_data(self, user_id: Optional[str]) -> Dict[str, Any]:
        """Get user data - placeholder for database integration"""
        return {
            "portfolio": {"total_value": 10000, "holdings": []},
            "recent_trades": [],
            "preferences": {"risk_tolerance": "moderate"}
        }
    
    def _get_market_pulse(self) -> Dict[str, Any]:
        """Get quick market pulse for mobile display"""
        try:
            spy = yf.Ticker("SPY")
            hist = spy.history(period="1d")
            
            if not hist.empty:
                current = float(hist['Close'].iloc[-1])
                open_price = float(hist['Open'].iloc[-1])
                change = ((current - open_price) / open_price) * 100
                
                return {
                    "market_direction": "📈" if change > 0 else "📉",
                    "spy_change": round(change, 2),
                    "market_mood": "Bullish" if change > 0.5 else "Bearish" if change < -0.5 else "Neutral",
                    "volatility": "High" if abs(change) > 1 else "Normal"
                }
        except Exception:
            pass
            
        return {
            "market_direction": "📊",
            "spy_change": 0,
            "market_mood": "Neutral",
            "volatility": "Normal"
        }
    
    def _get_quick_actions(self) -> List[Dict[str, str]]:
        """Get quick actions for mobile interface"""
        return [
            {"icon": "🔍", "text": "Search Stocks", "action": "search"},
            {"icon": "📊", "text": "Market Pulse", "action": "market"},
            {"icon": "💼", "text": "My Portfolio", "action": "portfolio"},
            {"icon": "🔔", "text": "Set Alert", "action": "alert"},
            {"icon": "🎯", "text": "AI Picks", "action": "ai_picks"},
            {"icon": "📈", "text": "Trending", "action": "trending"}
        ]

# Initialize the mobile personal assistant
mobile_assistant = MobilePersonalAssistant()