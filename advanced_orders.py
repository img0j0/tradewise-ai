"""
Advanced Order Management System
Implements professional trading order types and risk management
"""

import logging
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import math
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TRAILING_STOP = "trailing_stop"
    BRACKET = "bracket"
    OCO = "oco"  # One-Cancels-Other

class OrderStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    FILLED = "filled"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

@dataclass
class OrderCondition:
    """Represents a condition for order execution"""
    type: str
    value: float
    operator: str  # ">=", "<=", "==", "!=", "<", ">"
    
class AdvancedOrder:
    """Advanced order with professional trading features"""
    
    def __init__(self, symbol: str, quantity: int, order_type: OrderType, 
                 side: OrderSide, user_id: int, **kwargs):
        self.id = self._generate_order_id()
        self.symbol = symbol
        self.quantity = quantity
        self.order_type = order_type
        self.side = side
        self.user_id = user_id
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Order-specific parameters
        self.limit_price = kwargs.get('limit_price')
        self.stop_price = kwargs.get('stop_price')
        self.trailing_amount = kwargs.get('trailing_amount')
        self.trailing_percent = kwargs.get('trailing_percent')
        self.time_in_force = kwargs.get('time_in_force', 'GTC')  # Good Till Cancelled
        self.expires_at = kwargs.get('expires_at')
        
        # Bracket order parameters
        self.parent_order_id = kwargs.get('parent_order_id')
        self.child_orders = kwargs.get('child_orders', [])
        
        # OCO parameters
        self.oco_group_id = kwargs.get('oco_group_id')
        
        # Risk management
        self.max_loss = kwargs.get('max_loss')
        self.max_profit = kwargs.get('max_profit')
        
        # Execution tracking
        self.filled_quantity = 0
        self.average_fill_price = 0
        self.fills = []
        
        # Conditions
        self.conditions = kwargs.get('conditions', [])
        
        # Metadata
        self.notes = kwargs.get('notes', '')
        self.strategy_name = kwargs.get('strategy_name', '')
        
        logger.info(f"Advanced order created: {self.id} - {self.symbol} {self.side.value} {self.quantity} @ {self.order_type.value}")
    
    def _generate_order_id(self) -> str:
        """Generate unique order ID"""
        return f"ADV_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def update_status(self, status: OrderStatus, notes: str = ""):
        """Update order status with timestamp"""
        self.status = status
        self.updated_at = datetime.now()
        if notes:
            self.notes += f"\n{datetime.now()}: {notes}"
        logger.info(f"Order {self.id} status updated to {status.value}")
    
    def add_fill(self, quantity: int, price: float, timestamp: datetime = None):
        """Add a partial or full fill to the order"""
        if timestamp is None:
            timestamp = datetime.now()
        
        fill = {
            'quantity': quantity,
            'price': price,
            'timestamp': timestamp
        }
        
        self.fills.append(fill)
        self.filled_quantity += quantity
        
        # Calculate average fill price
        total_value = sum(f['quantity'] * f['price'] for f in self.fills)
        self.average_fill_price = total_value / self.filled_quantity
        
        # Update status
        if self.filled_quantity >= self.quantity:
            self.update_status(OrderStatus.FILLED)
        
        logger.info(f"Order {self.id} filled: {quantity} @ {price} (Total: {self.filled_quantity}/{self.quantity})")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary for API responses"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'filled_quantity': self.filled_quantity,
            'order_type': self.order_type.value,
            'side': self.side.value,
            'status': self.status.value,
            'limit_price': self.limit_price,
            'stop_price': self.stop_price,
            'trailing_amount': self.trailing_amount,
            'trailing_percent': self.trailing_percent,
            'average_fill_price': self.average_fill_price,
            'time_in_force': self.time_in_force,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'parent_order_id': self.parent_order_id,
            'child_orders': self.child_orders,
            'oco_group_id': self.oco_group_id,
            'max_loss': self.max_loss,
            'max_profit': self.max_profit,
            'fills': self.fills,
            'conditions': [c.__dict__ for c in self.conditions],
            'notes': self.notes,
            'strategy_name': self.strategy_name
        }

