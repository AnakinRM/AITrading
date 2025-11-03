"""
Configuration loader module
"""
import os
import yaml
from typing import Dict, Any
from pathlib import Path


class ConfigLoader:
    """Load and manage configuration"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration loader
        
        Args:
            config_path: Path to configuration file
        """
        if config_path is None:
            # Default to config/config.yaml in project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Override with environment variables if present
        config = self._override_with_env(config)
        
        return config
    
    def _override_with_env(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Override configuration with environment variables"""
        # HyperLiquid
        if os.getenv('HYPERLIQUID_ACCOUNT_ADDRESS'):
            config['hyperliquid']['account_address'] = os.getenv('HYPERLIQUID_ACCOUNT_ADDRESS')
        if os.getenv('HYPERLIQUID_SECRET_KEY'):
            config['hyperliquid']['secret_key'] = os.getenv('HYPERLIQUID_SECRET_KEY')
        
        # Deepseek
        if os.getenv('DEEPSEEK_API_KEY'):
            config['deepseek']['api_key'] = os.getenv('DEEPSEEK_API_KEY')
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key (supports nested keys with dot notation)
        
        Args:
            key: Configuration key (e.g., 'hyperliquid.api_url')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section
        
        Args:
            section: Section name
        
        Returns:
            Configuration section as dictionary
        """
        return self.config.get(section, {})
    
    def validate(self) -> bool:
        """
        Validate configuration
        
        Returns:
            True if configuration is valid
        """
        # Check required fields
        required_fields = [
            'hyperliquid.api_url',
            'trading.trading_pairs',
            'risk.max_position_per_coin',
        ]
        
        for field in required_fields:
            if self.get(field) is None:
                raise ValueError(f"Required configuration field missing: {field}")
        
        # Validate API credentials if in live mode
        if self.get('trading.mode') == 'live':
            if not self.get('hyperliquid.account_address'):
                raise ValueError("HyperLiquid account address is required for live trading")
            if not self.get('hyperliquid.secret_key'):
                raise ValueError("HyperLiquid secret key is required for live trading")
        
        return True


# Global configuration instance
_config_instance = None


def get_config(config_path: str = None) -> ConfigLoader:
    """
    Get global configuration instance
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        ConfigLoader instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ConfigLoader(config_path)
    
    return _config_instance
