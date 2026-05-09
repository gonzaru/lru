"""log"""

import logging


def setup(name: str) -> logging.Logger:
    """Setup and configure the application logger."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
        hdlr = logging.StreamHandler()
        hdlr.setFormatter(fmt)

        logger.setLevel(logging.ERROR)
        logger.addHandler(hdlr)

    return logger