class PositionSizer:
    """Kelly Criterion and risk-based position sizing"""
    
    @staticmethod
    def kelly_criterion(win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Calculate optimal position size using Kelly Criterion"""
        if avg_loss == 0:
            return 0
        
        b = avg_win / avg_loss  # Win/loss ratio
        p = win_rate  # Win probability
        q = 1 - p  # Loss probability
        
        f = (b * p - q) / b  # Kelly fraction
        
        # Cap at 25% for safety
        return min(f, 0.25)
    
    @staticmethod
    def risk_based_sizing(account_balance: float, risk_percent: float, 
                         entry_price: float, stop_loss: float) -> int:
        """Calculate position size based on risk percentage"""
        if stop_loss <= 0 or entry_price <= 0:
            return 0
        
        risk_amount = account_balance * (risk_percent / 100)
        price_difference = abs(entry_price - stop_loss)
        
        if price_difference == 0:
            return 0
        
        position_size = risk_amount / price_difference
        return int(position_size)
    
    @staticmethod
    def volatility_sizing(account_balance: float, volatility: float, 
                         target_volatility: float = 0.02) -> float:
        """Size position based on volatility targeting"""
        if volatility == 0:
            return 0
        
        volatility_multiplier = target_volatility / volatility
        max_position_value = account_balance * volatility_multiplier
        
        return max_position_value

class AdvancedOrderManager:
    """Manages advanced order types and execution logic"""
    
    def __init__(self):
        self.orders = {}  # order_id -> AdvancedOrder
        self.active_orders = {}  # symbol -> list of active orders
        self.oco_groups = {}  # oco_group_id -> list of orders
        self.position_sizer = PositionSizer()
        
        logger.info("Advanced Order Manager initialized")
    
    def create_order(self, symbol: str, quantity: int, order_type: OrderType, 
                    side: OrderSide, user_id: int, **kwargs) -> AdvancedOrder:
        """Create a new advanced order"""
        order = AdvancedOrder(symbol, quantity, order_type, side, user_id, **kwargs)
        
        # Store order
        self.orders[order.id] = order
        
        # Add to active orders
        if symbol not in self.active_orders:
            self.active_orders[symbol] = []
        self.active_orders[symbol].append(order)
        
        # Handle OCO grouping
        if order.oco_group_id:
            if order.oco_group_id not in self.oco_groups:
                self.oco_groups[order.oco_group_id] = []
            self.oco_groups[order.oco_group_id].append(order)
        
        return order
    
    def create_bracket_order(self, symbol: str, quantity: int, side: OrderSide, 
                           user_id: int, entry_price: float, stop_loss: float, 
                           take_profit: float, **kwargs) -> Dict[str, AdvancedOrder]:
        """Create a bracket order (entry + stop loss + take profit)"""
        
        # Create parent entry order
        parent_order = self.create_order(
            symbol, quantity, OrderType.LIMIT, side, user_id,
            limit_price=entry_price, **kwargs
        )
        
        # Create stop loss order
        stop_side = OrderSide.SELL if side == OrderSide.BUY else OrderSide.BUY
        stop_order = self.create_order(
            symbol, quantity, OrderType.STOP_LOSS, stop_side, user_id,
            stop_price=stop_loss, parent_order_id=parent_order.id, **kwargs
        )
        
        # Create take profit order
        profit_order = self.create_order(
            symbol, quantity, OrderType.TAKE_PROFIT, stop_side, user_id,
            limit_price=take_profit, parent_order_id=parent_order.id, **kwargs
        )
        
        # Link orders
        parent_order.child_orders = [stop_order.id, profit_order.id]
        
        return {
            'parent': parent_order,
            'stop_loss': stop_order,
            'take_profit': profit_order
        }
    
    def create_trailing_stop(self, symbol: str, quantity: int, side: OrderSide, 
                           user_id: int, trailing_amount: float = None, 
                           trailing_percent: float = None, **kwargs) -> AdvancedOrder:
        """Create a trailing stop order"""
        return self.create_order(
            symbol, quantity, OrderType.TRAILING_STOP, side, user_id,
            trailing_amount=trailing_amount, trailing_percent=trailing_percent,
            **kwargs
        )
    
    def cancel_order(self, order_id: str, reason: str = "User cancelled") -> bool:
        """Cancel an order"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        
        # Cancel OCO group if applicable
        if order.oco_group_id:
            self._cancel_oco_group(order.oco_group_id, exclude_order_id=order_id)
        
        # Cancel child orders for bracket orders
        if order.child_orders:
            for child_id in order.child_orders:
                if child_id in self.orders:
                    self.orders[child_id].update_status(OrderStatus.CANCELLED, "Parent order cancelled")
        
        order.update_status(OrderStatus.CANCELLED, reason)
        return True
    
    def _cancel_oco_group(self, oco_group_id: str, exclude_order_id: str = None):
        """Cancel all orders in an OCO group"""
        if oco_group_id not in self.oco_groups:
            return
        
        for order in self.oco_groups[oco_group_id]:
            if order.id != exclude_order_id and order.status == OrderStatus.ACTIVE:
                order.update_status(OrderStatus.CANCELLED, "OCO group cancelled")
    
    def process_market_update(self, symbol: str, current_price: float):
        """Process market price updates and trigger orders"""
        if symbol not in self.active_orders:
            return
        
        orders_to_process = [o for o in self.active_orders[symbol] 
                           if o.status == OrderStatus.ACTIVE]
        
        for order in orders_to_process:
            self._evaluate_order_conditions(order, current_price)
    
    def _evaluate_order_conditions(self, order: AdvancedOrder, current_price: float):
        """Evaluate order conditions and trigger execution"""
        should_execute = False
        
        if order.order_type == OrderType.STOP_LOSS:
            if order.side == OrderSide.SELL and current_price <= order.stop_price:
                should_execute = True
            elif order.side == OrderSide.BUY and current_price >= order.stop_price:
                should_execute = True
        
        elif order.order_type == OrderType.TAKE_PROFIT:
            if order.side == OrderSide.SELL and current_price >= order.limit_price:
                should_execute = True
            elif order.side == OrderSide.BUY and current_price <= order.limit_price:
                should_execute = True
        
        elif order.order_type == OrderType.TRAILING_STOP:
            self._update_trailing_stop(order, current_price)
        
        # Check custom conditions
        for condition in order.conditions:
            if not self._evaluate_condition(condition, current_price):
                should_execute = False
                break
        
        if should_execute:
            self._execute_order(order, current_price)
    
    def _update_trailing_stop(self, order: AdvancedOrder, current_price: float):
        """Update trailing stop price"""
        if not order.stop_price:
            # Initialize trailing stop
            if order.trailing_amount:
                order.stop_price = current_price - order.trailing_amount
            elif order.trailing_percent:
                order.stop_price = current_price * (1 - order.trailing_percent / 100)
            return
        
        # Update trailing stop
        if order.side == OrderSide.SELL:
            # For sell orders, trail up
            if order.trailing_amount:
                new_stop = current_price - order.trailing_amount
            else:
                new_stop = current_price * (1 - order.trailing_percent / 100)
            
            if new_stop > order.stop_price:
                order.stop_price = new_stop
                order.notes += f"\nTrailing stop updated to {new_stop} at {datetime.now()}"
        
        # Check if stop should trigger
        if current_price <= order.stop_price:
            self._execute_order(order, current_price)
    
    def _evaluate_condition(self, condition: OrderCondition, current_price: float) -> bool:
        """Evaluate a custom order condition"""
        if condition.operator == ">=":
            return current_price >= condition.value
        elif condition.operator == "<=":
            return current_price <= condition.value
        elif condition.operator == "==":
            return abs(current_price - condition.value) < 0.01
        elif condition.operator == "!=":
            return abs(current_price - condition.value) >= 0.01
        elif condition.operator == "<":
            return current_price < condition.value
        elif condition.operator == ">":
            return current_price > condition.value
        
        return False
    
    def _execute_order(self, order: AdvancedOrder, price: float):
        """Execute an order"""
        order.add_fill(order.quantity - order.filled_quantity, price)
        
        # Cancel OCO group if applicable
        if order.oco_group_id:
            self._cancel_oco_group(order.oco_group_id, exclude_order_id=order.id)
        
        logger.info(f"Order executed: {order.id} - {order.symbol} {order.side.value} {order.quantity} @ {price}")
    
    def get_orders_by_user(self, user_id: int) -> List[AdvancedOrder]:
        """Get all orders for a user"""
        return [order for order in self.orders.values() if order.user_id == user_id]
    
    def get_active_orders(self, symbol: str = None) -> List[AdvancedOrder]:
        """Get active orders, optionally filtered by symbol"""
        if symbol:
            return [o for o in self.active_orders.get(symbol, []) 
                   if o.status == OrderStatus.ACTIVE]
        else:
            all_orders = []
            for orders in self.active_orders.values():
                all_orders.extend([o for o in orders if o.status == OrderStatus.ACTIVE])
            return all_orders
    
    def calculate_position_size(self, method: str, **kwargs) -> float:
        """Calculate position size using various methods"""
        if method == "kelly":
            return self.position_sizer.kelly_criterion(
                kwargs.get('win_rate', 0.6),
                kwargs.get('avg_win', 1.0),
                kwargs.get('avg_loss', 1.0)
            )
        elif method == "risk_based":
            return self.position_sizer.risk_based_sizing(
                kwargs.get('account_balance', 10000),
                kwargs.get('risk_percent', 2),
                kwargs.get('entry_price', 100),
                kwargs.get('stop_loss', 95)
            )
        elif method == "volatility":
            return self.position_sizer.volatility_sizing(
                kwargs.get('account_balance', 10000),
                kwargs.get('volatility', 0.02),
                kwargs.get('target_volatility', 0.02)
            )
        else:
            return 0

# Global order manager instance
order_manager = AdvancedOrderManager()

def get_order_manager():
    """Get the global order manager instance"""
    return order_manager