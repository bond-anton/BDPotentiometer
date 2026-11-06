"""Tests for SpiDigitalWiper SPI setter."""

import unittest

try:
    from src.BDPotentiometer import Potentiometer, SpiDigitalWiper
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, SpiDigitalWiper


class _StubSpi:
    """Minimal SPI transport used to exercise the setter."""

    def __init__(self):
        self.calls = []

    def transfer(self, tx):
        """Record the frame and return a zero response."""
        self.calls.append(list(tx))
        return [0] * len(tx)

    def close(self):
        """No-op close."""


class TestSpiDigitalWiperSpiSetter(unittest.TestCase):
    """
    Testing SpiDigitalWiper SPI setter.
    """

    def setUp(self) -> None:
        """
        Set up Unittest
        """
        self.pot = Potentiometer(r_ab=10e3, r_w=75)
        self.spi_digital_wiper = SpiDigitalWiper(
            spi=None, potentiometer=self.pot, max_value=128
        )

    def test_set_spi_none(self):
        """
        Test setting SPI interface to None.
        """
        self.spi_digital_wiper.spi = None
        self.assertIsNone(self.spi_digital_wiper.spi)

    def test_set_spi_invalid(self):
        """
        Test setting SPI interface to an invalid object.
        """
        self.spi_digital_wiper.spi = object()
        self.assertIsNone(self.spi_digital_wiper.spi)

    def test_set_spi_valid(self):
        """
        Test that a valid SPI interface is stored and not overwritten.
        """
        spi = _StubSpi()
        self.spi_digital_wiper.spi = spi
        self.assertIs(self.spi_digital_wiper.spi, spi)


if __name__ == "__main__":
    unittest.main()
