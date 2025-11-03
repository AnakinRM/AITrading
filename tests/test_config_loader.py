import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from src.utils.config_loader import ConfigLoader, get_config

@pytest.fixture
def config_file(tmp_path):
    config_content = """
    test_key: test_value

    nested:
      key1: value1
      key2: 123

    hyperliquid:
      account_address: ""
      secret_key: ""

    deepseek:
      api_key: ""

    trading:
        mode: "paper"
    """
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text(config_content)
    return str(config_path)

def test_load_config(config_file):
    loader = ConfigLoader(config_file)
    assert loader.get("test_key") == "test_value"
    assert loader.get("nested.key1") == "value1"
    assert loader.get("nested.key2") == 123

def test_get_section(config_file):
    loader = ConfigLoader(config_file)
    nested_section = loader.get_section("nested")
    assert nested_section == {"key1": "value1", "key2": 123}

def test_override_with_env(config_file):
    with patch.dict(os.environ, {
        "HYPERLIQUID_ACCOUNT_ADDRESS": "0x123",
        "HYPERLIQUID_SECRET_KEY": "abc",
        "DEEPSEEK_API_KEY": "xyz",
    }):
        loader = ConfigLoader(config_file)
        assert loader.get("hyperliquid.account_address") == "0x123"
        assert loader.get("hyperliquid.secret_key") == "abc"
        assert loader.get("deepseek.api_key") == "xyz"

def test_get_config_singleton(config_file):
    instance1 = get_config(config_file)
    instance2 = get_config()
    assert instance1 is instance2

