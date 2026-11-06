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

    NAMES = (
        "bdpot-test-single-handler",
        "bdpot-test-log-level",
        "bdpot-test-log-notset",
        "bdpot-test-keep-level",
        "bdpot-test-concurrent",
    )

    def tearDown(self) -> None:
        for name in self.NAMES:
            logger = logging.getLogger(name)
            for handler in list(logger.handlers):
                logger.removeHandler(handler)
                handler.close()
            logger.setLevel(logging.NOTSET)
            if hasattr(logger, "_bdpot_configured"):
                del logger._bdpot_configured

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
