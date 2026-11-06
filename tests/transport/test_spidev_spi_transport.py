"""Tests for SpiDevTransport using a stubbed spidev module."""

import sys
import types
import unittest
from unittest import mock

try:
    from src.BDPotentiometer.transport import (
        SpiDevTransport,
        TransportClosed,
        TransportError,
    )
except ModuleNotFoundError:
    from BDPotentiometer.transport import (
        SpiDevTransport,
        TransportClosed,
        TransportError,
    )


class _StubSpiDev:
    """Stand-in for spidev.SpiDev that records every call."""

    return_len = None

    def __init__(self):
        self.open_args = None
        self.calls = []
        self.closed = False

    def open(self, bus, device):
        """Record the device node selection."""
        self.open_args = (bus, device)

    def xfer2(self, tx):
        """Record the transfer and return a frame of the same length."""
        self.calls.append(("xfer2", list(tx)))
        length = self.return_len if self.return_len is not None else len(tx)
        return [0] * length

    def xfer(self, tx):
        """Fail: the adapter must never use xfer."""
        self.calls.append(("xfer", list(tx)))
        raise AssertionError("xfer must not be used")

    def close(self):
        """Record the close."""
        self.closed = True


class _FailingOpenSpiDev(_StubSpiDev):
    """Stand-in whose open() fails like a missing device node."""

    def open(self, bus, device):
        raise PermissionError(13, "Permission denied")


class _ConfigFailingSpiDev(_StubSpiDev):
    """Stand-in whose mode assignment fails like a rejected bus setting."""

    instances = []

    def __init__(self):
        super().__init__()
        _ConfigFailingSpiDev.instances.append(self)

    def __setattr__(self, name, value):
        if name == "mode":
            raise OSError(22, "Invalid argument")
        super().__setattr__(name, value)


class _TransferFailingSpiDev(_StubSpiDev):
    """Stand-in whose transfer fails at the kernel boundary."""

    def xfer2(self, tx):
        raise OSError(5, "Input/output error")


class _FailingCloseSpiDev(_StubSpiDev):
    """Stand-in whose first close() fails before succeeding on retry."""

    def __init__(self):
        super().__init__()
        self.close_calls = 0

    def close(self):
        """Fail the first close, then record success."""
        self.close_calls += 1
        if self.close_calls == 1:
            raise OSError(5, "Input/output error")
        self.closed = True


def _stub_module(spi_dev_class=_StubSpiDev):
    module = types.ModuleType("spidev")
    module.SpiDev = spi_dev_class
    return module


