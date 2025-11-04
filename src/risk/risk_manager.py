"""
Risk management module
"""
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta

from ..utils.logger import get_logger
from ..utils.config_loader import get_config


class RiskManager:
    """Manage trading risks and position sizing"""
    
    def __init__(self, config: dict = None):
        """
        Initialize risk manager
        
        Args:
            config: Risk configuration dictionary
        """
        self.logger = get_logger()
        
        if config is None:
            config_loader = get_config()
            config = config_loader.get_section('risk')
        
        # Risk parameters
        self.max_position_per_coin = config.get('max_position_per_coin', 0.20)
        self.max_total_position = config.get('max_total_position', 0.80)
        self.default_leverage = config.get('default_leverage', 3)
        self.max_leverage = config.get('max_leverage', 5)
        if self.max_leverage in (None, 0):
            self.max_leverage = float('inf')
        self.stop_loss_pct = config.get('stop_loss_pct', 0.05)
        self.take_profit_pct = config.get('take_profit_pct', 0.10)
        self.max_drawdown = config.get('max_drawdown', 0.20)
        self.max_daily_loss = config.get('max_daily_loss', 0.10)
        
        # State tracking
        self.initial_capital = 0
        self.current_capital = 0
        self.peak_capital = 0
        self.daily_pnl = 0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.trading_enabled = True
        
        self.logger.info("RiskManager initialized")
    
    def initialize_capital(self, capital: float):
        """
        Initialize capital tracking
        
        Args:
            capital: Initial capital amount
        """
        self.initial_capital = capital
        self.current_capital = capital
        self.peak_capital = capital
        self.logger.info(f"Capital initialized: ${capital:,.2f}")
    
    def update_capital(self, capital: float):
        """
        Update current capital
        
        Args:
            capital: Current capital amount
        """
        self.current_capital = capital
        
        # Update peak capital
        if capital > self.peak_capital:
            self.peak_capital = capital
        
        # Check for max drawdown
        drawdown = self.calculate_drawdown()
        if drawdown > self.max_drawdown:
            self.trading_enabled = False
            self.logger.critical(
                f"Maximum drawdown exceeded: {drawdown:.2%} > {self.max_drawdown:.2%}. "
                "Trading disabled!"
            )
    
    def calculate_drawdown(self) -> float:
        """
        Calculate current drawdown from peak
        
        Returns:
            Drawdown as a decimal (e.g., 0.15 for 15%)
        """
        if self.peak_capital == 0:
            return 0
        
        drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
        return max(0, drawdown)
    
    def check_daily_loss_limit(self, pnl: float) -> bool:
        """
        Check if daily loss limit is exceeded
        
        Args:
            pnl: Profit/loss for the day
        
        Returns:
            True if within limit, False if exceeded
        """
        # Reset daily PnL if new day
        now = datetime.now()
        if now >= self.daily_reset_time + timedelta(days=1):
            self.daily_pnl = 0
            self.daily_reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        self.daily_pnl = pnl
        
        # Check limit
        loss_pct = abs(pnl) / self.initial_capital if pnl < 0 else 0
        
        if loss_pct > self.max_daily_loss:
            self.trading_enabled = False
            self.logger.critical(
                f"Daily loss limit exceeded: {loss_pct:.2%} > {self.max_daily_loss:.2%}. "
                "Trading disabled for today!"
            )
            return False
        
        return True
    
    def calculate_position_size(
        self,
        coin: str,
        entry_price: float,
        confidence: float = 0.5,
        volatility: float = 0.02
    ) -> float:
        """
        Calculate optimal position size based on risk parameters
        
        Args:
            coin: Coin symbol
            entry_price: Entry price
            confidence: Confidence level (0-1)
            volatility: Estimated volatility
        
        Returns:
            Position size in base currency units
        """
        # Base position size from max position per coin
        max_position_value = self.current_capital * self.max_position_per_coin
        
        # Adjust for confidence (higher confidence = larger position)
        confidence_multiplier = 0.5 + (confidence * 0.5)  # Range: 0.5 to 1.0
        position_value = max_position_value * confidence_multiplier
        
        # Adjust for volatility (higher volatility = smaller position)
        volatility_multiplier = 1.0 / (1.0 + volatility * 10)  # Reduce size for high volatility
        position_value *= volatility_multiplier
        
        # Calculate position size in coins
        position_size = position_value / entry_price
        
        self.logger.debug(
            f"Position size calculated for {coin}: {position_size:.4f} "
            f"(value: ${position_value:.2f}, confidence: {confidence:.2f})"
        )
        
        return position_size
    
    def calculate_stop_loss(self, entry_price: float, is_long: bool) -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            is_long: True for long position, False for short
        
        Returns:
            Stop loss price
        """
        if is_long:
            stop_loss = entry_price * (1 - self.stop_loss_pct)
        else:
            stop_loss = entry_price * (1 + self.stop_loss_pct)
        
        return stop_loss
    
    def calculate_take_profit(self, entry_price: float, is_long: bool) -> float:
        """
        Calculate take profit price
        
        Args:
            entry_price: Entry price
            is_long: True for long position, False for short
        
        Returns:
            Take profit price
        """
        if is_long:
            take_profit = entry_price * (1 + self.take_profit_pct)
        else:
            take_profit = entry_price * (1 - self.take_profit_pct)
        
        return take_profit
    
    def validate_trade(
        self,
        coin: str,
        size: float,
        price: float,
        leverage: int = 1
    ) -> Tuple[bool, str]:
        """
        Validate if a trade meets risk requirements
        
        Args:
            coin: Coin symbol
            size: Position size
            price: Entry price
            leverage: Leverage to use
        
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check if trading is enabled
        if not self.trading_enabled:
            return False, "Trading is currently disabled due to risk limits"
        
        # Check leverage
        if self.max_leverage != float('inf') and leverage > self.max_leverage:
            return False, f"Leverage {leverage}x exceeds maximum {self.max_leverage}x"
        
        # Calculate position value
        position_value = size * price
        
        # Check position size limit
        max_position_value = self.current_capital * self.max_position_per_coin
        if position_value > max_position_value:
            return False, f"Position size ${position_value:.2f} exceeds limit ${max_position_value:.2f}"
        
        # Check total position limit
        total_position_value = sum(
            pos.get('size', 0) * pos.get('entry_price', 0)
            for pos in self.positions.values()
        )
        total_position_value += position_value
        
        max_total_value = self.current_capital * self.max_total_position
        if total_position_value > max_total_value:
            return False, f"Total position ${total_position_value:.2f} exceeds limit ${max_total_value:.2f}"
        
        return True, "Trade validated"
    
    def add_position(
        self,
        coin: str,
        size: float,
        entry_price: float,
        is_long: bool,
        leverage: int = 1
    ):
        """
        Add a position to tracking
        
        Args:
            coin: Coin symbol
            size: Position size
            entry_price: Entry price
            is_long: True for long, False for short
            leverage: Leverage used
        """
        self.positions[coin] = {
            'size': size,
            'entry_price': entry_price,
            'is_long': is_long,
            'leverage': leverage,
            'stop_loss': self.calculate_stop_loss(entry_price, is_long),
            'take_profit': self.calculate_take_profit(entry_price, is_long),
            'entry_time': datetime.now()
        }
        
        self.logger.info(
            f"Position added: {coin} {'LONG' if is_long else 'SHORT'} "
            f"{size} @ ${entry_price:.2f} (leverage: {leverage}x)"
        )
    
    def remove_position(self, coin: str):
        """
        Remove a position from tracking
        
        Args:
            coin: Coin symbol
        """
        if coin in self.positions:
            del self.positions[coin]
            self.logger.info(f"Position removed: {coin}")
    
    def update_position(self, coin: str, current_price: float) -> Optional[str]:
        """
        Update position and check for stop loss / take profit
        
        Args:
            coin: Coin symbol
            current_price: Current market price
        
        Returns:
            Action to take ('close_stop_loss', 'close_take_profit', None)
        """
        if coin not in self.positions:
            return None
        
        position = self.positions[coin]
        is_long = position['is_long']
        stop_loss = position['stop_loss']
        take_profit = position['take_profit']
        
        # Check stop loss
        if is_long and current_price <= stop_loss:
            self.logger.warning(f"Stop loss triggered for {coin}: ${current_price:.2f} <= ${stop_loss:.2f}")
            return 'close_stop_loss'
        elif not is_long and current_price >= stop_loss:
            self.logger.warning(f"Stop loss triggered for {coin}: ${current_price:.2f} >= ${stop_loss:.2f}")
            return 'close_stop_loss'
        
        # Check take profit
        if is_long and current_price >= take_profit:
            self.logger.info(f"Take profit triggered for {coin}: ${current_price:.2f} >= ${take_profit:.2f}")
            return 'close_take_profit'
        elif not is_long and current_price <= take_profit:
            self.logger.info(f"Take profit triggered for {coin}: ${current_price:.2f} <= ${take_profit:.2f}")
            return 'close_take_profit'
        
        return None
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """
        Get current risk metrics
        
        Returns:
            Dictionary of risk metrics
        """
        return {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'peak_capital': self.peak_capital,
            'drawdown': self.calculate_drawdown(),
            'daily_pnl': self.daily_pnl,
            'num_positions': len(self.positions),
            'trading_enabled': self.trading_enabled,
            'total_position_value': sum(
                pos.get('size', 0) * pos.get('entry_price', 0)
                for pos in self.positions.values()
            )
        }
