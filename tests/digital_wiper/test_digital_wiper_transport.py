"""Tests for SpiDigitalWiper transport injection."""

import unittest

from scietex.hal.spi import FakeSpiTransport

try:
    from src.BDPotentiometer import Potentiometer, SpiDigitalWiper
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, SpiDigitalWiper


class _RawSpiStub:
    """Transport-like object exposing a raw gpiozero-style handle."""

    def __init__(self) -> None:
        self.raw = object()

    def transfer(self, tx):
        """Return a zero-filled response frame."""
        return [0] * len(tx)

    def close(self) -> None:
        """No-op close."""


class TestSpiDigitalWiperTransport(unittest.TestCase):
    """
    Testing SpiDigitalWiper transport handling.
    """

    def setUp(self) -> None:
        """
        Set up Unittest
        """
        self.pot = Potentiometer(r_ab=10e3, r_w=75)

    def test_transport_stored(self):
        """
        Test injected transport is stored and exposed by both accessors.
        """
        fake = FakeSpiTransport()
        wiper = SpiDigitalWiper(potentiometer=self.pot, transport=fake)
        self.assertIs(wiper.transport, fake)
        self.assertIs(wiper.spi, fake)

    def test_no_transport(self):
        """
        Test absent transport resolves to None.
        """
        wiper = SpiDigitalWiper(spi=None, potentiometer=self.pot, max_value=128)
        self.assertIsNone(wiper.transport)
        self.assertIsNone(wiper.spi)
        wiper = SpiDigitalWiper(potentiometer=self.pot, transport=None)
        self.assertIsNone(wiper.transport)
        self.assertIsNone(wiper.spi)

    def test_spi_only_constructor_has_no_transport(self):
        """
        Test spi=None constructor keyword leaves transport unset.
        """
        wiper = SpiDigitalWiper(potentiometer=self.pot, spi=None)
        self.assertIsNone(wiper.transport)

    def test_transport_wins_over_spi(self):
        """
        Test an explicit transport takes precedence over the spi argument.
        """
        fake = FakeSpiTransport()
        wiper = SpiDigitalWiper(potentiometer=self.pot, spi=object(), transport=fake)
        self.assertIs(wiper.transport, fake)

    def test_invalid_transport_raises(self):
        """
        Test an object without transfer() is rejected.
        """
        with self.assertRaises(TypeError):
            SpiDigitalWiper(potentiometer=self.pot, transport=object())

    def test_transport_setter(self):
        """
        Test the transport setter accepts transports and clears on None.
        """
        wiper = SpiDigitalWiper(potentiometer=self.pot)
        fake = FakeSpiTransport()
        wiper.transport = fake
        self.assertIs(wiper.transport, fake)
        wiper.transport = None
        self.assertIsNone(wiper.transport)
        with self.assertRaises(TypeError):
            wiper.transport = object()

    def test_spi_accessor_returns_raw(self):
        """
        Test the compatibility accessor unwraps the raw handle when present.
        """
        stub = _RawSpiStub()
        wiper = SpiDigitalWiper(potentiometer=self.pot, transport=stub)
        self.assertIs(wiper.spi, stub.raw)

    def test_require_transport_raises_without_transport(self):
        """
        Test missing transport raises ConnectionError on access.
        """
        wiper = SpiDigitalWiper(potentiometer=self.pot)
        with self.assertRaises(ConnectionError):
            wiper._require_transport()


if __name__ == "__main__":
    unittest.main()
