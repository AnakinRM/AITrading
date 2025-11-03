'''
Tests for the logger module
'''
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from pathlib import Path

from src.utils.logger import Logger, get_logger


def test_logger_creation(tmp_path):
    """Test logger creation and basic logging."""
    log_file = tmp_path / "test.log"
    logger = Logger("test_logger", log_file=str(log_file))

    logger.info("This is an info message")
    logger.warning("This is a warning message")

    assert log_file.exists()
    log_content = log_file.read_text()
    assert "This is an info message" in log_content
    assert "This is a warning message" in log_content


def test_get_logger_singleton(tmp_path):
    """Test that get_logger returns a singleton instance."""
    log_file = tmp_path / "singleton.log"
    logger1 = get_logger("singleton", log_file=str(log_file))
    logger2 = get_logger("singleton")

    assert logger1 is logger2
