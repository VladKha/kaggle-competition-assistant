import logging


def get_logger(name: str) -> logging.Logger:
    """Returns a logger for usage in the library"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.NOTSET)             # Do not set a level, let the user control it
    logger.addHandler(logging.NullHandler())    # Prevent output by default
    return logger
