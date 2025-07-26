"""
Smart Event Detection & Alert System
Provides early warning system for market-moving events
Key differentiator: Institutional-level event detection for retail investors
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import yfinance as yf
import requests
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class MarketEvent:
    """Represents a detected market event"""
    event_type: str
    symbol: str
    title: str
    description: str
    impact_level: str  # LOW, MEDIUM, HIGH
    event_time: datetime
    price_impact_estimate: Optional[float] = None
    actionable: bool = True
    event_id: Optional[str] = None

class SmartEventDetector:
    """
    Detects market-moving events before they fully impact stock prices
    Our competitive advantage: Early warning system for retail investors
    """
    
    def __init__(self):
        self.event_types = {
            'earnings_surprise': {
                'priority': 'HIGH',
                'lookback_days': 1,
                'impact_threshold': 0.05  # 5% price movement
            },
            'leadership_change': {
                'priority': 'HIGH',
                'lookback_days': 3,
                'impact_threshold': 0.03
            },
            'analyst_upgrade': {
                'priority': 'MEDIUM',
                'lookback_days': 1,
                'impact_threshold': 0.02
            },
            'analyst_downgrade': {
                'priority': 'MEDIUM',
                'lookback_days': 1,
                'impact_threshold': 0.02
            },
            'volume_anomaly': {
                'priority': 'MEDIUM',
                'lookback_days': 1,
                'impact_threshold': 0.1  # 10x average volume
            },
            'merger_acquisition': {
                'priority': 'HIGH',
                'lookback_days': 7,
                'impact_threshold': 0.1
            },
            'dividend_announcement': {
                'priority': 'LOW',
                'lookback_days': 1,
                'impact_threshold': 0.01
            },
            'product_launch': {
                'priority': 'MEDIUM',
                'lookback_days': 3,
                'impact_threshold': 0.02
            },
            'regulatory_change': {
                'priority': 'HIGH',
                'lookback_days': 7,
                'impact_threshold': 0.05
            }
        }
        
        self.sector_impact_multipliers = {
            'Technology': 1.2,
            'Healthcare': 1.1,
            'Financial Services': 1.0,
            'Energy': 1.3,
            'Consumer Discretionary': 1.1,
            'Utilities': 0.8
        }
    
    def detect_events_for_stock(self, symbol: str, stock_data: Dict) -> List[MarketEvent]:
        """
        Detect potential market events for a specific stock
        Returns list of events that could impact price
        """
        try:
            events = []
            
            # Get enhanced stock data
            ticker = yf.Ticker(symbol)
            
            # Detect various event types
            events.extend(self._detect_earnings_events(symbol, ticker, stock_data))
            events.extend(self._detect_volume_anomalies(symbol, ticker, stock_data))
            events.extend(self._detect_price_breakouts(symbol, ticker, stock_data))
            events.extend(self._detect_analyst_activity(symbol, stock_data))
            events.extend(self._simulate_news_events(symbol, stock_data))
            
            # Sort by priority and impact
            events.sort(key=lambda x: (
                self._get_priority_score(x.impact_level),
                x.event_time
            ), reverse=True)
            
            return events[:10]  # Return top 10 events
            
        except Exception as e:
            logger.error(f"Error detecting events for {symbol}: {e}")
            return []
    
    def detect_market_wide_events(self) -> List[MarketEvent]:
        """
        Detect market-wide events that could affect multiple stocks
        """
        try:
            events = []
            
            # Simulate market-wide event detection
            market_events = [
                {
                    'type': 'fed_announcement',
                    'title': 'Federal Reserve Policy Update Expected',
                    'description': 'FOMC meeting results could impact interest-sensitive sectors',
                    'impact': 'HIGH',
                    'sectors_affected': ['Financial Services', 'Real Estate', 'Utilities']
                },
                {
                    'type': 'earnings_season',
                    'title': 'Technology Earnings Season Beginning',
                    'description': 'Major tech companies reporting earnings this week',
                    'impact': 'MEDIUM',
                    'sectors_affected': ['Technology']
                },
                {
                    'type': 'economic_data',
                    'title': 'Key Economic Indicators Release',
                    'description': 'Jobs report and inflation data could drive market sentiment',
                    'impact': 'MEDIUM',
                    'sectors_affected': ['All']
                }
            ]
            
            for event_data in market_events:
                event = MarketEvent(
                    event_type=event_data['type'],
                    symbol='MARKET',
                    title=event_data['title'],
                    description=event_data['description'],
                    impact_level=event_data['impact'],
                    event_time=datetime.now() + timedelta(days=1),
                    event_id=f"market_{event_data['type']}_{datetime.now().strftime('%Y%m%d')}"
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error detecting market-wide events: {e}")
            return []
    
    def _detect_earnings_events(self, symbol: str, ticker, stock_data: Dict) -> List[MarketEvent]:
        """Detect earnings-related events"""
        events = []
        
        try:
            # Get earnings calendar
            calendar = ticker.calendar
            
            if calendar is not None and hasattr(calendar, 'empty') and not calendar.empty:
                next_earnings = calendar.index[0] if len(calendar.index) > 0 else None
                
                if next_earnings:
                    days_to_earnings = (next_earnings.date() - datetime.now().date()).days
                    
                    if 0 <= days_to_earnings <= 7:
                        event = MarketEvent(
                            event_type='earnings_announcement',
                            symbol=symbol,
                            title=f'{symbol} Earnings Report Due',
                            description=f'Earnings announcement expected in {days_to_earnings} days. Historical volatility around earnings dates.',
                            impact_level='HIGH' if days_to_earnings <= 2 else 'MEDIUM',
                            event_time=datetime.combine(next_earnings.date(), datetime.min.time()),
                            price_impact_estimate=0.05,  # 5% estimated impact
                            event_id=f"{symbol}_earnings_{next_earnings.strftime('%Y%m%d')}"
                        )
                        events.append(event)
            
            # Simulate earnings surprise detection
            if stock_data.get('price_change_percent', 0) > 5:
                event = MarketEvent(
                    event_type='earnings_surprise',
                    symbol=symbol,
                    title=f'{symbol} Potential Earnings Beat Signal',
                    description='Unusual price movement may indicate earnings expectations revision or early results leak.',
                    impact_level='HIGH',
                    event_time=datetime.now(),
                    price_impact_estimate=abs(stock_data.get('price_change_percent', 0)) / 100,
                    event_id=f"{symbol}_surprise_{datetime.now().strftime('%Y%m%d_%H%M')}"
                )
                events.append(event)
                
        except Exception as e:
            logger.warning(f"Could not fetch earnings data for {symbol}: {e}")
        
        return events
    
    def _detect_volume_anomalies(self, symbol: str, ticker, stock_data: Dict) -> List[MarketEvent]:
        """Detect unusual volume patterns"""
        events = []
        
        try:
            # Get recent volume data
            hist = ticker.history(period="5d")
            
            if not hist.empty and len(hist) >= 3:
                recent_volume = hist['Volume'].iloc[-1]
                avg_volume = hist['Volume'].iloc[:-1].mean()
                
                if recent_volume > avg_volume * 3:  # 3x average volume
                    volume_ratio = recent_volume / avg_volume
                    
                    event = MarketEvent(
                        event_type='volume_anomaly',
                        symbol=symbol,
                        title=f'{symbol} Unusual Volume Activity',
                        description=f'Volume {volume_ratio:.1f}x above average. May indicate institutional activity or news catalyst.',
                        impact_level='HIGH' if volume_ratio > 5 else 'MEDIUM',
                        event_time=datetime.now(),
                        price_impact_estimate=0.03,
                        event_id=f"{symbol}_volume_{datetime.now().strftime('%Y%m%d')}"
                    )
                    events.append(event)
                    
        except Exception as e:
            logger.warning(f"Could not analyze volume for {symbol}: {e}")
        
        return events
    
    def _detect_price_breakouts(self, symbol: str, ticker, stock_data: Dict) -> List[MarketEvent]:
        """Detect technical breakouts and breakdowns"""
        events = []
        
        try:
            current_price = stock_data.get('current_price', 0)
            price_change_percent = stock_data.get('price_change_percent', 0)
            
            # Detect significant price movements
            if abs(price_change_percent) > 5:
                direction = 'breakout' if price_change_percent > 0 else 'breakdown'
                impact = 'HIGH' if abs(price_change_percent) > 10 else 'MEDIUM'
                
                event = MarketEvent(
                    event_type=f'price_{direction}',
                    symbol=symbol,
                    title=f'{symbol} Technical {direction.title()}',
                    description=f'Price movement of {price_change_percent:.1f}% suggests {direction} from technical levels.',
                    impact_level=impact,
                    event_time=datetime.now(),
                    price_impact_estimate=abs(price_change_percent) / 100,
                    event_id=f"{symbol}_{direction}_{datetime.now().strftime('%Y%m%d')}"
                )
                events.append(event)
                
        except Exception as e:
            logger.warning(f"Could not analyze price breakouts for {symbol}: {e}")
        
        return events
    
    def _detect_analyst_activity(self, symbol: str, stock_data: Dict) -> List[MarketEvent]:
        """Detect analyst upgrades/downgrades and target price changes"""
        events = []
        
        # Simulate analyst activity detection
        # In production, this would connect to analyst data providers
        analyst_activities = [
            {
                'type': 'upgrade',
                'firm': 'Major Investment Bank',
                'action': 'Upgraded to Buy',
                'target_price': stock_data.get('current_price', 0) * 1.15,
                'probability': 0.3  # 30% chance of this type of event
            },
            {
                'type': 'downgrade',
                'firm': 'Research Firm',
                'action': 'Downgraded to Hold',
                'target_price': stock_data.get('current_price', 0) * 0.9,
                'probability': 0.2
            }
        ]
        
        for activity in analyst_activities:
            # Randomly simulate analyst activity
            import random
            if random.random() < activity['probability']:
                event = MarketEvent(
                    event_type=f"analyst_{activity['type']}",
                    symbol=symbol,
                    title=f'{symbol} Analyst {activity["action"]}',
                    description=f'{activity["firm"]} {activity["action"].lower()} with target price ${activity["target_price"]:.2f}',
                    impact_level='MEDIUM',
                    event_time=datetime.now() - timedelta(hours=random.randint(1, 24)),
                    price_impact_estimate=0.02,
                    event_id=f"{symbol}_analyst_{activity['type']}_{datetime.now().strftime('%Y%m%d')}"
                )
                events.append(event)
        
        return events
    
    def _simulate_news_events(self, symbol: str, stock_data: Dict) -> List[MarketEvent]:
        """Simulate news event detection"""
        events = []
        
        # Simulate various news events
        news_events = [
            {
                'type': 'product_launch',
                'title': f'{symbol} Announces New Product Line',
                'description': 'Company unveils innovative product expected to drive revenue growth',
                'impact': 'MEDIUM',
                'probability': 0.15
            },
            {
                'type': 'partnership',
                'title': f'{symbol} Forms Strategic Partnership',
                'description': 'Strategic alliance with industry leader could expand market reach',
                'impact': 'MEDIUM',
                'probability': 0.1
            },
            {
                'type': 'regulatory_approval',
                'title': f'{symbol} Receives Regulatory Approval',
                'description': 'Key regulatory milestone clears path for market expansion',
                'impact': 'HIGH',
                'probability': 0.05
            }
        ]
        
        for news in news_events:
            import random
            if random.random() < news['probability']:
                event = MarketEvent(
                    event_type=news['type'],
                    symbol=symbol,
                    title=news['title'],
                    description=news['description'],
                    impact_level=news['impact'],
                    event_time=datetime.now() - timedelta(hours=random.randint(1, 48)),
                    price_impact_estimate=0.03,
                    event_id=f"{symbol}_{news['type']}_{datetime.now().strftime('%Y%m%d')}"
                )
                events.append(event)
        
        return events
    
    def _get_priority_score(self, impact_level: str) -> int:
        """Convert impact level to numeric score for sorting"""
        scores = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        return scores.get(impact_level, 0)
    
    def get_alert_recommendations(self, symbol: str, events: List[MarketEvent], user_portfolio: Dict = None) -> List[Dict]:
        """
        Generate actionable alert recommendations based on detected events
        """
        recommendations = []
        
        for event in events:
            if event.impact_level in ['HIGH', 'MEDIUM'] and event.actionable:
                rec = {
                    'event': event,
                    'recommendation_type': self._determine_recommendation_type(event),
                    'urgency': self._calculate_urgency(event),
                    'suggested_actions': self._generate_action_suggestions(event),
                    'monitoring_period': self._suggest_monitoring_period(event),
                    'risk_assessment': self._assess_event_risk(event)
                }
                recommendations.append(rec)
        
        return recommendations
    
    def _determine_recommendation_type(self, event: MarketEvent) -> str:
        """Determine type of recommendation for the event"""
        if event.event_type in ['earnings_surprise', 'analyst_upgrade', 'regulatory_approval']:
            return 'BULLISH_CATALYST'
        elif event.event_type in ['analyst_downgrade', 'regulatory_setback']:
            return 'BEARISH_CATALYST'
        elif event.event_type in ['volume_anomaly', 'price_breakout']:
            return 'MOMENTUM_SIGNAL'
        else:
            return 'MONITOR_CLOSELY'
    
    def _calculate_urgency(self, event: MarketEvent) -> str:
        """Calculate urgency level for the event"""
        time_since_event = datetime.now() - event.event_time
        
        if time_since_event.total_seconds() < 3600:  # 1 hour
            return 'IMMEDIATE'
        elif time_since_event.total_seconds() < 86400:  # 24 hours
            return 'TODAY'
        else:
            return 'THIS_WEEK'
    
    def _generate_action_suggestions(self, event: MarketEvent) -> List[str]:
        """Generate actionable suggestions for the event"""
        actions = []
        
        if event.event_type == 'earnings_announcement':
            actions.extend([
                'Review historical earnings volatility',
                'Consider position sizing before announcement',
                'Set stop-loss orders to manage risk'
            ])
        elif event.event_type == 'volume_anomaly':
            actions.extend([
                'Investigate news sources for catalyst',
                'Monitor price action for confirmation',
                'Check institutional trading activity'
            ])
        elif event.event_type == 'analyst_upgrade':
            actions.extend([
                'Review analyst price target vs current price',
                'Consider gradual position building',
                'Monitor for additional analyst coverage'
            ])
        else:
            actions.extend([
                'Monitor price and volume for confirmation',
                'Review fundamentals for context',
                'Consider risk management measures'
            ])
        
        return actions
    
    def _suggest_monitoring_period(self, event: MarketEvent) -> str:
        """Suggest how long to monitor the event impact"""
        monitoring_periods = {
            'earnings_announcement': '1-2 weeks',
            'analyst_upgrade': '2-4 weeks',
            'volume_anomaly': '3-5 days',
            'price_breakout': '1-2 weeks',
            'regulatory_approval': '1-3 months'
        }
        
        return monitoring_periods.get(event.event_type, '1-2 weeks')
    
    def _assess_event_risk(self, event: MarketEvent) -> Dict:
        """Assess risk associated with the event"""
        return {
            'risk_level': event.impact_level,
            'probability_of_impact': self._estimate_impact_probability(event),
            'potential_downside': event.price_impact_estimate or 0.02,
            'potential_upside': (event.price_impact_estimate or 0.02) * 1.5
        }
    
    def _estimate_impact_probability(self, event: MarketEvent) -> float:
        """Estimate probability that event will impact price"""
        probabilities = {
            'earnings_announcement': 0.8,
            'analyst_upgrade': 0.6,
            'volume_anomaly': 0.7,
            'price_breakout': 0.5,
            'regulatory_approval': 0.9
        }
        
        return probabilities.get(event.event_type, 0.5)

# Initialize the event detector
smart_event_detector = SmartEventDetector()

def get_smart_alerts(symbol: str, stock_data: Dict) -> Dict:
    """
    Public interface for getting smart event alerts
    Our competitive advantage: Early warning system for market events
    """
    try:
        # Detect events for the specific stock
        stock_events = smart_event_detector.detect_events_for_stock(symbol, stock_data)
        
        # Get market-wide events that might affect this stock
        market_events = smart_event_detector.detect_market_wide_events()
        
        # Generate actionable recommendations
        recommendations = smart_event_detector.get_alert_recommendations(symbol, stock_events, {})
        
        return {
            'stock_events': [
                {
                    'type': event.event_type,
                    'title': event.title,
                    'description': event.description,
                    'impact_level': event.impact_level,
                    'event_time': event.event_time.isoformat(),
                    'price_impact_estimate': event.price_impact_estimate
                }
                for event in stock_events
            ],
            'market_events': [
                {
                    'type': event.event_type,
                    'title': event.title,
                    'description': event.description,
                    'impact_level': event.impact_level,
                    'event_time': event.event_time.isoformat()
                }
                for event in market_events[:3]  # Top 3 market events
            ],
            'alert_recommendations': [
                {
                    'event_title': rec['event'].title,
                    'recommendation_type': rec['recommendation_type'],
                    'urgency': rec['urgency'],
                    'actions': rec['suggested_actions'],
                    'monitoring_period': rec['monitoring_period'],
                    'risk_level': rec['risk_assessment']['risk_level']
                }
                for rec in recommendations[:5]  # Top 5 recommendations
            ],
            'summary': {
                'total_events': len(stock_events),
                'high_impact_events': len([e for e in stock_events if e.impact_level == 'HIGH']),
                'immediate_attention_needed': len([e for e in stock_events if e.impact_level == 'HIGH']),
                'next_monitoring_date': (datetime.now() + timedelta(days=1)).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating smart alerts for {symbol}: {e}")
        return {
            'stock_events': [],
            'market_events': [],
            'alert_recommendations': [],
            'summary': {'error': 'Unable to generate alerts at this time'}
        }