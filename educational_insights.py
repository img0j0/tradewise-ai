"""
Educational Insights Engine
Integrates learning opportunities into every stock analysis
Key differentiator: Education-first approach vs. pure trading focus
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EducationalInsightsEngine:
    """
    Provides educational context and learning opportunities for every analysis
    Our competitive advantage: Users learn while they invest
    """
    
    def __init__(self):
        self.learning_modules = {
            'fundamental_analysis': {
                'title': 'Understanding Fundamental Analysis',
                'key_concepts': ['P/E Ratio', 'Revenue Growth', 'Debt-to-Equity', 'Market Cap'],
                'difficulty': 'Beginner'
            },
            'technical_analysis': {
                'title': 'Technical Analysis Basics',
                'key_concepts': ['Support/Resistance', 'Moving Averages', 'Volume', 'Momentum'],
                'difficulty': 'Intermediate'
            },
            'risk_management': {
                'title': 'Investment Risk Management',
                'key_concepts': ['Diversification', 'Position Sizing', 'Stop Losses', 'Risk Tolerance'],
                'difficulty': 'Essential'
            },
            'market_psychology': {
                'title': 'Market Psychology & Sentiment',
                'key_concepts': ['Market Cycles', 'Fear & Greed', 'Behavioral Biases', 'Contrarian Thinking'],
                'difficulty': 'Advanced'
            }
        }
        
        self.sector_education = {
            'Technology': {
                'key_metrics': ['Revenue per user', 'R&D spending', 'Market share', 'Innovation pipeline'],
                'risk_factors': ['Regulatory changes', 'Competition', 'Technology disruption'],
                'investment_considerations': ['Growth vs profitability', 'Scalability', 'Moats']
            },
            'Healthcare': {
                'key_metrics': ['Pipeline value', 'Patent expiry', 'Clinical trial success rates'],
                'risk_factors': ['Regulatory approval', 'Patent cliffs', 'Healthcare policy'],
                'investment_considerations': ['Long development cycles', 'Binary outcomes', 'Demographics']
            },
            'Financial Services': {
                'key_metrics': ['Net interest margin', 'Credit loss provisions', 'Return on equity'],
                'risk_factors': ['Interest rates', 'Credit cycles', 'Regulation'],
                'investment_considerations': ['Economic sensitivity', 'Capital requirements', 'Digital disruption']
            }
        }
        
        self.investment_concepts = {
            'beginner': [
                'What is a stock?',
                'How stock prices move',
                'Different types of investments',
                'Basic risk and return concepts'
            ],
            'intermediate': [
                'Reading financial statements',
                'Valuation methods',
                'Portfolio diversification',
                'Market cycles and timing'
            ],
            'advanced': [
                'Options and derivatives',
                'Advanced portfolio theory',
                'Alternative investments',
                'Tax optimization strategies'
            ]
        }
    
    def generate_educational_insights(self, stock_data: Dict, analysis_result: Dict) -> Dict:
        """
        Generate educational insights tailored to the specific stock analysis
        Makes every search a learning opportunity
        """
        try:
            insights = {
                'key_learning_points': self._generate_key_learning_points(stock_data, analysis_result),
                'concept_explanations': self._explain_key_concepts(stock_data, analysis_result),
                'sector_education': self._provide_sector_education(stock_data),
                'investment_lessons': self._extract_investment_lessons(stock_data, analysis_result),
                'risk_education': self._explain_risk_concepts(analysis_result),
                'strategy_education': self._explain_strategy_concepts(analysis_result),
                'next_learning_steps': self._suggest_next_learning_steps(stock_data, analysis_result),
                'practical_applications': self._provide_practical_applications(stock_data, analysis_result),
                'common_mistakes': self._highlight_common_mistakes(stock_data, analysis_result)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating educational insights: {e}")
            return self._fallback_educational_content()
    
    def _generate_key_learning_points(self, stock_data: Dict, analysis_result: Dict) -> List[Dict]:
        """Generate key learning points for this analysis"""
        learning_points = []
        
        # Market cap education
        market_cap = stock_data.get('market_cap', 0)
        if market_cap > 0:
            cap_category = self._categorize_market_cap(market_cap)
            learning_points.append({
                'concept': 'Market Capitalization',
                'explanation': f'This is a {cap_category} stock with market cap of ${market_cap/1e9:.1f}B',
                'why_it_matters': f'{cap_category} stocks typically have different risk/return profiles and volatility characteristics',
                'learn_more': 'Market cap = Share Price × Outstanding Shares. It represents the total value investors place on the company.'
            })
        
        # Technical analysis education
        technical_score = analysis_result.get('technical_score', 50)
        learning_points.append({
            'concept': 'Technical Analysis Score',
            'explanation': f'Technical score of {technical_score}/100 indicates {self._interpret_technical_score(technical_score)}',
            'why_it_matters': 'Technical analysis looks at price patterns and trends to predict future movements',
            'learn_more': 'Technical analysis uses charts, indicators, and patterns. It\'s about timing entry and exit points.'
        })
        
        # Fundamental analysis education
        fundamental_score = analysis_result.get('fundamental_score', 50)
        learning_points.append({
            'concept': 'Fundamental Analysis Score',
            'explanation': f'Fundamental score of {fundamental_score}/100 reflects {self._interpret_fundamental_score(fundamental_score)}',
            'why_it_matters': 'Fundamental analysis examines company\'s financial health and intrinsic value',
            'learn_more': 'Fundamentals include revenue, profits, debt, growth rates, and competitive position.'
        })
        
        # Risk education
        risk_level = analysis_result.get('risk_level', 'MEDIUM')
        learning_points.append({
            'concept': 'Investment Risk Assessment',
            'explanation': f'{risk_level} risk means {self._explain_risk_level(risk_level)}',
            'why_it_matters': 'Understanding risk helps you size positions appropriately for your portfolio',
            'learn_more': 'Risk and return are related - higher potential returns usually come with higher risk.'
        })
        
        return learning_points
    
    def _explain_key_concepts(self, stock_data: Dict, analysis_result: Dict) -> Dict:
        """Explain key investment concepts relevant to this analysis"""
        concepts = {}
        
        # Price movement concepts
        price_change = stock_data.get('price_change_percent', 0)
        if abs(price_change) > 2:
            concepts['volatility'] = {
                'definition': 'The degree of variation in a stock\'s price over time',
                'current_example': f'Today\'s {abs(price_change):.1f}% price movement shows {"high" if abs(price_change) > 5 else "moderate"} volatility',
                'investment_impact': 'Higher volatility means more risk but also more potential for gains',
                'practical_tip': 'Volatile stocks require smaller position sizes and closer monitoring'
            }
        
        # Recommendation concepts
        recommendation = analysis_result.get('recommendation', 'HOLD')
        concepts['investment_recommendations'] = {
            'definition': 'Professional opinions on whether to buy, sell, or hold a stock',
            'current_example': f'Current {recommendation} recommendation based on analysis of multiple factors',
            'investment_impact': 'Recommendations provide guidance but should be combined with your own research',
            'practical_tip': 'Never rely solely on recommendations - understand the reasoning behind them'
        }
        
        # Confidence concepts
        confidence = analysis_result.get('confidence', 50)
        concepts['confidence_levels'] = {
            'definition': 'How certain the analysis is about the recommendation',
            'current_example': f'{confidence}% confidence indicates {self._interpret_confidence_level(confidence)}',
            'investment_impact': 'Lower confidence suggests more uncertainty and potential for surprise outcomes',
            'practical_tip': 'Consider reducing position size when confidence is low'
        }
        
        return concepts
    
    def _provide_sector_education(self, stock_data: Dict) -> Dict:
        """Provide sector-specific educational content"""
        sector = stock_data.get('sector', 'Unknown')
        
        if sector in self.sector_education:
            sector_info = self.sector_education[sector]
            return {
                'sector_name': sector,
                'overview': f'Understanding {sector} sector investments',
                'key_metrics_to_watch': sector_info['key_metrics'],
                'common_risk_factors': sector_info['risk_factors'],
                'investment_considerations': sector_info['investment_considerations'],
                'educational_focus': f'When analyzing {sector} stocks, pay special attention to these sector-specific factors'
            }
        else:
            return {
                'sector_name': sector,
                'overview': f'{sector} sector analysis',
                'general_advice': 'Research sector-specific metrics and trends when analyzing any stock',
                'educational_focus': 'Understanding sector dynamics helps contextualize individual stock performance'
            }
    
    def _extract_investment_lessons(self, stock_data: Dict, analysis_result: Dict) -> List[Dict]:
        """Extract practical investment lessons from this analysis"""
        lessons = []
        
        # Strategy impact lesson
        strategy_impact = analysis_result.get('strategy_impact', {})
        if strategy_impact.get('changed', False):
            lessons.append({
                'lesson_title': 'How Investment Strategy Affects Analysis',
                'key_takeaway': 'Different investment approaches can lead to different conclusions about the same stock',
                'practical_example': f'Strategy changed confidence from {strategy_impact.get("original_confidence", 50)}% to {analysis_result.get("confidence", 50)}%',
                'application': 'Define your investment strategy before analyzing stocks to maintain consistency'
            })
        
        # Risk-return lesson
        risk_level = analysis_result.get('risk_level', 'MEDIUM')
        expected_return = self._estimate_expected_return(analysis_result)
        lessons.append({
            'lesson_title': 'Risk-Return Relationship',
            'key_takeaway': f'{risk_level} risk stocks typically offer {expected_return} return potential',
            'practical_example': 'Higher risk doesn\'t guarantee higher returns, but higher returns usually require accepting higher risk',
            'application': 'Match your risk tolerance with appropriate investments'
        })
        
        # Diversification lesson
        sector = stock_data.get('sector', 'Unknown')
        lessons.append({
            'lesson_title': 'Sector Concentration Risk',
            'key_takeaway': f'This {sector} stock adds to your {sector} sector exposure',
            'practical_example': 'Too much concentration in one sector increases portfolio risk',
            'application': 'Spread investments across different sectors for better diversification'
        })
        
        return lessons
    
    def _explain_risk_concepts(self, analysis_result: Dict) -> Dict:
        """Explain risk concepts relevant to this analysis"""
        risk_level = analysis_result.get('risk_level', 'MEDIUM')
        risk_factors = analysis_result.get('risk_factors', [])
        
        return {
            'risk_level_explanation': {
                'current_risk': risk_level,
                'what_it_means': self._explain_risk_level(risk_level),
                'historical_context': self._provide_risk_context(risk_level),
                'portfolio_implications': self._explain_portfolio_risk_impact(risk_level)
            },
            'specific_risk_factors': {
                'identified_risks': risk_factors,
                'risk_education': [
                    'Company-specific risks affect individual stocks',
                    'Market risks affect all investments',
                    'Sector risks affect companies in the same industry'
                ],
                'mitigation_strategies': self._suggest_risk_mitigation_education(risk_factors)
            },
            'risk_management_principles': [
                'Never invest more than you can afford to lose',
                'Diversification reduces but doesn\'t eliminate risk',
                'Understanding risk is as important as understanding returns',
                'Risk tolerance should match your financial situation and goals'
            ]
        }
    
    def _explain_strategy_concepts(self, analysis_result: Dict) -> Dict:
        """Explain investment strategy concepts"""
        strategy_applied = analysis_result.get('strategy_applied', {})
        
        if not strategy_applied:
            return {'note': 'No specific strategy applied to this analysis'}
        
        strategy_name = strategy_applied.get('name', 'Unknown')
        
        strategy_explanations = {
            'Growth Investor': {
                'philosophy': 'Focus on companies with strong growth potential',
                'key_metrics': ['Revenue growth', 'Earnings growth', 'Market expansion'],
                'typical_characteristics': ['Higher P/E ratios', 'Reinvestment of profits', 'Innovation focus'],
                'risk_profile': 'Higher volatility but potential for significant returns',
                'best_for': 'Investors with longer time horizons and higher risk tolerance'
            },
            'Value Investor': {
                'philosophy': 'Buy undervalued companies trading below intrinsic value',
                'key_metrics': ['P/E ratio', 'P/B ratio', 'Dividend yield', 'Free cash flow'],
                'typical_characteristics': ['Lower valuations', 'Established businesses', 'Strong fundamentals'],
                'risk_profile': 'Generally lower volatility with steady returns',
                'best_for': 'Conservative investors seeking steady, long-term wealth building'
            },
            'Dividend Investor': {
                'philosophy': 'Focus on stocks that provide regular income through dividends',
                'key_metrics': ['Dividend yield', 'Payout ratio', 'Dividend growth history'],
                'typical_characteristics': ['Mature companies', 'Stable cash flows', 'Conservative management'],
                'risk_profile': 'Lower volatility with steady income generation',
                'best_for': 'Income-focused investors, retirees, conservative portfolios'
            },
            'Momentum Trader': {
                'philosophy': 'Invest in stocks showing strong price momentum and trends',
                'key_metrics': ['Price momentum', 'Volume trends', 'Technical indicators'],
                'typical_characteristics': ['Recent strong performance', 'High trading volume', 'Market leadership'],
                'risk_profile': 'Higher volatility with potential for quick gains or losses',
                'best_for': 'Active investors comfortable with higher risk and frequent monitoring'
            }
        }
        
        strategy_info = strategy_explanations.get(strategy_name, {})
        
        return {
            'strategy_name': strategy_name,
            'strategy_explanation': strategy_info,
            'how_it_affected_analysis': strategy_applied.get('description', ''),
            'learning_point': f'Different investment strategies emphasize different aspects of stock analysis',
            'practical_application': 'Choose a strategy that matches your goals, timeline, and risk tolerance'
        }
    
    def _suggest_next_learning_steps(self, stock_data: Dict, analysis_result: Dict) -> List[Dict]:
        """Suggest next learning steps based on this analysis"""
        steps = []
        
        # Based on user's apparent knowledge level (inferred from analysis complexity)
        confidence = analysis_result.get('confidence', 50)
        
        if confidence < 60:  # Suggest fundamental learning
            steps.append({
                'step': 'Learn Fundamental Analysis Basics',
                'reason': 'Understanding company fundamentals will help you make more confident investment decisions',
                'specific_topics': ['Reading financial statements', 'Key financial ratios', 'Industry analysis'],
                'time_investment': '2-3 hours of study',
                'practical_exercise': 'Compare this company\'s metrics with 2-3 competitors'
            })
        
        # Technical analysis learning
        technical_score = analysis_result.get('technical_score', 50)
        if technical_score != 50:  # If technical analysis was actually performed
            steps.append({
                'step': 'Understand Technical Analysis',
                'reason': 'Technical analysis helps with timing buy/sell decisions',
                'specific_topics': ['Chart patterns', 'Moving averages', 'Support and resistance'],
                'time_investment': '1-2 hours of study',
                'practical_exercise': 'Practice identifying patterns on stock charts'
            })
        
        # Risk management
        steps.append({
            'step': 'Master Risk Management',
            'reason': 'Protecting capital is as important as growing it',
            'specific_topics': ['Position sizing', 'Stop-loss strategies', 'Portfolio diversification'],
            'time_investment': '1 hour of study',
            'practical_exercise': 'Calculate appropriate position size for your portfolio'
        })
        
        # Sector-specific learning
        sector = stock_data.get('sector', 'Unknown')
        if sector in self.sector_education:
            steps.append({
                'step': f'Deep Dive into {sector} Sector',
                'reason': f'Sector-specific knowledge improves analysis of {sector} stocks',
                'specific_topics': self.sector_education[sector]['key_metrics'][:3],
                'time_investment': '30-45 minutes',
                'practical_exercise': f'Research industry trends affecting {sector} companies'
            })
        
        return steps[:3]  # Limit to top 3 suggestions
    
    def _provide_practical_applications(self, stock_data: Dict, analysis_result: Dict) -> Dict:
        """Provide practical applications of the analysis"""
        return {
            'portfolio_application': {
                'position_sizing': self._suggest_position_sizing(analysis_result),
                'portfolio_fit': self._assess_portfolio_fit(stock_data, analysis_result),
                'timing_considerations': self._provide_timing_guidance(analysis_result)
            },
            'monitoring_plan': {
                'key_metrics_to_watch': self._identify_key_monitoring_metrics(stock_data),
                'review_frequency': self._suggest_review_frequency(analysis_result),
                'exit_criteria': self._suggest_exit_criteria(analysis_result)
            },
            'research_checklist': [
                'Verify the analysis with additional sources',
                'Check recent news and developments',
                'Compare with industry peers',
                'Review your investment thesis',
                'Confirm the investment fits your strategy'
            ]
        }
    
    def _highlight_common_mistakes(self, stock_data: Dict, analysis_result: Dict) -> List[Dict]:
        """Highlight common investment mistakes to avoid"""
        mistakes = []
        
        # Overconfidence mistake
        confidence = analysis_result.get('confidence', 50)
        if confidence > 80:
            mistakes.append({
                'mistake': 'Overconfidence Bias',
                'description': 'Being too certain about investment outcomes',
                'why_it_happens': 'High confidence scores can lead to oversized positions',
                'how_to_avoid': 'Always maintain some uncertainty and use appropriate position sizing',
                'relevant_to_analysis': f'Even with {confidence}% confidence, markets can surprise'
            })
        
        # Sector concentration
        sector = stock_data.get('sector', 'Unknown')
        mistakes.append({
            'mistake': 'Sector Concentration',
            'description': 'Putting too much money in one sector',
            'why_it_happens': f'{sector} stocks might all seem attractive at the same time',
            'how_to_avoid': 'Limit exposure to any single sector to 20-25% of portfolio',
            'relevant_to_analysis': f'Consider your total {sector} exposure before investing'
        })
        
        # Timing the market
        recommendation = analysis_result.get('recommendation', 'HOLD')
        if recommendation in ['BUY', 'SELL']:
            mistakes.append({
                'mistake': 'Trying to Time the Market',
                'description': 'Believing you can predict short-term price movements',
                'why_it_happens': f'{recommendation} recommendations can feel urgent',
                'how_to_avoid': 'Consider dollar-cost averaging for large positions',
                'relevant_to_analysis': 'This analysis is a snapshot - conditions can change quickly'
            })
        
        return mistakes
    
    # Helper methods
    
    def _categorize_market_cap(self, market_cap: float) -> str:
        """Categorize market cap for educational purposes"""
        if market_cap > 200e9:
            return "mega-cap"
        elif market_cap > 10e9:
            return "large-cap"
        elif market_cap > 2e9:
            return "mid-cap"
        elif market_cap > 300e6:
            return "small-cap"
        else:
            return "micro-cap"
    
    def _interpret_technical_score(self, score: float) -> str:
        """Interpret technical score for educational purposes"""
        if score >= 70:
            return "strong bullish technical signals"
        elif score <= 30:
            return "weak technical indicators suggesting caution"
        else:
            return "mixed technical signals"
    
    def _interpret_fundamental_score(self, score: float) -> str:
        """Interpret fundamental score for educational purposes"""
        if score >= 70:
            return "strong company fundamentals"
        elif score <= 30:
            return "concerning fundamental metrics"
        else:
            return "mixed fundamental indicators"
    
    def _explain_risk_level(self, risk_level: str) -> str:
        """Explain risk levels for educational purposes"""
        explanations = {
            'LOW': 'lower volatility and more predictable returns, suitable for conservative investors',
            'MEDIUM': 'moderate volatility with balanced risk-reward profile',
            'HIGH': 'higher volatility requiring careful position sizing and active monitoring'
        }
        return explanations.get(risk_level, 'standard market risk characteristics')
    
    def _interpret_confidence_level(self, confidence: float) -> str:
        """Interpret confidence levels for educational purposes"""
        if confidence >= 80:
            return "high conviction with strong supporting evidence"
        elif confidence >= 60:
            return "moderate confidence with some supporting factors"
        elif confidence >= 40:
            return "low confidence due to mixed signals"
        else:
            return "very low confidence with significant uncertainty"
    
    def _estimate_expected_return(self, analysis_result: Dict) -> str:
        """Estimate expected return category"""
        risk_level = analysis_result.get('risk_level', 'MEDIUM')
        recommendation = analysis_result.get('recommendation', 'HOLD')
        
        if risk_level == 'HIGH' and recommendation == 'BUY':
            return "high"
        elif risk_level == 'LOW':
            return "conservative"
        else:
            return "moderate"
    
    def _provide_risk_context(self, risk_level: str) -> str:
        """Provide historical context for risk levels"""
        contexts = {
            'LOW': 'Historically, low-risk stocks have provided steady returns with occasional periods of underperformance during bull markets',
            'MEDIUM': 'Medium-risk stocks typically balance growth potential with stability, suitable for most investment portfolios',
            'HIGH': 'High-risk stocks can provide substantial returns but also significant losses, requiring careful portfolio management'
        }
        return contexts.get(risk_level, 'Risk characteristics vary with market conditions')
    
    def _explain_portfolio_risk_impact(self, risk_level: str) -> str:
        """Explain how this risk level affects portfolio"""
        impacts = {
            'LOW': 'Reduces overall portfolio volatility and provides stability',
            'MEDIUM': 'Contributes balanced risk-return profile to portfolio',
            'HIGH': 'Increases portfolio volatility but adds growth potential'
        }
        return impacts.get(risk_level, 'Consider position sizing based on total portfolio risk')
    
    def _suggest_risk_mitigation_education(self, risk_factors: List) -> List[str]:
        """Suggest educational content for risk mitigation"""
        return [
            'Learn about stop-loss orders for downside protection',
            'Understand position sizing based on risk tolerance',
            'Study diversification principles',
            'Research hedging strategies for high-risk positions'
        ]
    
    def _suggest_position_sizing(self, analysis_result: Dict) -> str:
        """Suggest position sizing based on analysis"""
        confidence = analysis_result.get('confidence', 50)
        risk_level = analysis_result.get('risk_level', 'MEDIUM')
        
        if confidence >= 70 and risk_level == 'LOW':
            return "Consider standard position size (2-5% of portfolio)"
        elif confidence >= 60 and risk_level == 'MEDIUM':
            return "Consider moderate position size (1-3% of portfolio)"
        else:
            return "Consider small position size (<1% of portfolio) due to uncertainty or high risk"
    
    def _assess_portfolio_fit(self, stock_data: Dict, analysis_result: Dict) -> str:
        """Assess how this stock fits in a portfolio"""
        sector = stock_data.get('sector', 'Unknown')
        risk_level = analysis_result.get('risk_level', 'MEDIUM')
        
        return f"As a {risk_level.lower()}-risk {sector} stock, consider current sector allocation and overall portfolio balance"
    
    def _provide_timing_guidance(self, analysis_result: Dict) -> str:
        """Provide timing guidance"""
        recommendation = analysis_result.get('recommendation', 'HOLD')
        confidence = analysis_result.get('confidence', 50)
        
        if recommendation == 'BUY' and confidence >= 70:
            return "Consider gradual accumulation rather than large immediate purchase"
        elif recommendation == 'SELL':
            return "Consider exit strategy and tax implications"
        else:
            return "No immediate action required - continue monitoring"
    
    def _identify_key_monitoring_metrics(self, stock_data: Dict) -> List[str]:
        """Identify key metrics to monitor"""
        sector = stock_data.get('sector', 'Unknown')
        
        general_metrics = ['Price movement', 'Volume patterns', 'News and developments']
        
        if sector in self.sector_education:
            sector_metrics = self.sector_education[sector]['key_metrics'][:2]
            return general_metrics + sector_metrics
        else:
            return general_metrics + ['Earnings reports', 'Competitive developments']
    
    def _suggest_review_frequency(self, analysis_result: Dict) -> str:
        """Suggest how often to review the investment"""
        risk_level = analysis_result.get('risk_level', 'MEDIUM')
        
        frequencies = {
            'LOW': 'Monthly review sufficient for low-risk holdings',
            'MEDIUM': 'Bi-weekly review recommended',
            'HIGH': 'Weekly or more frequent monitoring for high-risk positions'
        }
        return frequencies.get(risk_level, 'Regular monitoring recommended')
    
    def _suggest_exit_criteria(self, analysis_result: Dict) -> List[str]:
        """Suggest exit criteria"""
        return [
            'Fundamental deterioration in company business',
            'Achievement of price target (if applicable)',
            'Change in investment thesis or strategy',
            'Portfolio rebalancing needs',
            'Better opportunities identified elsewhere'
        ]
    
    def _fallback_educational_content(self) -> Dict:
        """Provide fallback educational content"""
        return {
            'key_learning_points': [
                {
                    'concept': 'Investment Research',
                    'explanation': 'Always research before investing',
                    'why_it_matters': 'Understanding your investments reduces risk',
                    'learn_more': 'Combine multiple analysis methods for better decisions'
                }
            ],
            'note': 'Educational insights temporarily unavailable. Continue learning through practice and research.'
        }

# Initialize the educational engine
educational_insights_engine = EducationalInsightsEngine()

def get_educational_insights(stock_data: Dict, analysis_result: Dict) -> Dict:
    """
    Public interface for getting educational insights
    Our competitive advantage: Learning integrated with analysis
    """
    return educational_insights_engine.generate_educational_insights(stock_data, analysis_result)