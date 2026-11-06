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

# Guards handler installation so that two threads calling `get_logger` for the
# same label cannot attach two handlers.
_LOCK = threading.Lock()

_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Marks the one handler this module owns. Tagging the handler keeps the package
# handler distinguishable from handlers the application installs on the same
# logger, so an explicit level is never applied to application handlers.
_PACKAGE_HANDLER_ATTR = "_bdpot_package_handler"


def _package_handler(logger: logging.Logger) -> logging.Handler | None:
    """Return the handler installed by this module, if it is still attached."""
    for handler in logger.handlers:
        if getattr(handler, _PACKAGE_HANDLER_ATTR, False):
            return handler
    return None


def get_logger(label: str, log_level: int | None = None) -> logging.Logger:
    """
    Return the named logger `label`, configured once.

    The level defaults to `logging.ERROR` when `log_level` is None. On first use
    the logger gets exactly one tagged `logging.StreamHandler` with the package
    format. Later calls with `log_level=None` leave the level and handlers
    untouched unless the package handler was removed, in which case it is
    re-attached at the logger's current level. An explicit `log_level` is
    applied on every call to the logger and to the package handler only;
    handlers installed by the application are never re-leveled. Any int level,
    including `logging.NOTSET`, is applied as given; only `None` selects the
    default `logging.ERROR`.

    The logger keeps ``propagate = True``, so its records also reach the
    application's root handlers and may be duplicated if the application adds
    its own handler.

    :param label: Logger name, also used to look up an already configured logger.
    :param log_level: Logging level such as `logging.DEBUG`; defaults to `logging.ERROR`.
    :return: Configured logger.
    """
    logger = logging.getLogger(label)
    with _LOCK:
        handler = _package_handler(logger)
        if handler is None:
            if log_level is not None:
                level = log_level
                logger.setLevel(level)
            elif logger.level == logging.NOTSET:
                level = logging.ERROR
                logger.setLevel(level)
            else:
                # Re-attach after application code cleared the handlers without
                # discarding the level configured by an earlier call.
                level = logger.level
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(_FORMAT))
            handler.setLevel(level)
            setattr(handler, _PACKAGE_HANDLER_ATTR, True)
            logger.addHandler(handler)
        elif log_level is not None:
            logger.setLevel(log_level)
            handler.setLevel(log_level)
        logger.propagate = True
    return logger
