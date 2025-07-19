import logging
import random
from datetime import datetime
from stock_search import StockSearchService

logger = logging.getLogger(__name__)

class ComprehensiveAIAdvisor:
    """Advanced AI advisor for comprehensive stock analysis"""
    
    def __init__(self):
        self.stock_service = StockSearchService()
        
    def analyze_any_stock(self, symbol):
        """Provide comprehensive analysis for any stock symbol"""
        try:
            # Get comprehensive stock data
            stock_data = self.stock_service.search_stock(symbol)
            if not stock_data:
                return {
                    'success': False,
                    'error': f'Stock symbol {symbol.upper()} not found or invalid'
                }
            
            # Get fundamental data
            fundamentals = self.stock_service.get_stock_fundamentals(symbol)
            
            # Generate comprehensive AI analysis
            analysis = self._generate_comprehensive_analysis(stock_data, fundamentals)
            
            return {
                'success': True,
                'symbol': stock_data['symbol'],
                'company_name': stock_data['name'],
                'sector': stock_data.get('sector', 'Unknown'),
                'industry': stock_data.get('industry', 'Unknown'),
                'country': stock_data.get('country', 'Unknown'),
                'current_price': round(float(stock_data['current_price']), 2),
                'price_change': round(float(stock_data['price_change']), 2),
                'price_change_percent': stock_data['price_change_percent'],
                'market_cap': self._format_market_cap(stock_data.get('market_cap', 0)),
                'volume': self._format_volume(stock_data.get('volume', 0)),
                'pe_ratio': round(float(stock_data.get('pe_ratio', 0)), 2) if stock_data.get('pe_ratio') else None,
                'beta': round(float(stock_data.get('beta', 0)), 2) if stock_data.get('beta') else None,
                'week_52_high': round(float(stock_data.get('week_52_high', 0)), 2) if stock_data.get('week_52_high') else None,
                'week_52_low': round(float(stock_data.get('week_52_low', 0)), 2) if stock_data.get('week_52_low') else None,
                'dividend_yield': stock_data.get('dividend_yield'),
                'ai_analysis': analysis,
                'business_summary': stock_data.get('business_summary', '') if stock_data.get('business_summary', '') else 'No business summary available',
                'website': stock_data.get('website', ''),
                'last_updated': stock_data.get('last_updated')
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis for {symbol}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to analyze {symbol.upper()}: {str(e)}'
            }
    
    def _generate_comprehensive_analysis(self, stock_data, fundamentals):
        """Generate detailed AI-powered stock analysis"""
        try:
            # Technical Analysis
            technical = self._analyze_technical_indicators(stock_data)
            
            # Fundamental Analysis
            fundamental = self._analyze_fundamentals(stock_data, fundamentals)
            
            # Risk Assessment
            risk = self._assess_risk(stock_data, fundamentals)
            
            # Market Position Analysis
            market_position = self._analyze_market_position(stock_data)
            
            # Generate overall recommendation
            recommendation = self._generate_recommendation(technical, fundamental, risk, market_position)
            
            # Generate confidence score
            confidence = self._calculate_confidence(technical, fundamental, risk, stock_data, fundamentals)
            
            # Create comprehensive analysis summary
            analysis_summary = self._create_analysis_summary(
                stock_data, technical, fundamental, risk, market_position, recommendation
            )
            
            return {
                'recommendation': recommendation,
                'confidence': confidence,
                'analysis_summary': analysis_summary,
                'technical_analysis': technical,
                'fundamental_analysis': fundamental,
                'risk_assessment': risk,
                'market_position': market_position,
                'key_metrics': self._extract_key_metrics(stock_data, fundamentals),
                'investment_thesis': self._generate_investment_thesis(stock_data, fundamentals, recommendation)
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analysis: {str(e)}")
            return {
                'recommendation': 'HOLD',
                'confidence': 50,
                'analysis_summary': f"Analysis for {stock_data.get('name', 'this stock')} is currently limited due to data processing issues. Please try again later.",
                'technical_analysis': {},
                'fundamental_analysis': {},
                'risk_assessment': {},
                'market_position': {},
                'key_metrics': {},
                'investment_thesis': 'Insufficient data for detailed investment thesis.'
            }
    
    def _analyze_technical_indicators(self, stock_data):
        """Analyze technical indicators"""
        current_price = stock_data.get('current_price', 0)
        ma_20 = stock_data.get('moving_avg_20', current_price)
        ma_50 = stock_data.get('moving_avg_50', current_price)
        week_52_high = stock_data.get('week_52_high', current_price)
        week_52_low = stock_data.get('week_52_low', current_price)
        volume = stock_data.get('volume', 0)
        avg_volume = stock_data.get('avg_volume', 1)
        
        # Price trend analysis
        trend_signal = 'NEUTRAL'
        if current_price > ma_20 * 1.02 and current_price > ma_50 * 1.02:
            trend_signal = 'BULLISH'
        elif current_price < ma_20 * 0.98 and current_price < ma_50 * 0.98:
            trend_signal = 'BEARISH'
        
        # Volume analysis
        volume_signal = 'NORMAL'
        if avg_volume > 0:
            volume_ratio = volume / avg_volume
            if volume_ratio > 1.5:
                volume_signal = 'HIGH'
            elif volume_ratio < 0.5:
                volume_signal = 'LOW'
        
        # 52-week position
        if week_52_high > week_52_low:
            position_in_range = (current_price - week_52_low) / (week_52_high - week_52_low) * 100
        else:
            position_in_range = 50
        
        return {
            'trend_signal': trend_signal,
            'price_vs_ma20': round((current_price / ma_20 - 1) * 100, 2) if ma_20 > 0 else 0,
            'price_vs_ma50': round((current_price / ma_50 - 1) * 100, 2) if ma_50 > 0 else 0,
            'volume_signal': volume_signal,
            'volume_ratio': round(volume / avg_volume, 2) if avg_volume > 0 else 1,
            '52_week_position': round(position_in_range, 1),
            'support_level': week_52_low,
            'resistance_level': week_52_high
        }
    
    def _analyze_fundamentals(self, stock_data, fundamentals):
        """Analyze fundamental metrics"""
        if not fundamentals:
            return {'status': 'Limited fundamental data available'}
        
        # Valuation metrics
        pe_ratio = stock_data.get('pe_ratio')
        pb_ratio = stock_data.get('price_to_book')
        peg_ratio = fundamentals.get('peg_ratio')
        
        # Profitability metrics
        profit_margin = fundamentals.get('profit_margin')
        roe = fundamentals.get('return_on_equity')
        roa = fundamentals.get('return_on_assets')
        
        # Growth metrics
        revenue_growth = fundamentals.get('revenue_growth')
        earnings_growth = fundamentals.get('earnings_growth')
        
        # Financial health
        debt_to_equity = fundamentals.get('debt_to_equity')
        current_ratio = fundamentals.get('current_ratio')
        
        # Analyst sentiment
        analyst_rating = fundamentals.get('analyst_rating')
        recommendation_key = fundamentals.get('recommendation_key', 'none')
        
        return {
            'valuation_score': self._score_valuation(pe_ratio, pb_ratio, peg_ratio),
            'profitability_score': self._score_profitability(profit_margin, roe, roa),
            'growth_score': self._score_growth(revenue_growth, earnings_growth),
            'financial_health_score': self._score_financial_health(debt_to_equity, current_ratio),
            'analyst_sentiment': self._interpret_analyst_rating(analyst_rating, recommendation_key),
            'key_ratios': {
                'pe_ratio': pe_ratio,
                'price_to_book': pb_ratio,
                'profit_margin': profit_margin,
                'return_on_equity': roe,
                'debt_to_equity': debt_to_equity,
                'current_ratio': current_ratio,
                'revenue_growth': revenue_growth,
                'earnings_growth': earnings_growth
            }
        }
    
    def _assess_risk(self, stock_data, fundamentals):
        """Comprehensive risk assessment"""
        risk_factors = []
        risk_score = 50  # Base risk score
        
        # Volatility risk
        beta = stock_data.get('beta', 1.0)
        if beta and beta > 1.5:
            risk_score += 15
            risk_factors.append(f"High volatility (Beta: {beta:.2f})")
        elif beta and beta < 0.5:
            risk_score -= 10
            risk_factors.append(f"Low volatility (Beta: {beta:.2f})")
        
        # Liquidity risk
        volume = stock_data.get('volume', 0)
        avg_volume = stock_data.get('avg_volume', 1)
        if avg_volume > 0 and volume < avg_volume * 0.3:
            risk_score += 10
            risk_factors.append("Low trading volume")
        
        # Financial health risk
        if fundamentals:
            debt_to_equity = fundamentals.get('debt_to_equity')
            if debt_to_equity and debt_to_equity > 2:
                risk_score += 15
                risk_factors.append(f"High debt-to-equity ratio ({debt_to_equity:.2f})")
            
            current_ratio = fundamentals.get('current_ratio')
            if current_ratio and current_ratio < 1:
                risk_score += 10
                risk_factors.append(f"Poor liquidity (Current ratio: {current_ratio:.2f})")
            
            profit_margin = fundamentals.get('profit_margin')
            if profit_margin and profit_margin < 0:
                risk_score += 20
                risk_factors.append("Negative profit margins")
        
        # Market cap risk
        market_cap = stock_data.get('market_cap', 0)
        if market_cap < 2_000_000_000:  # Small cap
            risk_score += 10
            risk_factors.append("Small-cap volatility risk")
        
        risk_level = self._categorize_risk_level(risk_score)
        
        return {
            'risk_score': max(0, min(100, risk_score)),
            'risk_level': risk_level,
            'risk_factors': risk_factors[:5],  # Top 5 risk factors
            'risk_mitigation': self._suggest_risk_mitigation(risk_factors, risk_level)
        }
    
    def _analyze_market_position(self, stock_data):
        """Analyze stock's market position"""
        current_price = stock_data.get('current_price', 0)
        week_52_high = stock_data.get('week_52_high', current_price)
        week_52_low = stock_data.get('week_52_low', current_price)
        market_cap = stock_data.get('market_cap', 0)
        
        # Market cap category
        if market_cap > 200_000_000_000:
            cap_category = "Mega Cap"
        elif market_cap > 10_000_000_000:
            cap_category = "Large Cap"
        elif market_cap > 2_000_000_000:
            cap_category = "Mid Cap"
        elif market_cap > 300_000_000:
            cap_category = "Small Cap"
        else:
            cap_category = "Micro Cap"
        
        # Price position
        if week_52_high > week_52_low:
            position_pct = (current_price - week_52_low) / (week_52_high - week_52_low) * 100
        else:
            position_pct = 50
        
        position_description = "middle of range"
        if position_pct > 80:
            position_description = "near 52-week high"
        elif position_pct < 20:
            position_description = "near 52-week low"
        
        return {
            'market_cap_category': cap_category,
            'market_cap_formatted': self._format_market_cap(market_cap),
            '52_week_position_pct': round(position_pct, 1),
            'position_description': position_description,
            'momentum': self._calculate_momentum(stock_data)
        }
    
    def _generate_recommendation(self, technical, fundamental, risk, market_position):
        """Generate overall investment recommendation"""
        score = 0
        
        # Technical score
        if technical.get('trend_signal') == 'BULLISH':
            score += 2
        elif technical.get('trend_signal') == 'BEARISH':
            score -= 2
        
        if technical.get('volume_signal') == 'HIGH':
            score += 1
        
        # Fundamental score
        fund_scores = fundamental.get('valuation_score', 0) + fundamental.get('profitability_score', 0) + \
                     fundamental.get('growth_score', 0) + fundamental.get('financial_health_score', 0)
        score += fund_scores / 20  # Normalize to -2 to +2 range
        
        # Risk adjustment
        risk_score = risk.get('risk_score', 50)
        if risk_score > 70:
            score -= 2
        elif risk_score < 30:
            score += 1
        
        # Generate recommendation
        if score > 2:
            return 'STRONG BUY'
        elif score > 0.5:
            return 'BUY'
        elif score > -0.5:
            return 'HOLD'
        elif score > -2:
            return 'SELL'
        else:
            return 'STRONG SELL'
    
    def _calculate_confidence(self, technical, fundamental, risk, stock_data, fundamentals):
        """Calculate confidence score for the recommendation"""
        confidence = 50
        
        # Data availability boosts confidence
        if stock_data.get('pe_ratio'):
            confidence += 5
        if stock_data.get('beta'):
            confidence += 5
        if fundamentals and fundamentals.get('profit_margin') is not None:
            confidence += 10
        if fundamentals and fundamentals.get('debt_to_equity') is not None:
            confidence += 5
        
        # Clear signals boost confidence
        if technical.get('trend_signal') in ['BULLISH', 'BEARISH']:
            confidence += 10
        if technical.get('volume_signal') == 'HIGH':
            confidence += 5
        
        # Risk clarity
        risk_factors = len(risk.get('risk_factors', []))
        if risk_factors > 3:
            confidence += 5
        
        return max(30, min(95, confidence))
    
    def _create_analysis_summary(self, stock_data, technical, fundamental, risk, market_position, recommendation):
        """Create human-readable analysis summary"""
        company_name = stock_data.get('name', 'This company')
        current_price = stock_data.get('current_price', 0)
        change_pct = stock_data.get('price_change_percent', 0)
        sector = stock_data.get('sector', 'Unknown sector')
        
        # Price movement description
        if change_pct > 2:
            price_desc = f"up {change_pct:.1f}% today"
        elif change_pct < -2:
            price_desc = f"down {abs(change_pct):.1f}% today"
        else:
            sign = "+" if change_pct >= 0 else ""
            price_desc = f"relatively stable ({sign}{change_pct:.1f}%)"
        
        # Technical summary
        trend = technical.get('trend_signal', 'NEUTRAL')
        trend_desc = trend.lower().replace('_', ' ')
        
        # Risk summary
        risk_level = risk.get('risk_level', 'Moderate').lower()
        
        # Market position
        cap_category = market_position.get('market_cap_category', 'Unknown cap')
        position_desc = market_position.get('position_description', 'middle of range')
        
        summary = f"{company_name} ({sector}) is trading at ${current_price:.2f}, {price_desc}. "
        summary += f"Technical indicators suggest a {trend_desc} trend. "
        summary += f"The stock is currently {position_desc} in its 52-week range. "
        summary += f"This {cap_category.lower()} stock carries {risk_level} investment risk. "
        
        # Add recommendation context
        rec_context = {
            'STRONG BUY': "showing exceptional strength across multiple indicators",
            'BUY': "displaying positive momentum and attractive fundamentals", 
            'HOLD': "presenting mixed signals requiring careful monitoring",
            'SELL': "showing concerning trends that warrant caution",
            'STRONG SELL': "displaying significant weakness across key metrics"
        }
        
        summary += f"Our AI analysis recommends {recommendation}, {rec_context.get(recommendation, 'based on current market conditions')}."
        
        return summary
    
    # Helper methods for scoring and formatting
    def _score_valuation(self, pe, pb, peg):
        """Score valuation metrics (-10 to +10)"""
        score = 0
        if pe:
            if pe < 15:
                score += 3
            elif pe > 30:
                score -= 3
        if pb:
            if pb < 1.5:
                score += 2
            elif pb > 3:
                score -= 2
        if peg:
            if peg < 1:
                score += 3
            elif peg > 2:
                score -= 3
        return max(-10, min(10, score))
    
    def _score_profitability(self, margin, roe, roa):
        """Score profitability metrics"""
        score = 0
        if margin:
            if margin > 0.2:
                score += 3
            elif margin < 0:
                score -= 5
        if roe:
            if roe > 0.15:
                score += 3
            elif roe < 0:
                score -= 3
        return max(-10, min(10, score))
    
    def _score_growth(self, rev_growth, earnings_growth):
        """Score growth metrics"""
        score = 0
        if rev_growth:
            if rev_growth > 0.1:
                score += 3
            elif rev_growth < -0.05:
                score -= 3
        if earnings_growth:
            if earnings_growth > 0.1:
                score += 3
            elif earnings_growth < -0.1:
                score -= 3
        return max(-10, min(10, score))
    
    def _score_financial_health(self, debt_eq, current_ratio):
        """Score financial health"""
        score = 0
        if debt_eq is not None:
            if debt_eq < 0.5:
                score += 3
            elif debt_eq > 2:
                score -= 3
        if current_ratio:
            if current_ratio > 2:
                score += 2
            elif current_ratio < 1:
                score -= 3
        return max(-10, min(10, score))
    
    def _interpret_analyst_rating(self, rating, key):
        """Interpret analyst ratings"""
        if not rating:
            return "No analyst coverage"
        if rating <= 2:
            return "Strong Buy consensus"
        elif rating <= 2.5:
            return "Buy consensus"
        elif rating <= 3.5:
            return "Hold consensus"
        elif rating <= 4.5:
            return "Sell consensus"
        else:
            return "Strong Sell consensus"
    
    def _categorize_risk_level(self, risk_score):
        """Categorize risk level"""
        if risk_score < 25:
            return "Very Low"
        elif risk_score < 40:
            return "Low"
        elif risk_score < 60:
            return "Moderate"
        elif risk_score < 75:
            return "High"
        else:
            return "Very High"
    
    def _suggest_risk_mitigation(self, risk_factors, risk_level):
        """Suggest risk mitigation strategies"""
        if risk_level in ["Very High", "High"]:
            return "Consider position sizing carefully, use stop-losses, and diversify holdings"
        elif risk_level == "Moderate":
            return "Monitor key fundamentals and maintain balanced position size"
        else:
            return "Standard portfolio management practices apply"
    
    def _calculate_momentum(self, stock_data):
        """Calculate price momentum"""
        current = stock_data.get('current_price', 0)
        ma_20 = stock_data.get('moving_avg_20', current)
        if ma_20 > 0:
            momentum = (current / ma_20 - 1) * 100
            if momentum > 5:
                return "Strong Positive"
            elif momentum > 0:
                return "Positive"
            elif momentum > -5:
                return "Negative"
            else:
                return "Strong Negative"
        return "Neutral"
    
    def _extract_key_metrics(self, stock_data, fundamentals):
        """Extract key metrics for quick reference"""
        metrics = {}
        
        # Price metrics
        metrics['current_price'] = stock_data.get('current_price')
        metrics['market_cap'] = self._format_market_cap(stock_data.get('market_cap', 0))
        metrics['pe_ratio'] = stock_data.get('pe_ratio')
        metrics['beta'] = stock_data.get('beta')
        
        # Fundamental metrics
        if fundamentals:
            metrics['profit_margin'] = fundamentals.get('profit_margin')
            metrics['roe'] = fundamentals.get('return_on_equity')
            metrics['debt_to_equity'] = fundamentals.get('debt_to_equity')
            metrics['revenue_growth'] = fundamentals.get('revenue_growth')
        
        return {k: v for k, v in metrics.items() if v is not None}
    
    def _generate_investment_thesis(self, stock_data, fundamentals, recommendation):
        """Generate investment thesis"""
        company = stock_data.get('name', 'This company')
        sector = stock_data.get('sector', 'its sector')
        
        thesis_templates = {
            'STRONG BUY': f"{company} presents a compelling investment opportunity in {sector} with strong fundamentals, positive technical momentum, and attractive valuation metrics.",
            'BUY': f"{company} offers good investment potential with solid fundamentals and favorable market positioning in {sector}.",
            'HOLD': f"{company} maintains stable operations in {sector} but shows mixed signals requiring careful monitoring of key developments.",
            'SELL': f"{company} faces headwinds in {sector} with concerning fundamental trends that may pressure performance.",
            'STRONG SELL': f"{company} exhibits significant risks across multiple metrics, suggesting investors should avoid or exit positions."
        }
        
        return thesis_templates.get(recommendation, f"Investment thesis for {company} requires further analysis of current market conditions.")
    
    def _format_market_cap(self, market_cap):
        """Format market cap for display"""
        if market_cap >= 1_000_000_000_000:
            return f"${market_cap/1_000_000_000_000:.2f}T"
        elif market_cap >= 1_000_000_000:
            return f"${market_cap/1_000_000_000:.2f}B"
        elif market_cap >= 1_000_000:
            return f"${market_cap/1_000_000:.2f}M"
        else:
            return f"${market_cap:,.0f}"
    
    def _format_volume(self, volume):
        """Format volume for display"""
        if volume >= 1_000_000_000:
            return f"{volume/1_000_000_000:.2f}B"
        elif volume >= 1_000_000:
            return f"{volume/1_000_000:.2f}M"
        elif volume >= 1_000:
            return f"{volume/1_000:.2f}K"
        else:
            return f"{volume:,}"

# Global instance
comprehensive_advisor = ComprehensiveAIAdvisor()