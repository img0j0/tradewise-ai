#!/usr/bin/env python3
"""
AI-Powered Paper Trading Automation System
Tests the trading platform during market hours using real-time data
"""

import os
import sys
import time
import json
import logging
import requests
import schedule
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np
from dataclasses import dataclass
import yfinance as yf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paper_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TradingDecision:
    """Represents an AI trading decision"""
    symbol: str
    action: str  # 'buy' or 'sell'
    quantity: int
    confidence: float
    reasoning: str
    timestamp: datetime

class PaperTradingBot:
    """AI-powered paper trading bot that tests the platform"""
    
    def __init__(self, base_url: str = "http://localhost:5000", username: str = "ai_trader"):
        self.base_url = base_url
        self.username = username
        self.password = "ai_trader_2025"
        self.session = requests.Session()
        self.portfolio_value = 10000.0  # Starting with $10,000
        self.trade_history = []
        self.performance_metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_profit_loss': 0.0,
            'best_trade': 0.0,
            'worst_trade': 0.0,
            'win_rate': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0
        }
        self.watchlist = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
        self.is_running = False
        self.market_hours = {
            'open': 9,  # 9 AM EST
            'close': 16  # 4 PM EST
        }
        
    def authenticate(self) -> bool:
        """Authenticate with the trading platform"""
        try:
            # First, try to register the AI trader account
            register_data = {
                'username': self.username,
                'email': f'{self.username}@example.com',
                'password': self.password,
                'confirm_password': self.password
            }
            
            register_response = self.session.post(
                f"{self.base_url}/register",
                data=register_data
            )
            
            # Now login (will work even if registration failed due to existing account)
            login_data = {
                'username': self.username,
                'password': self.password
            }
            
            login_response = self.session.post(
                f"{self.base_url}/login",
                data=login_data
            )
            
            if login_response.status_code == 200:
                logger.info("Successfully authenticated with trading platform")
                return True
            else:
                logger.error(f"Authentication failed: {login_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def is_market_open(self) -> bool:
        """Check if the market is currently open"""
        now = datetime.now()
        weekday = now.weekday()
        hour = now.hour
        
        # Market is closed on weekends
        if weekday >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Market hours: 9 AM to 4 PM EST
        return self.market_hours['open'] <= hour < self.market_hours['close']
    
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """Get real-time market data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if hist.empty:
                return None
                
            current_price = hist['Close'].iloc[-1]
            volume = hist['Volume'].iloc[-1]
            
            return {
                'symbol': symbol,
                'current_price': float(current_price),
                'volume': int(volume),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'change_percent': info.get('regularMarketChangePercent', 0)
            }
            
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return None
    
    def analyze_stock(self, symbol: str) -> Optional[TradingDecision]:
        """AI analysis to make trading decisions"""
        try:
            # Get market data
            market_data = self.get_market_data(symbol)
            if not market_data:
                return None
            
            # Get technical indicators from the platform
            response = self.session.get(f"{self.base_url}/api/technical-indicators/{symbol}")
            if response.status_code != 200:
                logger.warning(f"Could not get technical indicators for {symbol}")
                indicators = {}
            else:
                indicators = response.json()
            
            # Get AI insights from the platform
            response = self.session.get(f"{self.base_url}/api/ai/insights/{symbol}")
            if response.status_code != 200:
                logger.warning(f"Could not get AI insights for {symbol}")
                ai_insights = {}
            else:
                ai_insights = response.json()
            
            # Make trading decision based on multiple factors
            decision = self._make_trading_decision(symbol, market_data, indicators, ai_insights)
            
            if decision:
                logger.info(f"AI Decision for {symbol}: {decision.action} {decision.quantity} shares (confidence: {decision.confidence:.2f})")
                logger.info(f"Reasoning: {decision.reasoning}")
            
            return decision
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def _make_trading_decision(self, symbol: str, market_data: Dict, indicators: Dict, ai_insights: Dict) -> Optional[TradingDecision]:
        """Internal method to make trading decisions using AI logic"""
        try:
            # Extract key metrics
            current_price = market_data['current_price']
            volume = market_data['volume']
            change_percent = market_data.get('change_percent', 0)
            
            # Technical analysis factors
            rsi = indicators.get('rsi', 50)
            macd = indicators.get('macd', {})
            bollinger = indicators.get('bollinger_bands', {})
            
            # AI insights
            ai_recommendation = ai_insights.get('recommendation', 'hold')
            ai_confidence = ai_insights.get('confidence_score', 0.5)
            
            # Decision logic
            buy_signals = 0
            sell_signals = 0
            reasoning_parts = []
            
            # RSI analysis
            if rsi < 30:
                buy_signals += 1
                reasoning_parts.append("RSI oversold")
            elif rsi > 70:
                sell_signals += 1
                reasoning_parts.append("RSI overbought")
            
            # MACD analysis
            if macd.get('signal') == 'bullish':
                buy_signals += 1
                reasoning_parts.append("MACD bullish crossover")
            elif macd.get('signal') == 'bearish':
                sell_signals += 1
                reasoning_parts.append("MACD bearish crossover")
            
            # Volume analysis
            if volume > 1000000:  # High volume
                if change_percent > 0:
                    buy_signals += 1
                    reasoning_parts.append("High volume with positive momentum")
                else:
                    sell_signals += 1
                    reasoning_parts.append("High volume with negative momentum")
            
            # AI recommendation
            if ai_recommendation == 'buy' and ai_confidence > 0.7:
                buy_signals += 2
                reasoning_parts.append(f"Strong AI buy signal (confidence: {ai_confidence:.2f})")
            elif ai_recommendation == 'sell' and ai_confidence > 0.7:
                sell_signals += 2
                reasoning_parts.append(f"Strong AI sell signal (confidence: {ai_confidence:.2f})")
            
            # Make decision
            if buy_signals > sell_signals and buy_signals >= 2:
                # Calculate position size (max 10% of portfolio per trade)
                max_position_value = self.portfolio_value * 0.1
                quantity = int(max_position_value / current_price)
                
                if quantity > 0:
                    confidence = min(0.9, (buy_signals / 5.0) + 0.1)
                    reasoning = "BUY - " + ", ".join(reasoning_parts)
                    
                    return TradingDecision(
                        symbol=symbol,
                        action='buy',
                        quantity=quantity,
                        confidence=confidence,
                        reasoning=reasoning,
                        timestamp=datetime.now()
                    )
            
            elif sell_signals > buy_signals and sell_signals >= 2:
                # Check if we own this stock
                portfolio_response = self.session.get(f"{self.base_url}/api/portfolio")
                if portfolio_response.status_code == 200:
                    portfolio = portfolio_response.json()
                    holding = next((item for item in portfolio if item['symbol'] == symbol), None)
                    
                    if holding and holding['quantity'] > 0:
                        quantity = holding['quantity']
                        confidence = min(0.9, (sell_signals / 5.0) + 0.1)
                        reasoning = "SELL - " + ", ".join(reasoning_parts)
                        
                        return TradingDecision(
                            symbol=symbol,
                            action='sell',
                            quantity=quantity,
                            confidence=confidence,
                            reasoning=reasoning,
                            timestamp=datetime.now()
                        )
            
            return None
            
        except Exception as e:
            logger.error(f"Error making trading decision: {e}")
            return None
    
    def execute_trade(self, decision: TradingDecision) -> bool:
        """Execute a trading decision on the platform"""
        try:
            if decision.action == 'buy':
                # First, search for the stock to get current price
                search_response = self.session.post(
                    f"{self.base_url}/api/search-stock",
                    json={'symbol': decision.symbol}
                )
                
                if search_response.status_code != 200:
                    logger.error(f"Could not search for {decision.symbol}")
                    return False
                
                # Execute buy order
                buy_response = self.session.post(
                    f"{self.base_url}/api/purchase-stock",
                    json={
                        'symbol': decision.symbol,
                        'quantity': decision.quantity
                    }
                )
                
                if buy_response.status_code == 200:
                    result = buy_response.json()
                    logger.info(f"Successfully bought {decision.quantity} shares of {decision.symbol}")
                    self.trade_history.append(decision)
                    self.performance_metrics['total_trades'] += 1
                    return True
                else:
                    logger.error(f"Failed to buy {decision.symbol}: {buy_response.text}")
                    return False
            
            elif decision.action == 'sell':
                # Execute sell order
                sell_response = self.session.post(
                    f"{self.base_url}/api/sell-stock",
                    json={
                        'symbol': decision.symbol,
                        'quantity': decision.quantity
                    }
                )
                
                if sell_response.status_code == 200:
                    result = sell_response.json()
                    logger.info(f"Successfully sold {decision.quantity} shares of {decision.symbol}")
                    self.trade_history.append(decision)
                    self.performance_metrics['total_trades'] += 1
                    return True
                else:
                    logger.error(f"Failed to sell {decision.symbol}: {sell_response.text}")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False
    
    def update_performance_metrics(self):
        """Update performance metrics based on current portfolio"""
        try:
            # Get current portfolio value
            portfolio_response = self.session.get(f"{self.base_url}/api/portfolio")
            if portfolio_response.status_code != 200:
                return
            
            portfolio = portfolio_response.json()
            current_value = 0.0
            
            for holding in portfolio:
                market_data = self.get_market_data(holding['symbol'])
                if market_data:
                    position_value = market_data['current_price'] * holding['quantity']
                    current_value += position_value
            
            # Get account balance
            account_response = self.session.get(f"{self.base_url}/api/account")
            if account_response.status_code == 200:
                account = account_response.json()
                current_value += account.get('balance', 0)
            
            # Calculate performance
            total_return = current_value - self.portfolio_value
            return_percentage = (total_return / self.portfolio_value) * 100
            
            self.performance_metrics['total_profit_loss'] = total_return
            self.performance_metrics['portfolio_value'] = current_value
            self.performance_metrics['return_percentage'] = return_percentage
            
            logger.info(f"Portfolio Value: ${current_value:.2f} (Return: {return_percentage:.2f}%)")
            
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        if not self.is_market_open():
            logger.info("Market is closed. Skipping trading cycle.")
            return
        
        logger.info("Starting trading cycle...")
        
        # Update performance metrics
        self.update_performance_metrics()
        
        # Analyze each stock in watchlist
        for symbol in self.watchlist:
            try:
                decision = self.analyze_stock(symbol)
                if decision:
                    success = self.execute_trade(decision)
                    if success:
                        logger.info(f"Trade executed successfully for {symbol}")
                    else:
                        logger.warning(f"Trade failed for {symbol}")
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error in trading cycle for {symbol}: {e}")
        
        logger.info("Trading cycle completed.")
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive trading report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'performance_metrics': self.performance_metrics,
            'trade_history': [
                {
                    'symbol': trade.symbol,
                    'action': trade.action,
                    'quantity': trade.quantity,
                    'confidence': trade.confidence,
                    'reasoning': trade.reasoning,
                    'timestamp': trade.timestamp.isoformat()
                } for trade in self.trade_history
            ],
            'platform_status': 'operational',
            'market_hours_active': self.is_market_open()
        }
        
        return report
    
    def save_report(self, filename: str = None):
        """Save trading report to file"""
        if not filename:
            filename = f"trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Trading report saved to {filename}")
    
    def start_automation(self):
        """Start the automated trading system"""
        logger.info("Starting AI Paper Trading Automation System")
        
        # Authenticate
        if not self.authenticate():
            logger.error("Failed to authenticate. Exiting.")
            return
        
        # Schedule trading cycles
        schedule.every(15).minutes.do(self.run_trading_cycle)  # Every 15 minutes during market hours
        schedule.every().day.at("16:30").do(self.save_report)  # Daily report after market close
        
        self.is_running = True
        
        # Run initial cycle
        self.run_trading_cycle()
        
        # Main loop
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop_automation(self):
        """Stop the automated trading system"""
        logger.info("Stopping AI Paper Trading Automation System")
        self.is_running = False
        self.save_report()

def main():
    """Main function to run the paper trading bot"""
    # Check if running in deployment environment
    base_url = os.getenv('APP_URL', 'http://localhost:5000')
    
    bot = PaperTradingBot(base_url=base_url)
    
    try:
        bot.start_automation()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        bot.stop_automation()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        bot.stop_automation()

if __name__ == "__main__":
    main()