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
        
        # Calculate EMAs (12 and 26 periods)
        ema_12 = TechnicalIndicators.calculate_ema(prices, 12)
        ema_26 = TechnicalIndicators.calculate_ema(prices, 26)
        
        # Calculate MACD line
        macd_line = []
        for i in range(len(ema_26)):
            macd_line.append(ema_12[i + (len(ema_12) - len(ema_26))] - ema_26[i])
        
        # Calculate signal line (9-period EMA of MACD)
        signal_line = TechnicalIndicators.calculate_ema(macd_line, 9)
        
        # Calculate histogram
        histogram = []
        for i in range(len(signal_line)):
            histogram.append(macd_line[i + (len(macd_line) - len(signal_line))] - signal_line[i])
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, List[float]]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {'upper': [], 'middle': [], 'lower': []}
        
        sma = TechnicalIndicators.calculate_sma(prices, period)
        upper_band = []
        lower_band = []
        
        for i in range(period - 1, len(prices)):
            # Calculate standard deviation for the period
            price_slice = prices[i - period + 1:i + 1]
            mean = sum(price_slice) / period
            variance = sum((x - mean) ** 2 for x in price_slice) / period
            std_deviation = variance ** 0.5
            
            upper_band.append(sma[i - period + 1] + (std_dev * std_deviation))
            lower_band.append(sma[i - period + 1] - (std_dev * std_deviation))
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    
    @staticmethod
    def calculate_stochastic(high: List[float], low: List[float], close: List[float], k_period: int = 14, d_period: int = 3) -> Dict[str, List[float]]:
        """Calculate Stochastic Oscillator"""
        if len(high) < k_period or len(low) < k_period or len(close) < k_period:
            return {'k': [], 'd': []}
        
        k_values = []
        
        for i in range(k_period - 1, len(close)):
            highest_high = max(high[i - k_period + 1:i + 1])
            lowest_low = min(low[i - k_period + 1:i + 1])
            
            if highest_high == lowest_low:
                k_percent = 50  # Avoid division by zero
            else:
                k_percent = ((close[i] - lowest_low) / (highest_high - lowest_low)) * 100
            
            k_values.append(k_percent)
        
        # Calculate %D (moving average of %K)
        d_values = TechnicalIndicators.calculate_sma(k_values, d_period)
        
        return {
            'k': k_values,
            'd': d_values
        }
    
    @staticmethod
    def calculate_vwap(prices: List[float], volumes: List[float]) -> List[float]:
        """Calculate Volume Weighted Average Price"""
        if len(prices) != len(volumes) or len(prices) == 0:
            return []
        
        vwap_values = []
        cumulative_volume = 0
        cumulative_price_volume = 0
        
        for i in range(len(prices)):
            cumulative_volume += volumes[i]
            cumulative_price_volume += prices[i] * volumes[i]
            
            if cumulative_volume > 0:
                vwap_values.append(cumulative_price_volume / cumulative_volume)
            else:
                vwap_values.append(prices[i])
        
        return vwap_values
    
    @staticmethod
    def find_support_resistance(prices: List[float], window: int = 10) -> Dict[str, List[float]]:
        """Find support and resistance levels"""
        if len(prices) < window * 2:
            return {'support': [], 'resistance': []}
        
        support_levels = []
        resistance_levels = []
        
        for i in range(window, len(prices) - window):
            # Check for local minimum (support)
            is_support = True
            for j in range(i - window, i + window + 1):
                if j != i and prices[j] < prices[i]:
                    is_support = False
                    break
            
            if is_support:
                support_levels.append(prices[i])
            
            # Check for local maximum (resistance)
            is_resistance = True
            for j in range(i - window, i + window + 1):
                if j != i and prices[j] > prices[i]:
                    is_resistance = False
                    break
            
            if is_resistance:
                resistance_levels.append(prices[i])
        
        # Sort and return most significant levels
        support_levels.sort()
        resistance_levels.sort(reverse=True)
        
        return {
            'support': support_levels[:3],  # Top 3 support levels
            'resistance': resistance_levels[:3]  # Top 3 resistance levels
        }
    
    @staticmethod
    def calculate_additional_indicators(prices: List[float], volumes: List[float]) -> Dict:
        """Calculate additional technical indicators"""
        if len(prices) < 50:
            return {}
            
        # Average True Range (ATR)
        atr = TechnicalIndicators.calculate_atr(prices, 14)
        
        # Commodity Channel Index (CCI)
        cci = TechnicalIndicators.calculate_cci(prices, 20)
        
        # Williams %R
        williams_r = TechnicalIndicators.calculate_williams_r(prices, 14)
        
        # Money Flow Index (MFI)
        mfi = TechnicalIndicators.calculate_mfi(prices, volumes, 14)
        
        return {
            'atr': atr,
            'cci': cci,
            'williams_r': williams_r,
            'mfi': mfi
        }
    
    @staticmethod
    def calculate_atr(prices: List[float], period: int = 14) -> List[float]:
        """Calculate Average True Range"""
        if len(prices) < period + 1:
            return []
        
        true_ranges = []
        for i in range(1, len(prices)):
            high_low = prices[i] - prices[i-1] if i > 0 else 0
            high_close = abs(prices[i] - prices[i-1])
            low_close = abs(prices[i-1] - prices[i-1])
            true_range = max(high_low, high_close, low_close)
            true_ranges.append(true_range)
        
        return TechnicalIndicators.calculate_sma(true_ranges, period)
    
    @staticmethod
    def calculate_cci(prices: List[float], period: int = 20) -> List[float]:
        """Calculate Commodity Channel Index"""
        if len(prices) < period:
            return []
        
        cci_values = []
        for i in range(period - 1, len(prices)):
            slice_prices = prices[i - period + 1:i + 1]
            typical_price = sum(slice_prices) / period
            mean_deviation = sum(abs(price - typical_price) for price in slice_prices) / period
            
            if mean_deviation != 0:
                cci = (typical_price - sum(slice_prices) / period) / (0.015 * mean_deviation)
            else:
                cci = 0
            
            cci_values.append(cci)
        
        return cci_values
    
    @staticmethod
    def calculate_williams_r(prices: List[float], period: int = 14) -> List[float]:
        """Calculate Williams %R"""
        if len(prices) < period:
            return []
        
        williams_r_values = []
        for i in range(period - 1, len(prices)):
            slice_prices = prices[i - period + 1:i + 1]
            highest_high = max(slice_prices)
            lowest_low = min(slice_prices)
            
            if highest_high != lowest_low:
                williams_r = ((highest_high - prices[i]) / (highest_high - lowest_low)) * -100
            else:
                williams_r = 0
            
            williams_r_values.append(williams_r)
        
        return williams_r_values
    
    @staticmethod
    def calculate_mfi(prices: List[float], volumes: List[float], period: int = 14) -> List[float]:
        """Calculate Money Flow Index"""
        if len(prices) < period + 1 or len(volumes) < period + 1:
            return []
        
        mfi_values = []
        for i in range(period, len(prices)):
            positive_flow = 0
            negative_flow = 0
            
            for j in range(i - period + 1, i + 1):
                if j > 0:
                    typical_price = prices[j]
                    prev_typical_price = prices[j-1]
                    money_flow = typical_price * volumes[j]
                    
                    if typical_price > prev_typical_price:
                        positive_flow += money_flow
                    elif typical_price < prev_typical_price:
                        negative_flow += money_flow
            
            if negative_flow == 0:
                mfi = 100
            elif positive_flow == 0:
                mfi = 0
            else:
                money_flow_ratio = positive_flow / negative_flow
                mfi = 100 - (100 / (1 + money_flow_ratio))
            
            mfi_values.append(mfi)
        
        return mfi_values
    
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