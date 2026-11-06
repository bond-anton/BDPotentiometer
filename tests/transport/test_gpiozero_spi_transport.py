"""Tests for GpiozeroSpiTransport using a stubbed SPI object."""

import unittest

try:
    from src.BDPotentiometer.transport import TransportClosed, TransportError
    from src.BDPotentiometer.transport.gpiozero_spi import GpiozeroSpiTransport
except ModuleNotFoundError:
    from BDPotentiometer.transport import TransportClosed, TransportError
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

    def test_close_blocks_transfers(self) -> None:
        """
        close() is idempotent, closes the SPI object, and blocks transfers.
        """
        stub = _StubSpi()
        transport = GpiozeroSpiTransport(spi=stub)
        transport.close()
        transport.close()
        self.assertTrue(transport.closed)
        self.assertTrue(stub.closed)
        with self.assertRaises(TransportClosed):
            transport.transfer([0x0C, 0])

    def test_spi_args_match_legacy_constructor(self) -> None:
        """
        The adapter accepts exactly the legacy gpiozero SPI keyword set.
        """
        expected = "channel port device clock_pin mosi_pin miso_pin select_pin"
        actual = GpiozeroSpiTransport._SPI_ARGS
        self.assertEqual(set(actual), set(expected.split()))


if __name__ == "__main__":
    unittest.main()
