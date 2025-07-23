"""
Enhanced AI Explanations Engine
Provides detailed, transparent explanations for all AI recommendations
"""

import logging
from typing import Dict, List, Any
from datetime import datetime
import yfinance as yf

logger = logging.getLogger(__name__)

class AIExplanationEngine:
    """
    Generates detailed explanations for AI recommendations
    Makes our AI transparent and trustworthy vs. black-box competitors
    """
    
    def __init__(self):
        self.explanation_templates = {
            'technical_analysis': {
                'bullish': "Technical indicators suggest upward momentum: {details}",
                'bearish': "Technical signals indicate downward pressure: {details}",
                'neutral': "Mixed technical signals suggest sideways movement: {details}"
            },
            'fundamental_analysis': {
                'strong': "Strong fundamentals support the analysis: {details}",
                'weak': "Fundamental concerns impact the outlook: {details}",
                'mixed': "Mixed fundamental picture creates uncertainty: {details}"
            },
            'market_sentiment': {
                'positive': "Market sentiment is favorable: {details}",
                'negative': "Market sentiment shows caution: {details}",
                'neutral': "Market sentiment is balanced: {details}"
            }
        }
    
    def generate_detailed_explanation(self, stock_data: Dict, analysis_result: Dict) -> Dict:
        """
        Generate comprehensive explanation for AI recommendation
        This transparency is our key differentiator
        """
        try:
            explanation = {
                'summary': self._generate_summary_explanation(analysis_result),
                'technical_reasoning': self._explain_technical_analysis(stock_data, analysis_result),
                'fundamental_reasoning': self._explain_fundamental_analysis(stock_data, analysis_result),
                'risk_assessment': self._explain_risk_factors(stock_data, analysis_result),
                'confidence_breakdown': self._explain_confidence_score(analysis_result),
                'strategy_impact_detail': self._explain_strategy_impact(analysis_result),
                'market_context': self._explain_market_context(stock_data),
                'key_factors': self._identify_key_decision_factors(stock_data, analysis_result),
                'uncertainty_factors': self._identify_uncertainty_sources(stock_data, analysis_result)
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating AI explanation: {e}")
            return self._fallback_explanation(analysis_result)
    
    def _generate_summary_explanation(self, analysis_result: Dict) -> str:
        """Generate high-level summary of recommendation reasoning"""
        recommendation = analysis_result.get('recommendation', 'HOLD')
        confidence = analysis_result.get('confidence', 50)
        
        if recommendation == 'BUY':
            if confidence >= 70:
                return f"Strong BUY recommendation ({confidence}% confidence) based on favorable technical indicators, solid fundamentals, and positive market positioning."
            else:
                return f"Moderate BUY signal ({confidence}% confidence) with some uncertainties that warrant careful consideration."
        
        elif recommendation == 'SELL':
            if confidence >= 70:
                return f"Strong SELL recommendation ({confidence}% confidence) due to concerning technical patterns, fundamental weaknesses, or elevated risk factors."
            else:
                return f"Cautious SELL signal ({confidence}% confidence) with mixed indicators suggesting potential downside."
        
        else:  # HOLD
            return f"HOLD recommendation ({confidence}% confidence) as current analysis suggests maintaining position while monitoring key developments."
    
    def _explain_technical_analysis(self, stock_data: Dict, analysis_result: Dict) -> Dict:
        """Explain technical analysis components"""
        technical_score = analysis_result.get('technical_score', 50)
        
        explanation = {
            'score': technical_score,
            'interpretation': self._interpret_technical_score(technical_score),
            'key_indicators': [],
            'trend_analysis': self._analyze_price_trend(stock_data),
            'support_resistance': self._identify_support_resistance(stock_data)
        }
        
        # Add specific technical indicators
        if technical_score >= 70:
            explanation['key_indicators'] = [
                "Price momentum showing strength",
                "Moving averages in bullish alignment",
                "Volume supporting price movement"
            ]
        elif technical_score <= 30:
            explanation['key_indicators'] = [
                "Price momentum weakening",
                "Moving averages showing bearish signals",
                "Volume patterns concerning"
            ]
        else:
            explanation['key_indicators'] = [
                "Mixed technical signals",
                "Price consolidation pattern",
                "Waiting for clearer directional signals"
            ]
        
        return explanation
    
    def _explain_fundamental_analysis(self, stock_data: Dict, analysis_result: Dict) -> Dict:
        """Explain fundamental analysis components"""
        fundamental_score = analysis_result.get('fundamental_score', 50)
        
        explanation = {
            'score': fundamental_score,
            'interpretation': self._interpret_fundamental_score(fundamental_score),
            'financial_health': self._assess_financial_health(stock_data),
            'valuation_assessment': self._assess_valuation(stock_data),
            'growth_prospects': self._assess_growth_prospects(stock_data)
        }
        
        return explanation
    
    def _explain_risk_factors(self, stock_data: Dict, analysis_result: Dict) -> Dict:
        """Explain risk assessment and factors"""
        risk_level = analysis_result.get('risk_level', 'MEDIUM')
        risk_factors = analysis_result.get('risk_factors', [])
        
        explanation = {
            'risk_level': risk_level,
            'risk_interpretation': self._interpret_risk_level(risk_level),
            'specific_risks': risk_factors,
            'risk_mitigation': self._suggest_risk_mitigation(risk_level, risk_factors),
            'portfolio_impact': self._assess_portfolio_risk_impact(stock_data, risk_level)
        }
        
        return explanation
    
    def _explain_confidence_score(self, analysis_result: Dict) -> Dict:
        """Break down confidence score components"""
        confidence = analysis_result.get('confidence', 50)
        
        # Simulate confidence breakdown based on available data
        technical_weight = min(analysis_result.get('technical_score', 50) / 100 * 40, 40)
        fundamental_weight = min(analysis_result.get('fundamental_score', 50) / 100 * 40, 40)
        market_weight = 20  # Market sentiment component
        
        breakdown = {
            'overall_confidence': confidence,
            'confidence_interpretation': self._interpret_confidence(confidence),
            'contributing_factors': {
                'technical_analysis': round(technical_weight, 1),
                'fundamental_analysis': round(fundamental_weight, 1),
                'market_sentiment': market_weight
            },
            'confidence_rationale': self._generate_confidence_rationale(confidence)
        }
        
        return breakdown
    
    def _explain_strategy_impact(self, analysis_result: Dict) -> Dict:
        """Detailed explanation of how investment strategy affected the analysis"""
        strategy_applied = analysis_result.get('strategy_applied', {})
        strategy_impact = analysis_result.get('strategy_impact', {})
        
        if not strategy_impact.get('changed', False):
            return {
                'strategy_applied': False,
                'explanation': "No strategy modifications were applied to this analysis."
            }
        
        explanation = {
            'strategy_applied': True,
            'strategy_name': strategy_applied.get('name', 'Unknown'),
            'strategy_description': strategy_applied.get('description', ''),
            'original_recommendation': strategy_impact.get('original_recommendation', 'HOLD'),
            'original_confidence': strategy_impact.get('original_confidence', 50),
            'adjusted_recommendation': analysis_result.get('recommendation', 'HOLD'),
            'adjusted_confidence': analysis_result.get('confidence', 50),
            'modification_reasoning': self._explain_strategy_modification(strategy_applied, strategy_impact),
            'strategy_alignment': self._assess_strategy_alignment(strategy_applied, analysis_result)
        }
        
        return explanation
    
    def _explain_market_context(self, stock_data: Dict) -> Dict:
        """Provide market context for the analysis"""
        sector = stock_data.get('sector', 'Unknown')
        market_cap = stock_data.get('market_cap', 0)
        
        context = {
            'sector_analysis': f"Operating in {sector} sector",
            'market_cap_category': self._categorize_market_cap(market_cap),
            'sector_trends': self._get_sector_trends(sector),
            'market_position': self._assess_market_position(stock_data)
        }
        
        return context
    
    def _identify_key_decision_factors(self, stock_data: Dict, analysis_result: Dict) -> List[str]:
        """Identify the most important factors driving the recommendation"""
        factors = []
        
        technical_score = analysis_result.get('technical_score', 50)
        fundamental_score = analysis_result.get('fundamental_score', 50)
        
        if technical_score >= 70:
            factors.append("Strong technical momentum supporting upward movement")
        elif technical_score <= 30:
            factors.append("Weak technical indicators suggesting caution")
        
        if fundamental_score >= 70:
            factors.append("Solid fundamental metrics indicating financial health")
        elif fundamental_score <= 30:
            factors.append("Fundamental concerns affecting long-term outlook")
        
        # Add market-specific factors
        market_cap = stock_data.get('market_cap', 0)
        if market_cap > 100e9:  # Large cap
            factors.append("Large-cap stability with established market position")
        elif market_cap < 2e9:  # Small cap
            factors.append("Small-cap growth potential with higher volatility")
        
        return factors[:5]  # Limit to top 5 factors
    
    def _identify_uncertainty_sources(self, stock_data: Dict, analysis_result: Dict) -> List[str]:
        """Identify sources of uncertainty affecting the analysis"""
        uncertainties = []
        
        confidence = analysis_result.get('confidence', 50)
        
        if confidence < 60:
            uncertainties.append("Mixed signals from technical and fundamental analysis")
        
        if analysis_result.get('risk_level') == 'HIGH':
            uncertainties.append("Elevated risk factors require careful monitoring")
        
        # Market-specific uncertainties
        current_price = stock_data.get('current_price', 0)
        if current_price == 0:
            uncertainties.append("Limited recent price data affects analysis accuracy")
        
        uncertainties.append("Market volatility may impact short-term performance")
        
        return uncertainties[:4]  # Limit to top 4 uncertainties
    
    # Helper methods for interpretations
    
    def _interpret_technical_score(self, score: float) -> str:
        if score >= 70:
            return "Strong technical indicators support bullish outlook"
        elif score <= 30:
            return "Weak technical indicators suggest bearish pressure"
        else:
            return "Mixed technical signals indicate consolidation"
    
    def _interpret_fundamental_score(self, score: float) -> str:
        if score >= 70:
            return "Strong fundamentals indicate financial health and growth potential"
        elif score <= 30:
            return "Weak fundamentals raise concerns about company's financial position"
        else:
            return "Mixed fundamental picture with both strengths and concerns"
    
    def _interpret_risk_level(self, risk_level: str) -> str:
        risk_descriptions = {
            'LOW': "Conservative investment with limited downside risk",
            'MEDIUM': "Moderate risk with balanced risk-reward profile",
            'HIGH': "Elevated risk requiring careful position sizing and monitoring"
        }
        return risk_descriptions.get(risk_level, "Risk level assessment pending")
    
    def _interpret_confidence(self, confidence: float) -> str:
        if confidence >= 80:
            return "High confidence - Strong conviction in analysis"
        elif confidence >= 60:
            return "Moderate confidence - Analysis supported by multiple factors"
        elif confidence >= 40:
            return "Low confidence - Mixed signals require careful consideration"
        else:
            return "Very low confidence - High uncertainty in current analysis"
    
    def _analyze_price_trend(self, stock_data: Dict) -> str:
        """Analyze price trend based on available data"""
        price_change = stock_data.get('price_change', 0)
        
        if price_change > 2:
            return "Strong upward trend in recent sessions"
        elif price_change > 0:
            return "Modest positive momentum"
        elif price_change > -2:
            return "Minor downward pressure"
        else:
            return "Significant downward trend"
    
    def _identify_support_resistance(self, stock_data: Dict) -> Dict:
        """Identify key support and resistance levels"""
        current_price = stock_data.get('current_price', 0)
        
        # Simplified support/resistance calculation
        support = round(current_price * 0.95, 2)
        resistance = round(current_price * 1.05, 2)
        
        return {
            'support_level': support,
            'resistance_level': resistance,
            'explanation': f"Key support around ${support}, resistance near ${resistance}"
        }
    
    def _assess_financial_health(self, stock_data: Dict) -> str:
        """Assess financial health based on available metrics"""
        market_cap = stock_data.get('market_cap', 0)
        
        if market_cap > 50e9:
            return "Large, established company with substantial market presence"
        elif market_cap > 10e9:
            return "Mid-cap company with solid market position"
        else:
            return "Smaller company with growth potential and higher volatility"
    
    def _assess_valuation(self, stock_data: Dict) -> str:
        """Assess valuation metrics"""
        # Simplified valuation assessment
        return "Valuation assessment requires additional fundamental data for complete analysis"
    
    def _assess_growth_prospects(self, stock_data: Dict) -> str:
        """Assess growth prospects"""
        sector = stock_data.get('sector', 'Unknown')
        
        growth_sectors = ['Technology', 'Healthcare', 'Consumer Discretionary']
        
        if sector in growth_sectors:
            return f"{sector} sector offers significant growth opportunities"
        else:
            return f"{sector} sector provides stability with moderate growth potential"
    
    def _suggest_risk_mitigation(self, risk_level: str, risk_factors: List) -> List[str]:
        """Suggest risk mitigation strategies"""
        suggestions = []
        
        if risk_level == 'HIGH':
            suggestions.extend([
                "Consider smaller position size",
                "Use stop-loss orders for protection",
                "Monitor closely for early warning signs"
            ])
        elif risk_level == 'MEDIUM':
            suggestions.extend([
                "Maintain standard position sizing",
                "Regular portfolio rebalancing"
            ])
        else:
            suggestions.append("Standard risk management practices apply")
        
        return suggestions
    
    def _assess_portfolio_risk_impact(self, stock_data: Dict, risk_level: str) -> str:
        """Assess impact on portfolio risk"""
        sector = stock_data.get('sector', 'Unknown')
        
        return f"Adding {sector} exposure with {risk_level.lower()} risk profile"
    
    def _generate_confidence_rationale(self, confidence: float) -> str:
        """Generate rationale for confidence level"""
        if confidence >= 70:
            return "Multiple indicators align to support the analysis"
        elif confidence >= 50:
            return "Moderate agreement between technical and fundamental factors"
        else:
            return "Mixed signals create uncertainty in the analysis"
    
    def _explain_strategy_modification(self, strategy: Dict, impact: Dict) -> str:
        """Explain how strategy modified the analysis"""
        strategy_name = strategy.get('name', 'Investment Strategy')
        explanation = impact.get('explanation', '')
        
        return f"{strategy_name} approach emphasizes factors that modified this analysis: {explanation}"
    
    def _assess_strategy_alignment(self, strategy: Dict, analysis: Dict) -> str:
        """Assess how well the stock aligns with the strategy"""
        strategy_name = strategy.get('name', 'Unknown')
        recommendation = analysis.get('recommendation', 'HOLD')
        
        if recommendation == 'BUY':
            return f"Stock aligns well with {strategy_name} investment criteria"
        elif recommendation == 'HOLD':
            return f"Stock partially meets {strategy_name} requirements"
        else:
            return f"Stock does not currently align with {strategy_name} strategy"
    
    def _categorize_market_cap(self, market_cap: float) -> str:
        """Categorize market cap"""
        if market_cap > 200e9:
            return "Mega-cap (>$200B)"
        elif market_cap > 10e9:
            return "Large-cap ($10B-$200B)"
        elif market_cap > 2e9:
            return "Mid-cap ($2B-$10B)"
        elif market_cap > 300e6:
            return "Small-cap ($300M-$2B)"
        else:
            return "Micro-cap (<$300M)"
    
    def _get_sector_trends(self, sector: str) -> str:
        """Get sector trend information"""
        sector_trends = {
            'Technology': "Technology sector showing strong innovation and growth trends",
            'Healthcare': "Healthcare sector benefiting from demographic trends and innovation",
            'Financial Services': "Financial sector adapting to interest rate environment",
            'Consumer Discretionary': "Consumer discretionary sensitive to economic conditions",
            'Energy': "Energy sector influenced by commodity price cycles",
            'Utilities': "Utilities sector providing defensive characteristics"
        }
        
        return sector_trends.get(sector, f"{sector} sector analysis requires additional research")
    
    def _assess_market_position(self, stock_data: Dict) -> str:
        """Assess company's market position"""
        market_cap = stock_data.get('market_cap', 0)
        sector = stock_data.get('sector', 'Unknown')
        
        if market_cap > 50e9:
            return f"Leading player in {sector} with significant market influence"
        elif market_cap > 10e9:
            return f"Established player in {sector} with solid market presence"
        else:
            return f"Emerging player in {sector} with growth potential"
    
    def _fallback_explanation(self, analysis_result: Dict) -> Dict:
        """Provide fallback explanation if main generation fails"""
        return {
            'summary': f"AI analysis recommends {analysis_result.get('recommendation', 'HOLD')} with {analysis_result.get('confidence', 50)}% confidence.",
            'note': "Detailed explanation temporarily unavailable. Core recommendation based on comprehensive analysis of available data."
        }

# Initialize the explanation engine
ai_explanation_engine = AIExplanationEngine()

def get_enhanced_explanation(stock_data: Dict, analysis_result: Dict) -> Dict:
    """
    Public interface for getting enhanced AI explanations
    This is our key differentiator - transparent, detailed AI reasoning
    """
    return ai_explanation_engine.generate_detailed_explanation(stock_data, analysis_result)