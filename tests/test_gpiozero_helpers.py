"""Tests for the gpiozero dual-CS SPI helper."""

import importlib
import sys
import unittest
from unittest import mock

try:
    import BDPotentiometer.__gpiozero_helpers as helpers
except ModuleNotFoundError:
    from src.BDPotentiometer import __gpiozero_helpers as helpers


class TestGpiozeroHelpers(unittest.TestCase):
    """The dual-CS helper degrades to a no-op without the Pi pin backend."""

    def test_helper_is_callable(self):
        """The helper is exported as a callable on every host."""
        self.assertTrue(callable(helpers.fix_gpiozero_dual_cs_spi))

    def test_helper_without_pin_backend_does_not_raise(self):
        """A host without gpiozero's RPi pin backend gets a no-op stub."""
        blocked = {"gpiozero.pins.rpigpio": None, "RPi.GPIO": None}
        try:
            with mock.patch.dict(sys.modules, blocked):
                reloaded = importlib.reload(helpers)
                self.assertIsNone(reloaded.fix_gpiozero_dual_cs_spi())
        finally:
            importlib.reload(helpers)


if __name__ == "__main__":
    unittest.main()
