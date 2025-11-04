"""
Test JSON schema validation for DeepSeek trading plan output
"""
import unittest
import json
from jsonschema import validate, ValidationError, Draft7Validator
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.constants import ALLOWED_SYMBOLS


# Define expected JSON schema for trading plan
TRADING_PLAN_SCHEMA = {
    "type": "object",
    "required": ["timestamp", "market_view", "candidates", "portfolio_constraints", "next_actions"],
    "properties": {
        "timestamp": {
            "type": "string",
            "format": "date-time"
        },
        "market_view": {
            "type": "object",
            "required": ["summary", "news_signals", "onchain_offchain_signals"],
            "properties": {
                "summary": {"type": "string"},
                "news_signals": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "onchain_offchain_signals": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        },
        "candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["symbol", "direction", "entry", "stop_loss", "take_profit", "position", "rationale"],
                "properties": {
                    "symbol": {
                        "type": "string",
                        "enum": ALLOWED_SYMBOLS
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["LONG", "SHORT"]
                    },
                    "entry": {
                        "type": "object",
                        "required": ["type", "price"],
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["limit", "market"]
                            },
                            "price": {
                                "oneOf": [
                                    {"type": "number"},
                                    {"type": "null"}
                                ]
                            }
                        }
                    },
                    "stop_loss": {
                        "oneOf": [
                            {"type": "number"},
                            {"type": "string"}
                        ]
                    },
                    "take_profit": {
                        "oneOf": [
                            {"type": "number"},
                            {"type": "string"},
                            {
                                "type": "array",
                                "items": {"type": "number"}
                            }
                        ]
                    },
                    "position": {
                        "type": "object",
                        "required": ["size_pct"],
                        "properties": {
                            "size_pct": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "leverage_hint": {
                                "oneOf": [
                                    {"type": "number", "minimum": 1},
                                    {"type": "null"}
                                ]
                            }
                        }
                    },
                    "rationale": {"type": "string"},
                    "risk_notes": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        },
        "portfolio_constraints": {
            "type": "object",
            "required": ["allowed_symbols", "skip_unavailable"],
            "properties": {
                "allowed_symbols": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ALLOWED_SYMBOLS
                    }
                },
                "max_parallel_positions": {"type": "integer", "minimum": 1},
                "skip_unavailable": {"type": "boolean"}
            }
        },
        "next_actions": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}


