"""Tests for GpiozeroSpiTransport using a stubbed SPI object."""

import unittest
from unittest import mock

try:
    from src.BDPotentiometer.transport import TransportClosed, TransportError
    from src.BDPotentiometer.transport import gpiozero_spi as gpiozero_spi_module
    from src.BDPotentiometer.transport.gpiozero_spi import GpiozeroSpiTransport
except ModuleNotFoundError:
    from BDPotentiometer.transport import TransportClosed, TransportError
    from BDPotentiometer.transport import gpiozero_spi as gpiozero_spi_module
    from BDPotentiometer.transport.gpiozero_spi import GpiozeroSpiTransport


class _StubSpi:
    """Stand-in for a gpiozero SPI object that records every call."""

    return_len = None

    def __init__(self):
        self.calls = []
        self.closed = False

    def transfer(self, tx):
        """Record the frame and return a response of configurable length."""
        self.calls.append(list(tx))
        length = self.return_len if self.return_len is not None else len(tx)
        return [0] * length

    def close(self):
        """Record the close."""
        self.closed = True


class _StubGpiozeroHandle:
    """Stand-in for the private gpiozero device that owns the raw SPI."""

    instances = []

    def __init__(self, **spi_args):
        self.spi_args = spi_args
        self.raw = _StubSpi()
        self.close_calls = 0
        _StubGpiozeroHandle.instances.append(self)

    def close(self):
        """Record the close instead of touching hardware."""
        self.close_calls += 1


class TestGpiozeroSpiTransport(unittest.TestCase):
    """
    Testing the gpiozero-backed transport without hardware.
    """

    def test_wraps_existing_spi(self) -> None:
        """
        An injected SPI object is exposed as raw and not replaced.
        """
        stub = _StubSpi()
        transport = GpiozeroSpiTransport(spi=stub)
        self.assertIs(transport.raw, stub)
        self.assertFalse(transport.closed)

    def test_transfer_delegates(self) -> None:
        """
        transfer() forwards the frame to the wrapped SPI object.
        """
        stub = _StubSpi()
        transport = GpiozeroSpiTransport(spi=stub)
        response = transport.transfer([0x0C, 0])
        self.assertEqual(stub.calls, [[0x0C, 0]])
        self.assertEqual(response, [0, 0])
        self.assertIsInstance(response, list)

    def test_transfer_length_mismatch_raises(self) -> None:
        """
        A response whose length differs from the request raises TransportError.
        """
        stub = _StubSpi()
        stub.return_len = 1
        transport = GpiozeroSpiTransport(spi=stub)
        with self.assertRaises(TransportError):
            transport.transfer([0x0C, 0])

    def test_close_leaves_injected_spi_open(self) -> None:
        """
        close() is idempotent, keeps a caller-supplied SPI open, and blocks transfers.
        """
        stub = _StubSpi()
        transport = GpiozeroSpiTransport(spi=stub)
        transport.close()
        transport.close()
        self.assertTrue(transport.closed)
        self.assertFalse(stub.closed)
        with self.assertRaises(TransportClosed):
            transport.transfer([0x0C, 0])

    def test_default_construction_closes_owned_handle(self) -> None:
        """
        Without an injected SPI the transport builds a handle and closes it once.
        """
        _StubGpiozeroHandle.instances = []
        with mock.patch.object(
            gpiozero_spi_module, "_GpiozeroSpiHandle", _StubGpiozeroHandle
        ):
            transport = GpiozeroSpiTransport(device=1)
        handle = _StubGpiozeroHandle.instances[0]
        self.assertEqual(handle.spi_args, {"device": 1})
        self.assertIs(transport.raw, handle.raw)
        self.assertFalse(transport.closed)
        transport.close()
        transport.close()
        self.assertEqual(handle.close_calls, 1)
        self.assertFalse(handle.raw.closed)

    def test_spi_args_match_gpiozero_constructor(self) -> None:
        """
        The adapter accepts exactly the keywords gpiozero's SPI device accepts.
        """
        expected = "port device clock_pin mosi_pin miso_pin select_pin"
        actual = GpiozeroSpiTransport._SPI_ARGS
        self.assertEqual(set(actual), set(expected.split()))
        self.assertNotIn("channel", actual)


if __name__ == "__main__":
    unittest.main()
