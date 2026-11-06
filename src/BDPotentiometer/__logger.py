"""Logger factory used by every device class.

Each device gets its own named logger so that a single device can be traced
without enabling logging for the whole package.
"""

import logging
from typing import Union


def get_logger(label: str, log_level: Union[int, None] = None) -> logging.Logger:
    """
    Return the named logger `label`, configured once.

    The level defaults to `logging.ERROR` when `log_level` is falsy. On first use
    the logger gets exactly one `logging.StreamHandler` with the package format;
    later calls reuse that handler and re-apply the logger level to every handler,
    so changing `log_level` on a later call takes effect.

    :param label: Logger name, also used to look up an already configured logger.
    :param log_level: Logging level such as `logging.DEBUG`; defaults to `logging.ERROR`.
    :return: Configured logger.
    """
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
