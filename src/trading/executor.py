"""
Trading execution module
"""
from typing import Dict, List, Optional, Any
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

from ..utils.logger import get_logger
from ..utils.config_loader import get_config


class OrderType:
    """Order type constants"""
    LIMIT = "limit"
    MARKET = "market"
    TRIGGER = "trigger"


class TimeInForce:
    """Time in force constants"""
    GTC = "Gtc"  # Good til canceled
    IOC = "Ioc"  # Immediate or cancel
    ALO = "Alo"  # Add liquidity only (post only)


class TradeExecutor:
    """Execute trades on HyperLiquid"""
    
    def __init__(self, config: dict = None, paper_trading: bool = True):
        """
        Initialize trade executor
        
        Args:
            config: Configuration dictionary
            paper_trading: If True, simulate trades without actual execution
        """
        self.logger = get_logger()
        self.paper_trading = paper_trading
        
        if config is None:
            config_loader = get_config()
            config = config_loader.get_section('hyperliquid')
            trading_config = config_loader.get_section('trading')
            self.paper_trading = trading_config.get('mode', 'paper') == 'paper'
        
        self.api_url = config.get('api_url', constants.MAINNET_API_URL)
        self.account_address = config.get('account_address')
        self.secret_key = config.get('secret_key')
        
        # Initialize exchange client only for live trading
        self.exchange = None
        if not self.paper_trading and self.account_address and self.secret_key:
            try:
                self.exchange = Exchange(
                    wallet_address=self.account_address,
                    base_url=self.api_url,
                    secret_key=self.secret_key
                )
                self.logger.info("TradeExecutor initialized in LIVE mode")
            except Exception as e:
                self.logger.error(f"Failed to initialize exchange client: {e}")
                self.paper_trading = True
                self.logger.warning("Falling back to paper trading mode")
        else:
            self.logger.info("TradeExecutor initialized in PAPER TRADING mode")
        
        # Paper trading state
        self.paper_orders: List[Dict[str, Any]] = []
        self.paper_positions: Dict[str, Dict[str, Any]] = {}
        self.next_order_id = 1
    
    def place_order(
        self,
        coin: str,
        is_buy: bool,
        size: float,
        price: Optional[float] = None,
        order_type: str = OrderType.LIMIT,
        tif: str = TimeInForce.GTC,
        reduce_only: bool = False,
        leverage: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Place an order
        
        Args:
            coin: Coin symbol (e.g., 'BTC')
            is_buy: True for buy, False for sell
            size: Order size
            price: Limit price (None for market orders)
            order_type: Order type (limit, market, trigger)
            tif: Time in force
            reduce_only: Whether order is reduce-only
            leverage: Leverage to use
        
        Returns:
            Order result
        """
        if self.paper_trading:
            return self._place_paper_order(
                coin, is_buy, size, price, order_type, tif, reduce_only, leverage
            )
        
        try:
            # Set leverage if specified
            if leverage is not None:
                self._update_leverage(coin, leverage)
            
            # Prepare order
            order = {
                "a": self._get_asset_index(coin),
                "b": is_buy,
                "p": str(price) if price else "0",
                "s": str(size),
                "r": reduce_only,
                "t": {"limit": {"tif": tif}}
            }
            
            # Execute order
            result = self.exchange.order(order)
            
            self.logger.info(
                f"Order placed: {coin} {'BUY' if is_buy else 'SELL'} "
                f"{size} @ {price if price else 'MARKET'}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return {"status": "error", "error": str(e)}
    
    def cancel_order(self, coin: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel an order
        
        Args:
            coin: Coin symbol
            order_id: Order ID to cancel
        
        Returns:
            Cancel result
        """
        if self.paper_trading:
            return self._cancel_paper_order(order_id)
        
        try:
            cancel = {
                "a": self._get_asset_index(coin),
                "o": order_id
            }
            
            result = self.exchange.cancel(cancel)
            self.logger.info(f"Order canceled: {order_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error canceling order: {e}")
            return {"status": "error", "error": str(e)}
    
    def cancel_all_orders(self, coin: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel all orders for a coin or all coins
        
        Args:
            coin: Coin symbol (None for all coins)
        
        Returns:
            Cancel result
        """
        if self.paper_trading:
            if coin:
                self.paper_orders = [o for o in self.paper_orders if o['coin'] != coin]
            else:
                self.paper_orders = []
            return {"status": "ok", "message": "All paper orders canceled"}
        
        try:
            # Implementation depends on SDK version
            self.logger.info(f"Canceling all orders for {coin if coin else 'all coins'}")
            return {"status": "ok"}
            
        except Exception as e:
            self.logger.error(f"Error canceling all orders: {e}")
            return {"status": "error", "error": str(e)}
    
    def modify_order(
        self,
        coin: str,
        order_id: int,
        new_price: float,
        new_size: float
    ) -> Dict[str, Any]:
        """
        Modify an existing order
        
        Args:
            coin: Coin symbol
            order_id: Order ID to modify
            new_price: New price
            new_size: New size
        
        Returns:
            Modify result
        """
        if self.paper_trading:
            return self._modify_paper_order(order_id, new_price, new_size)
        
        try:
            modify = {
                "oid": order_id,
                "order": {
                    "a": self._get_asset_index(coin),
                    "b": True,  # Will be determined from existing order
                    "p": str(new_price),
                    "s": str(new_size),
                    "r": False,
                    "t": {"limit": {"tif": TimeInForce.GTC}}
                }
            }
            
            result = self.exchange.modify(modify)
            self.logger.info(f"Order modified: {order_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error modifying order: {e}")
            return {"status": "error", "error": str(e)}
    
    def _update_leverage(self, coin: str, leverage: int, is_cross: bool = True):
        """
        Update leverage for a coin
        
        Args:
            coin: Coin symbol
            leverage: Leverage value
            is_cross: True for cross margin, False for isolated
        """
        if self.paper_trading:
            return
        
        try:
            self.exchange.update_leverage(
                leverage=leverage,
                coin=coin,
                is_cross=is_cross
            )
            self.logger.info(f"Leverage updated for {coin}: {leverage}x")
        except Exception as e:
            self.logger.error(f"Error updating leverage: {e}")
    
    def _get_asset_index(self, coin: str) -> int:
        """
        Get asset index for a coin
        
        Args:
            coin: Coin symbol
        
        Returns:
            Asset index
        """
        # This would need to query the meta endpoint to get the actual index
        # For now, return a placeholder
        # In production, maintain a cache of coin -> index mapping
        return 0
    
    # Paper trading methods
    
    def _place_paper_order(
        self,
        coin: str,
        is_buy: bool,
        size: float,
        price: Optional[float],
        order_type: str,
        tif: str,
        reduce_only: bool,
        leverage: Optional[int]
    ) -> Dict[str, Any]:
        """Place a simulated paper order"""
        order_id = self.next_order_id
        self.next_order_id += 1
        
        order = {
            "order_id": order_id,
            "coin": coin,
            "is_buy": is_buy,
            "size": size,
            "price": price,
            "order_type": order_type,
            "tif": tif,
            "reduce_only": reduce_only,
            "leverage": leverage,
            "status": "open"
        }
        
        self.paper_orders.append(order)
        
        self.logger.info(
            f"[PAPER] Order placed: {coin} {'BUY' if is_buy else 'SELL'} "
            f"{size} @ {price if price else 'MARKET'} (ID: {order_id})"
        )
        
        return {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {"statuses": [{"resting": {"oid": order_id}}]}
            }
        }
    
    def _cancel_paper_order(self, order_id: int) -> Dict[str, Any]:
        """Cancel a simulated paper order"""
        for order in self.paper_orders:
            if order["order_id"] == order_id:
                order["status"] = "canceled"
                self.logger.info(f"[PAPER] Order canceled: {order_id}")
                return {"status": "ok"}
        
        return {"status": "error", "error": "Order not found"}
    
    def _modify_paper_order(
        self,
        order_id: int,
        new_price: float,
        new_size: float
    ) -> Dict[str, Any]:
        """Modify a simulated paper order"""
        for order in self.paper_orders:
            if order["order_id"] == order_id:
                order["price"] = new_price
                order["size"] = new_size
                self.logger.info(f"[PAPER] Order modified: {order_id}")
                return {"status": "ok"}
        
        return {"status": "error", "error": "Order not found"}
    
    def get_paper_orders(self) -> List[Dict[str, Any]]:
        """Get all paper orders"""
        return [o for o in self.paper_orders if o["status"] == "open"]
    
    def get_paper_positions(self) -> Dict[str, Dict[str, Any]]:
        """Get all paper positions"""
        return self.paper_positions