class TestSpiDevTransport(unittest.TestCase):
    """
    Testing the spidev-backed transport without hardware.
    """

    def tearDown(self) -> None:
        _ConfigFailingSpiDev.instances = []

    def test_open_applies_default_config(self) -> None:
        """
        Construction opens the requested bus/device and applies config.
        """
        with mock.patch.dict(sys.modules, {"spidev": _stub_module()}):
            transport = SpiDevTransport(device=1)
        self.assertIsInstance(transport.raw, _StubSpiDev)
        self.assertEqual(transport.raw.open_args, (0, 1))
        self.assertEqual(transport.raw.max_speed_hz, 500_000)
        self.assertEqual(transport.raw.mode, 0)
        self.assertEqual(transport.raw.bits_per_word, 8)
        self.assertIs(transport.raw.lsbfirst, False)
        self.assertIs(transport.raw.cshigh, False)
        self.assertFalse(transport.closed)

    def test_custom_config_is_applied(self) -> None:
        """
        Constructor arguments override every bus parameter.
        """
        with mock.patch.dict(sys.modules, {"spidev": _stub_module()}):
            transport = SpiDevTransport(
                bus=2,
                device=3,
                max_speed_hz=1_000_000,
                mode=3,
                bits_per_word=16,
                lsbfirst=True,
            )
        self.assertEqual(transport.raw.open_args, (2, 3))
        self.assertEqual(transport.raw.max_speed_hz, 1_000_000)
        self.assertEqual(transport.raw.mode, 3)
        self.assertEqual(transport.raw.bits_per_word, 16)
        self.assertIs(transport.raw.lsbfirst, True)
        self.assertIs(transport.raw.cshigh, False)

    def test_transfer_uses_xfer2(self) -> None:
        """
        transfer() delegates to xfer2 and never calls xfer.
        """
        with mock.patch.dict(sys.modules, {"spidev": _stub_module()}):
            transport = SpiDevTransport()
            transport.transfer([0x0C, 0])
        self.assertEqual(transport.raw.calls, [("xfer2", [0x0C, 0])])
        self.assertNotIn("xfer", [name for name, _ in transport.raw.calls])

    def test_transfer_length_mismatch_raises(self) -> None:
        """
        A short response raises TransportError.
        """
        with mock.patch.dict(sys.modules, {"spidev": _stub_module()}):
            transport = SpiDevTransport()
            transport.raw.return_len = 1
            with self.assertRaises(TransportError):
                transport.transfer([0x0C, 0])

    def test_close_blocks_transfers(self) -> None:
        """
        close() is idempotent and blocks later transfers.
        """
        with mock.patch.dict(sys.modules, {"spidev": _stub_module()}):
            transport = SpiDevTransport()
            transport.close()
            transport.close()
            self.assertTrue(transport.closed)
            self.assertTrue(transport.raw.closed)
            with self.assertRaises(TransportClosed):
                transport.transfer([0x0C, 0])

    def test_failed_close_leaves_transport_open(self) -> None:
        """
        A failing handle close leaves closed False and a second close retries.
        """
        with mock.patch.dict(
            sys.modules, {"spidev": _stub_module(_FailingCloseSpiDev)}
        ):
            transport = SpiDevTransport()
        with self.assertRaises(OSError):
            transport.close()
        self.assertFalse(transport.closed)
        transport.close()
        self.assertEqual(transport.raw.close_calls, 2)
        self.assertTrue(transport.closed)

    def test_open_failure_is_wrapped(self) -> None:
        """
        An OSError from open() becomes TransportError with setup hints.
        """
        with (
            mock.patch.dict(sys.modules, {"spidev": _stub_module(_FailingOpenSpiDev)}),
            self.assertRaises(TransportError) as context,
        ):
            SpiDevTransport(bus=0, device=0)
        message = str(context.exception)
        self.assertIn("/dev/spidev0.0", message)
        self.assertIn("gpio", message)
        self.assertIn("dtparam=spi=on", message)

    def test_config_failure_is_wrapped_and_closes_handle(self) -> None:
        """
        A rejected bus setting becomes TransportError and closes the handle.
        """
        _ConfigFailingSpiDev.instances = []
        with (
            mock.patch.dict(
                sys.modules, {"spidev": _stub_module(_ConfigFailingSpiDev)}
            ),
            self.assertRaises(TransportError) as context,
        ):
            SpiDevTransport(bus=1, device=2)
        message = str(context.exception)
        self.assertIn("/dev/spidev1.2", message)
        self.assertIsInstance(context.exception.__cause__, OSError)
        self.assertTrue(_ConfigFailingSpiDev.instances[0].closed)

    def test_transfer_oserror_is_not_wrapped(self) -> None:
        """
        An OSError from xfer2 propagates unchanged; transfer wrapping is out of scope.
        """
        with mock.patch.dict(
            sys.modules, {"spidev": _stub_module(_TransferFailingSpiDev)}
        ):
            transport = SpiDevTransport()
            with self.assertRaises(OSError) as context:
                transport.transfer([0x0C, 0])
        self.assertIs(type(context.exception), OSError)

    def test_missing_spidev_raises_import_error(self) -> None:
        """
        A missing spidev package raises ImportError naming the extra.
        """
        with (
            mock.patch.dict(sys.modules, {"spidev": None}),
            self.assertRaises(ImportError) as context,
        ):
            SpiDevTransport()
        message = str(context.exception)
        self.assertIn("BDPotentiometer[spi]", message)
        self.assertIn("spidev", message)


if __name__ == "__main__":
    unittest.main()
