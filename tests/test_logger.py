"""Tests for the shared logger factory."""

import logging
import unittest

try:
    from src.BDPotentiometer.__logger import get_logger
except ModuleNotFoundError:
    from BDPotentiometer.__logger import get_logger


class TestGetLogger(unittest.TestCase):
    """
    Testing logger creation and reuse.
    """

    NAMES = ("bdpot-test-single-handler", "bdpot-test-log-level")

    def tearDown(self) -> None:
        for name in self.NAMES:
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
