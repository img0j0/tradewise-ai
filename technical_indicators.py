"""
Technical indicators for advanced charting
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import yfinance as yf

class TechnicalIndicators:
    """Calculate various technical indicators for stocks"""
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return []
        
        sma = []
        for i in range(period - 1, len(prices)):
            avg = sum(prices[i - period + 1:i + 1]) / period
            sma.append(avg)
        
        return sma
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = [sum(prices[:period]) / period]  # First EMA is SMA
        
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return []
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        rsi_values = []
        
        for i in range(period, len(gains)):
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            rsi_values.append(rsi)
            
            # Update averages
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        return rsi_values
    
    @staticmethod
    def calculate_macd(prices: List[float]) -> Dict[str, List[float]]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        if len(prices) < 26:
            return {'macd': [], 'signal': [], 'histogram': []}
        
        # Calculate EMAs
        ema_12 = TechnicalIndicators.calculate_ema(prices, 12)
        ema_26 = TechnicalIndicators.calculate_ema(prices, 26)
        
        # MACD line
        macd = []
        for i in range(len(ema_26)):
            macd.append(ema_12[i + 14] - ema_26[i])
        
        # Signal line (9-day EMA of MACD)
        signal = TechnicalIndicators.calculate_ema(macd, 9) if len(macd) >= 9 else []
        
        # MACD histogram
        histogram = []
        for i in range(len(signal)):
            histogram.append(macd[i + 8] - signal[i])
        
        return {
            'macd': macd,
            'signal': signal,
            'histogram': histogram
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict[str, List[float]]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {'upper': [], 'middle': [], 'lower': []}
        
        sma = TechnicalIndicators.calculate_sma(prices, period)
        
        upper_band = []
        lower_band = []
        
        for i in range(len(sma)):
            # Calculate standard deviation
            start_idx = i
            end_idx = i + period
            price_slice = prices[start_idx:end_idx]
            std = np.std(price_slice)
            
            upper_band.append(sma[i] + (std_dev * std))
            lower_band.append(sma[i] - (std_dev * std))
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    
    @staticmethod
    def calculate_volume_indicators(volumes: List[float], prices: List[float]) -> Dict[str, List[float]]:
        """Calculate volume-based indicators"""
        if len(volumes) < 20 or len(prices) < 20:
            return {'obv': [], 'vwap': []}
        
        # On-Balance Volume (OBV)
        obv = [volumes[0]]
        for i in range(1, len(volumes)):
            if prices[i] > prices[i-1]:
                obv.append(obv[-1] + volumes[i])
            elif prices[i] < prices[i-1]:
                obv.append(obv[-1] - volumes[i])
            else:
                obv.append(obv[-1])
        
        # Volume Weighted Average Price (VWAP)
        vwap = []
        cumulative_volume = 0
        cumulative_pv = 0
        
        for i in range(len(prices)):
            cumulative_volume += volumes[i]
            cumulative_pv += prices[i] * volumes[i]
            
            if cumulative_volume > 0:
                vwap.append(cumulative_pv / cumulative_volume)
            else:
                vwap.append(prices[i])
        
        return {
            'obv': obv,
            'vwap': vwap
        }
    
    @staticmethod
    def identify_support_resistance(prices: List[float], window: int = 20) -> Dict[str, List[float]]:
        """Identify support and resistance levels"""
        if len(prices) < window * 2:
            return {'support': [], 'resistance': []}
        
        support_levels = []
        resistance_levels = []
        
        for i in range(window, len(prices) - window):
            # Check if it's a local minimum (support)
            if all(prices[i] <= prices[j] for j in range(i - window, i + window + 1)):
                support_levels.append(prices[i])
            
            # Check if it's a local maximum (resistance)
            if all(prices[i] >= prices[j] for j in range(i - window, i + window + 1)):
                resistance_levels.append(prices[i])
        
        # Remove duplicates and sort
        support_levels = sorted(list(set(support_levels)))
        resistance_levels = sorted(list(set(resistance_levels)), reverse=True)
        
        return {
            'support': support_levels[:5],  # Top 5 support levels
            'resistance': resistance_levels[:5]  # Top 5 resistance levels
        }
    
    @staticmethod
    def get_all_indicators(symbol: str, period: str = '3mo') -> Dict:
        """Get all technical indicators for a symbol"""
        try:
            # Fetch historical data
            stock = yf.Ticker(symbol)
            hist = stock.history(period=period)
            
            if hist.empty:
                return {}
            
            prices = hist['Close'].tolist()
            volumes = hist['Volume'].tolist()
            
            # Calculate all indicators
            indicators = {
                'sma_20': TechnicalIndicators.calculate_sma(prices, 20),
                'sma_50': TechnicalIndicators.calculate_sma(prices, 50),
                'ema_12': TechnicalIndicators.calculate_ema(prices, 12),
                'ema_26': TechnicalIndicators.calculate_ema(prices, 26),
                'rsi': TechnicalIndicators.calculate_rsi(prices),
                'macd': TechnicalIndicators.calculate_macd(prices),
                'bollinger': TechnicalIndicators.calculate_bollinger_bands(prices),
                'volume': TechnicalIndicators.calculate_volume_indicators(volumes, prices),
                'support_resistance': TechnicalIndicators.identify_support_resistance(prices),
                'prices': prices,
                'volumes': volumes,
                'dates': hist.index.strftime('%Y-%m-%d').tolist()
            }
            
            return indicators
            
        except Exception as e:
            print(f"Error calculating indicators for {symbol}: {e}")
            return {}