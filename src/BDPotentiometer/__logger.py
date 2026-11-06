"""Logger factory used by every device class.

Each device gets its own named logger so that a single device can be traced
without enabling logging for the whole package.

Loggers keep ``propagate = True``: a record emitted here also reaches the
application's root handlers. If the application installs its own handler at the
root (or on a parent logger), the same record may be printed twice. Disable
propagation on the returned logger if that is not wanted.
"""

import logging
import threading
from typing import Union

# Guards handler installation so that two threads calling `get_logger` for the
# same label cannot attach two handlers.
_LOCK = threading.Lock()

# Names of already configured loggers. Kept here instead of a private attribute
# on the Logger because `logging.Logger` does not declare arbitrary attributes.
_bdpot_configured: set[str] = set()


def get_logger(label: str, log_level: Union[int, None] = None) -> logging.Logger:
    """
    Return the named logger `label`, configured only once.

    The level defaults to `logging.ERROR` when `log_level` is None. On first use
    the logger gets exactly one `logging.StreamHandler` with the package format.
    Later calls with `log_level=None` leave the level and handlers untouched, so
    a device configured at DEBUG is not reset by another device that omits
    `log_level`. An explicit `log_level` is applied on every call, to the logger
    and to its handlers. Any int level, including `logging.NOTSET`, is applied
    as given; only `None` selects the default `logging.ERROR`.

    The logger keeps ``propagate = True``, so its records also reach the
    application's root handlers and may be duplicated if the application adds
    its own handler.

    :param label: Logger name, also used to look up an already configured logger.
    :param log_level: Logging level such as `logging.DEBUG`; defaults to `logging.ERROR`.
    :return: Configured logger.
    """
    logger = logging.getLogger(label)
    with _LOCK:
        if label not in _bdpot_configured:
            level = logging.ERROR if log_level is None else log_level
            logger.setLevel(level)
            ch = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            ch.setFormatter(formatter)
            ch.setLevel(level)
            logger.addHandler(ch)
            logger.propagate = True
            _bdpot_configured.add(label)
        elif log_level is not None:
            logger.setLevel(log_level)
            for handler in logger.handlers:
                handler.setLevel(log_level)
    return logger
