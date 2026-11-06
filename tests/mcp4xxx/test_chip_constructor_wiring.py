"""Tests for chip constructor transport wiring."""

import unittest
from unittest import mock

try:
    from src.BDPotentiometer.mcp4xxx import MCP4231, MCP4232, MCP4251
    from src.BDPotentiometer.mcp4xxx import mcp4xxx as mcp4xxx_module
    from src.BDPotentiometer.transport import FakeSpiTransport
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx import MCP4231, MCP4232, MCP4251
    from BDPotentiometer.mcp4xxx import mcp4xxx as mcp4xxx_module
    from BDPotentiometer.transport import FakeSpiTransport


class _StubSpi:
    """Minimal transport used to exercise the explicit spi= path."""

    def __init__(self):
        self.calls = []

    def transfer(self, tx):
        """Record the frame and return a zero response."""
        self.calls.append(list(tx))
        return [0, 0]

    def close(self):
        """No-op close."""


class TestMCP4xxxConstructorWiring(unittest.TestCase):
    """
    Testing how chip constructors build or accept a transport.
    """

    def test_no_spi_kwargs_builds_default_transport(self):
        """
        A bare constructor still builds the default gpiozero transport.
        """
        with mock.patch.object(mcp4xxx_module, "GpiozeroSpiTransport") as adapter:
            pot = MCP4231(r_ab=10e3)
        adapter.assert_called_once_with()
        self.assertIs(pot.transport, adapter.return_value)

    def test_device_kwarg_builds_gpiozero_transport(self):
        """
        device= builds a GpiozeroSpiTransport with that device number.
        """
        with mock.patch.object(mcp4xxx_module, "GpiozeroSpiTransport") as adapter:
            pot = MCP4231(r_ab=10e3, device=0)
        adapter.assert_called_once_with(device=0)
        self.assertIs(pot.transport, adapter.return_value)

    def test_pin_kwargs_forwarded(self):
        """
        All legacy SPI keyword arguments are forwarded to the adapter.
        """
        with mock.patch.object(mcp4xxx_module, "GpiozeroSpiTransport") as adapter:
            MCP4231(r_ab=10e3, port=0, device=1, clock_pin=11)
        adapter.assert_called_once_with(port=0, device=1, clock_pin=11)

    def test_channel_kwarg_is_rejected(self):
        """
        channel= is not an accepted constructor keyword and is rejected.
        """
        with mock.patch.object(mcp4xxx_module, "GpiozeroSpiTransport") as adapter:
            self.assertRaises(TypeError, MCP4231, r_ab=10e3, channel=1, device=0)
        adapter.assert_not_called()

    def test_mcp4xxx_forwards_port_and_device(self):
        """
        The base MCP4xxx constructor forwards port/device to the adapter.
        """
        with mock.patch.object(mcp4xxx_module, "GpiozeroSpiTransport") as adapter:
            pot = mcp4xxx_module.MCP4xxx(port=1, device=1)
        adapter.assert_called_once_with(port=1, device=1)
        self.assertIs(pot.transport, adapter.return_value)

    def test_explicit_spi_is_used_directly(self):
        """
        spi= bypasses adapter construction and becomes the device transport.
        """
        stub = _StubSpi()
        with mock.patch.object(mcp4xxx_module, "GpiozeroSpiTransport") as adapter:
            pot = MCP4231(r_ab=10e3, spi=stub)
        adapter.assert_not_called()
        self.assertIs(pot.transport, stub)

    def test_explicit_transport_wins(self):
        """
        transport= bypasses adapter construction and wins over device kwargs.
        """
        fake = FakeSpiTransport(default=[0, 0])
        with mock.patch.object(mcp4xxx_module, "GpiozeroSpiTransport") as adapter:
            pot = MCP4231(r_ab=10e3, device=0, transport=fake)
        adapter.assert_not_called()
        self.assertIs(pot.transport, fake)

    def test_mcp4251_constructs_through_adapter(self):
        """
        An 8-bit dual pot constructs through the same adapter path.
        """
        with mock.patch.object(mcp4xxx_module, "GpiozeroSpiTransport") as adapter:
            pot = MCP4251(r_ab=10e3, device=0)
        adapter.assert_called_once_with(device=0)
        self.assertEqual(pot.channels_num, 2)

    def test_mcp4232_constructs_through_adapter(self):
        """
        A rheostat constructs through the same adapter path.
        """
        with mock.patch.object(mcp4xxx_module, "GpiozeroSpiTransport") as adapter:
            pot = MCP4232(r_ab=10e3, device=1)
        adapter.assert_called_once_with(device=1)
        self.assertEqual(pot.channels_num, 2)


if __name__ == "__main__":
    unittest.main()
