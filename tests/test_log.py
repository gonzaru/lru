import logging
import log


def test_setup():
    """Test that log.setup configures a logger correctly."""
    logger = log.setup("test-logger")
    assert logger.name == "test-logger"
    assert len(logger.handlers) > 0
    assert logger.level == logging.ERROR
    assert isinstance(logger.handlers[0], logging.StreamHandler)
