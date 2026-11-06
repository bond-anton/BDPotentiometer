"""Tests for SPI and I2C transport protocols."""

import unittest

try:
    from src.BDPotentiometer.transport import (
        FakeSpiTransport,
        I2cTransport,
        SpiTransport,
        is_spi_transport,
    )
except ModuleNotFoundError:
    from BDPotentiometer.transport import (
        FakeSpiTransport,
        I2cTransport,
        SpiTransport,
        is_spi_transport,
    )


class _I2cBackend:
    """Minimal structural I2C backend."""

    def write(self, data):
        """Write data."""

    def read(self, nbytes):
        """Read nbytes."""
        return b""

    def write_read(self, tx, nbytes):
        """Write then read."""
        return b""

    def close(self):
        """Close the backend."""


class TestSpiTransportProtocol(unittest.TestCase):
    """
    Testing structural SPI transport admission.
    """

    def test_fake_is_spi_transport(self) -> None:
        """
        FakeSpiTransport satisfies is_spi_transport.
        """
        self.assertTrue(is_spi_transport(FakeSpiTransport()))

    def test_plain_object_is_not_spi_transport(self) -> None:
        """
        An object without transfer() is rejected.
        """
        self.assertFalse(is_spi_transport(object()))

    def test_non_callable_transfer_is_not_spi_transport(self) -> None:
        """
        A non-callable transfer attribute is rejected.
        """

        class _NotCallable:
            transfer = None

        self.assertFalse(is_spi_transport(_NotCallable()))

    def test_fake_is_instance_of_spi_protocol(self) -> None:
        """
        FakeSpiTransport satisfies the runtime-checkable SpiTransport protocol.
        """
        self.assertIsInstance(FakeSpiTransport(), SpiTransport)

    def test_i2c_protocol_is_structural(self) -> None:
        """
        I2cTransport admits objects exposing the four I2C methods.
        """
        self.assertIsInstance(_I2cBackend(), I2cTransport)
        self.assertNotIsInstance(object(), I2cTransport)


if __name__ == "__main__":
    unittest.main()
