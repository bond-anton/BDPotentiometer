"""Tests for the shared logger factory."""

import logging
import threading
import unittest

try:
    from src.BDPotentiometer.__logger import get_logger
except ModuleNotFoundError:
    from BDPotentiometer.__logger import get_logger


class TestGetLogger(unittest.TestCase):
    """
    Testing logger creation and reuse.
    """

    def tearDown(self) -> None:
        for name in list(logging.Logger.manager.loggerDict):
            if not name.startswith("bdpot-test-"):
                continue
            logger = logging.getLogger(name)
            for handler in list(logger.handlers):
                logger.removeHandler(handler)
                handler.close()
            logger.setLevel(logging.NOTSET)

    def test_repeated_calls_keep_one_handler(self) -> None:
        """
        Calling get_logger twice for one name attaches a single handler.
        """
        get_logger("bdpot-test-single-handler")
        logger = get_logger("bdpot-test-single-handler")
        self.assertEqual(len(logger.handlers), 1)
        self.assertTrue(logger.propagate)

    def test_latest_level_takes_effect(self) -> None:
        """
        A level passed on a later call updates the logger and its handler.
        """
        get_logger("bdpot-test-log-level", logging.ERROR)
        logger = get_logger("bdpot-test-log-level", logging.DEBUG)
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(logger.handlers[0].level, logging.DEBUG)
        self.assertEqual(
            logger.handlers[0].formatter._fmt,
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def test_notset_level_is_honoured(self) -> None:
        """
        logging.NOTSET is applied instead of falling back to ERROR.
        """
        logger = get_logger("bdpot-test-log-notset", logging.NOTSET)
        self.assertEqual(logger.level, logging.NOTSET)
        self.assertEqual(logger.handlers[0].level, logging.NOTSET)

    def test_later_call_without_level_keeps_configuration(self) -> None:
        """
        A later call without log_level leaves an existing DEBUG level intact.
        """
        get_logger("bdpot-test-keep-level", logging.DEBUG)
        logger = get_logger("bdpot-test-keep-level")
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(logger.handlers[0].level, logging.DEBUG)

    def test_foreign_handler_is_not_releveled(self) -> None:
        """
        An explicit level only touches the handler installed by this module.
        """
        logger = logging.getLogger("bdpot-test-foreign-handler")
        foreign = logging.NullHandler()
        foreign.setLevel(logging.WARNING)
        logger.addHandler(foreign)

        get_logger("bdpot-test-foreign-handler", logging.DEBUG)

        self.assertEqual(foreign.level, logging.WARNING)
        package_handlers = [h for h in logger.handlers if h is not foreign]
        self.assertEqual(len(package_handlers), 1)
        self.assertEqual(package_handlers[0].level, logging.DEBUG)

    def test_cleared_handler_is_reattached(self) -> None:
        """
        Clearing the handlers does not prevent the package handler coming back.
        """
        get_logger("bdpot-test-cleared-handler", logging.DEBUG)
        logger = logging.getLogger("bdpot-test-cleared-handler")
        logger.handlers.clear()

        logger = get_logger("bdpot-test-cleared-handler")

        self.assertEqual(len(logger.handlers), 1)
        self.assertEqual(logger.level, logging.DEBUG)
        self.assertEqual(logger.handlers[0].level, logging.DEBUG)

    def test_concurrent_calls_attach_one_handler(self) -> None:
        """
        Concurrent first calls for one name attach a single handler.
        """
        barrier = threading.Barrier(4)

        def call() -> None:
            barrier.wait()
            get_logger("bdpot-test-concurrent")

        threads = [threading.Thread(target=call) for _ in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        logger = logging.getLogger("bdpot-test-concurrent")
        self.assertEqual(len(logger.handlers), 1)