class TestJSONSchema(unittest.TestCase):
    """Test JSON schema validation for trading plans"""
    
    def test_valid_trading_plan(self):
        """Test that a valid trading plan passes schema validation"""
        valid_plan = {
            "timestamp": "2025-11-02T22:45:00Z",
            "market_view": {
                "summary": "Market is bullish",
                "news_signals": ["Fed holds rates"],
                "onchain_offchain_signals": ["BTC outflows increasing"]
            },
            "candidates": [
                {
                    "symbol": "BTC",
                    "direction": "LONG",
                    "entry": {
                        "type": "limit",
                        "price": 50000
                    },
                    "stop_loss": 48000,
                    "take_profit": [52000, 55000],
                    "position": {
                        "size_pct": 0.25,
                        "leverage_hint": 3
                    },
                    "rationale": "Strong technical setup",
                    "risk_notes": ["Watch funding rates"]
                }
            ],
            "portfolio_constraints": {
                "allowed_symbols": ALLOWED_SYMBOLS,
                "max_parallel_positions": 3,
                "skip_unavailable": True
            },
            "next_actions": ["place_orders"]
        }
        
        # Should not raise exception
        try:
            validate(instance=valid_plan, schema=TRADING_PLAN_SCHEMA)
        except ValidationError as e:
            self.fail(f"Valid plan failed validation: {e}")
    
    def test_invalid_symbol(self):
        """Test that invalid symbol fails validation"""
        invalid_plan = {
            "timestamp": "2025-11-02T22:45:00Z",
            "market_view": {
                "summary": "Market is bullish",
                "news_signals": [],
                "onchain_offchain_signals": []
            },
            "candidates": [
                {
                    "symbol": "INVALID",  # Not in ALLOWED_SYMBOLS
                    "direction": "LONG",
                    "entry": {"type": "market", "price": None},
                    "stop_loss": 100,
                    "take_profit": 200,
                    "position": {"size_pct": 0.1, "leverage_hint": None},
                    "rationale": "Test",
                    "risk_notes": []
                }
            ],
            "portfolio_constraints": {
                "allowed_symbols": ALLOWED_SYMBOLS,
                "skip_unavailable": True
            },
            "next_actions": []
        }
        
        with self.assertRaises(ValidationError):
            validate(instance=invalid_plan, schema=TRADING_PLAN_SCHEMA)
    
    def test_invalid_direction(self):
        """Test that invalid direction fails validation"""
        invalid_plan = {
            "timestamp": "2025-11-02T22:45:00Z",
            "market_view": {
                "summary": "Test",
                "news_signals": [],
                "onchain_offchain_signals": []
            },
            "candidates": [
                {
                    "symbol": "BTC",
                    "direction": "HOLD",  # Invalid, should be LONG or SHORT
                    "entry": {"type": "market", "price": None},
                    "stop_loss": 100,
                    "take_profit": 200,
                    "position": {"size_pct": 0.1, "leverage_hint": None},
                    "rationale": "Test",
                    "risk_notes": []
                }
            ],
            "portfolio_constraints": {
                "allowed_symbols": ALLOWED_SYMBOLS,
                "skip_unavailable": True
            },
            "next_actions": []
        }
        
        with self.assertRaises(ValidationError):
            validate(instance=invalid_plan, schema=TRADING_PLAN_SCHEMA)
    
    def test_missing_required_fields(self):
        """Test that missing required fields fail validation"""
        incomplete_plan = {
            "timestamp": "2025-11-02T22:45:00Z",
            # Missing market_view
            "candidates": [],
            "portfolio_constraints": {
                "allowed_symbols": ALLOWED_SYMBOLS,
                "skip_unavailable": True
            },
            "next_actions": []
        }
        
        with self.assertRaises(ValidationError):
            validate(instance=incomplete_plan, schema=TRADING_PLAN_SCHEMA)
    
    def test_invalid_position_size(self):
        """Test that position size outside 0-1 range fails"""
        invalid_plan = {
            "timestamp": "2025-11-02T22:45:00Z",
            "market_view": {
                "summary": "Test",
                "news_signals": [],
                "onchain_offchain_signals": []
            },
            "candidates": [
                {
                    "symbol": "BTC",
                    "direction": "LONG",
                    "entry": {"type": "market", "price": None},
                    "stop_loss": 100,
                    "take_profit": 200,
                    "position": {
                        "size_pct": 1.5,  # Invalid, should be 0-1
                        "leverage_hint": None
                    },
                    "rationale": "Test",
                    "risk_notes": []
                }
            ],
            "portfolio_constraints": {
                "allowed_symbols": ALLOWED_SYMBOLS,
                "skip_unavailable": True
            },
            "next_actions": []
        }
        
        with self.assertRaises(ValidationError):
            validate(instance=invalid_plan, schema=TRADING_PLAN_SCHEMA)
    
    def test_both_long_and_short_allowed(self):
        """Test that both LONG and SHORT directions are valid"""
        plan_with_both = {
            "timestamp": "2025-11-02T22:45:00Z",
            "market_view": {
                "summary": "Mixed signals",
                "news_signals": [],
                "onchain_offchain_signals": []
            },
            "candidates": [
                {
                    "symbol": "BTC",
                    "direction": "LONG",
                    "entry": {"type": "market", "price": None},
                    "stop_loss": 48000,
                    "take_profit": 52000,
                    "position": {"size_pct": 0.2, "leverage_hint": 3},
                    "rationale": "Bullish",
                    "risk_notes": []
                },
                {
                    "symbol": "ETH",
                    "direction": "SHORT",
                    "entry": {"type": "limit", "price": 3000},
                    "stop_loss": 3200,
                    "take_profit": 2800,
                    "position": {"size_pct": 0.15, "leverage_hint": 2},
                    "rationale": "Bearish",
                    "risk_notes": []
                }
            ],
            "portfolio_constraints": {
                "allowed_symbols": ALLOWED_SYMBOLS,
                "skip_unavailable": True
            },
            "next_actions": ["place_orders"]
        }
        
        # Should not raise exception
        try:
            validate(instance=plan_with_both, schema=TRADING_PLAN_SCHEMA)
        except ValidationError as e:
            self.fail(f"Plan with LONG and SHORT failed validation: {e}")


if __name__ == '__main__':
    unittest.main()
