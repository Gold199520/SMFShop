import pytest
from src.services.log_service import LogService

@pytest.fixture
def logger():
    return LogService("test.log")

def test_logger_creation():
    log = LogService("test.log")
    assert log is not None

def test_debug_logging(logger):
    logger.debug("Test debug message")

def test_info_logging(logger):
    logger.info("Test info message")

def test_warning_logging(logger):
    logger.warning("Test warning message")

def test_error_logging(logger):
    logger.error("Test error message")

def test_critical_logging(logger):
    logger.critical("Test critical message")

def test_setup_sentry_no_dsn(logger):
    logger.setup_sentry(None)
