"""Logging helper functions"""

from typing import Union
import logging


def get_logger(label: str, log_level: Union[int, None] = None) -> logging.Logger:
    """Creates logger"""
    logger = logging.getLogger(label)
    if log_level:
        logger.setLevel(log_level)
    else:
        logger.setLevel(logging.ERROR)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logger.level)
    # create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    return logger
