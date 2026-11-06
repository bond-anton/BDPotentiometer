"""Logging helper functions"""

import logging
from typing import Union


def get_logger(label: str, log_level: Union[int, None] = None) -> logging.Logger:
    """Creates logger"""
    logger = logging.getLogger(label)
    if log_level:
        logger.setLevel(log_level)
    else:
        logger.setLevel(logging.ERROR)
    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    for handler in logger.handlers:
        handler.setLevel(logger.level)
    return logger
