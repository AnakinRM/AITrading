"""
Unit tests for symbol filtering and availability checking
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.constants import ALLOWED_SYMBOLS
from src.data.market_data import MarketDataCollector


class TestSymbolFiltering(unittest.TestCase):
    """Test symbol whitelist and availability checking"""
    
    def test_allowed_symbols_constant(self):
        """Test that ALLOWED_SYMBOLS contains exactly 6 symbols"""
        self.assertEqual(len(ALLOWED_SYMBOLS), 6)
        self.assertIn("XRP", ALLOWED_SYMBOLS)
        self.assertIn("DOGE", ALLOWED_SYMBOLS)
        self.assertIn("BTC", ALLOWED_SYMBOLS)
        self.assertIn("ETH", ALLOWED_SYMBOLS)
        self.assertIn("SOL", ALLOWED_SYMBOLS)
        self.assertIn("BNB", ALLOWED_SYMBOLS)
    
    @patch('src.data.market_data.Info')
    def test_market_data_collector_init(self, mock_info):
        """Test MarketDataCollector initializes with allowed symbols"""
        config = {
            'api_url': 'https://api.hyperliquid-testnet.xyz'
        }
        
        collector = MarketDataCollector(config)
        
        self.assertEqual(collector.allowed_symbols, ALLOWED_SYMBOLS)
        self.assertEqual(len(collector.allowed_symbols), 6)
    
    @patch('src.data.market_data.Info')
    def test_get_price_safe_allowed_symbol(self, mock_info):
        """Test get_price_safe returns price for allowed symbol"""
        config = {'api_url': 'https://api.hyperliquid-testnet.xyz'}
        collector = MarketDataCollector(config)
        
        # Mock all_mids to return price
        collector.info.all_mids = Mock(return_value={'BTC': 50000.0})
        
        price = collector.get_price_safe('BTC')
        
        self.assertIsNotNone(price)
        self.assertEqual(price, 50000.0)
    
    @patch('src.data.market_data.Info')
    def test_get_price_safe_disallowed_symbol(self, mock_info):
        """Test get_price_safe returns None for disallowed symbol"""
        config = {'api_url': 'https://api.hyperliquid-testnet.xyz'}
        collector = MarketDataCollector(config)
        
        price = collector.get_price_safe('INVALID')
        
        self.assertIsNone(price)
    
    @patch('src.data.market_data.Info')
    def test_get_price_safe_unavailable_symbol(self, mock_info):
        """Test get_price_safe returns None when symbol has no price"""
        config = {'api_url': 'https://api.hyperliquid-testnet.xyz'}
        collector = MarketDataCollector(config)
        
        # Mock all_mids to return empty dict
        collector.info.all_mids = Mock(return_value={})
        
        price = collector.get_price_safe('BTC')
        
        self.assertIsNone(price)
    
    @patch('src.data.market_data.Info')
    def test_get_price_safe_invalid_price(self, mock_info):
        """Test get_price_safe returns None for invalid price values"""
        config = {'api_url': 'https://api.hyperliquid-testnet.xyz'}
        collector = MarketDataCollector(config)
        
        # Test None price
        collector.info.all_mids = Mock(return_value={'BTC': None})
        self.assertIsNone(collector.get_price_safe('BTC'))
        
        # Test zero price
        collector.info.all_mids = Mock(return_value={'BTC': 0})
        self.assertIsNone(collector.get_price_safe('BTC'))
        
        # Test negative price
        collector.info.all_mids = Mock(return_value={'BTC': -100})
        self.assertIsNone(collector.get_price_safe('BTC'))
    
    @patch('src.data.market_data.Info')
    def test_get_available_symbols(self, mock_info):
        """Test get_available_symbols filters correctly"""
        config = {'api_url': 'https://api.hyperliquid-testnet.xyz'}
        collector = MarketDataCollector(config)
        
        # Mock all_mids with some available and some unavailable
        collector.info.all_mids = Mock(return_value={
            'BTC': 50000.0,
            'ETH': 3000.0,
            'SOL': 100.0,
            'XRP': None,  # Unavailable
            'DOGE': 0,    # Invalid price
            # BNB missing completely
        })
        
        available = collector.get_available_symbols()
        
        self.assertEqual(len(available), 3)
        self.assertIn('BTC', available)
        self.assertIn('ETH', available)
        self.assertIn('SOL', available)
        self.assertNotIn('XRP', available)
        self.assertNotIn('DOGE', available)
        self.assertNotIn('BNB', available)
    
    @patch('src.data.market_data.Info')
    def test_get_market_data_for_symbols_skip_unavailable(self, mock_info):
        """Test get_market_data_for_symbols skips unavailable symbols"""
        config = {'api_url': 'https://api.hyperliquid-testnet.xyz'}
        collector = MarketDataCollector(config)
        
        # Mock methods
        def mock_get_price_safe(symbol):
            prices = {'BTC': 50000.0, 'ETH': 3000.0}
            return prices.get(symbol)
        
        collector.get_price_safe = mock_get_price_safe
        collector.get_l2_book = Mock(return_value={})
        collector.get_candles = Mock(return_value=Mock())
        
        # Request all allowed symbols
        market_data = collector.get_market_data_for_symbols(ALLOWED_SYMBOLS)
        
        # Should only return data for BTC and ETH
        self.assertEqual(len(market_data), 2)
        self.assertIn('BTC', market_data)
        self.assertIn('ETH', market_data)
        self.assertEqual(market_data['BTC']['price'], 50000.0)
        self.assertEqual(market_data['ETH']['price'], 3000.0)


class TestTradingPlanValidation(unittest.TestCase):
    """Test trading plan validation"""
    
    @patch('src.ai.deepseek_trading_agent.OpenAI')
    def test_validate_trading_plan_filters_disallowed(self, mock_openai):
        """Test that validation filters out disallowed symbols"""
        from src.ai.deepseek_trading_agent import DeepseekTradingAgent
        
        config = {
            'api_key': 'test-key',
            'api_url': 'https://api.deepseek.com',
            'model': 'deepseek-chat'
        }
        
        agent = DeepseekTradingAgent(config)
        
        # Plan with both allowed and disallowed symbols
        plan = {
            'candidates': [
                {'symbol': 'BTC', 'direction': 'LONG'},
                {'symbol': 'INVALID', 'direction': 'LONG'},  # Should be filtered
                {'symbol': 'ETH', 'direction': 'SHORT'},
            ]
        }
        
        validated = agent._validate_trading_plan(plan, [])
        
        self.assertEqual(len(validated['candidates']), 2)
        symbols = [c['symbol'] for c in validated['candidates']]
        self.assertIn('BTC', symbols)
        self.assertIn('ETH', symbols)
        self.assertNotIn('INVALID', symbols)
    
    @patch('src.ai.deepseek_trading_agent.OpenAI')
    def test_validate_trading_plan_filters_unavailable(self, mock_openai):
        """Test that validation filters out unavailable symbols"""
        from src.ai.deepseek_trading_agent import DeepseekTradingAgent
        
        config = {
            'api_key': 'test-key',
            'api_url': 'https://api.deepseek.com',
            'model': 'deepseek-chat'
        }
        
        agent = DeepseekTradingAgent(config)
        
        plan = {
            'candidates': [
                {'symbol': 'BTC', 'direction': 'LONG'},
                {'symbol': 'XRP', 'direction': 'LONG'},  # Unavailable
                {'symbol': 'ETH', 'direction': 'SHORT'},
            ]
        }
        
        # XRP is unavailable
        validated = agent._validate_trading_plan(plan, ['XRP'])
        
        self.assertEqual(len(validated['candidates']), 2)
        symbols = [c['symbol'] for c in validated['candidates']]
        self.assertIn('BTC', symbols)
        self.assertIn('ETH', symbols)
        self.assertNotIn('XRP', symbols)
    
    @patch('src.ai.deepseek_trading_agent.OpenAI')
    def test_validate_trading_plan_filters_invalid_direction(self, mock_openai):
        """Test that validation filters invalid directions"""
        from src.ai.deepseek_trading_agent import DeepseekTradingAgent
        
        config = {
            'api_key': 'test-key',
            'api_url': 'https://api.deepseek.com',
            'model': 'deepseek-chat'
        }
        
        agent = DeepseekTradingAgent(config)
        
        plan = {
            'candidates': [
                {'symbol': 'BTC', 'direction': 'LONG'},
                {'symbol': 'ETH', 'direction': 'INVALID'},  # Invalid direction
                {'symbol': 'SOL', 'direction': 'SHORT'},
            ]
        }
        
        validated = agent._validate_trading_plan(plan, [])
        
        self.assertEqual(len(validated['candidates']), 2)
        symbols = [c['symbol'] for c in validated['candidates']]
        self.assertIn('BTC', symbols)
        self.assertIn('SOL', symbols)
        self.assertNotIn('ETH', symbols)


if __name__ == '__main__':
    unittest.main()
