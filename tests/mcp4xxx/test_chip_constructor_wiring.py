"""Tests for chip constructor transport wiring."""

import unittest
from unittest import mock

try:
    from src.BDPotentiometer.mcp4xxx import MCP4231, MCP4232, MCP4251
    from src.BDPotentiometer.mcp4xxx import mcp4xxx as mcp4xxx_module
    from src.BDPotentiometer.transport import FakeSpiTransport
    from src.BDPotentiometer.transport import gpiozero_spi as gpiozero_spi_module
    from src.BDPotentiometer.transport import spidev_spi as spidev_spi_module
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx import MCP4231, MCP4232, MCP4251
    from BDPotentiometer.mcp4xxx import mcp4xxx as mcp4xxx_module
    from BDPotentiometer.transport import FakeSpiTransport
    from BDPotentiometer.transport import gpiozero_spi as gpiozero_spi_module
    from BDPotentiometer.transport import spidev_spi as spidev_spi_module


class _StubSpi:
    """Minimal transport used to exercise the explicit spi= path."""

    def __init__(self):
        self.calls = []

    def transfer(self, tx):
        """Record the frame and report wiper code 0."""
        self.calls.append(list(tx))
        return [0xFE, 0]

    def close(self):
        """No-op close."""


def _patch_backends(spidev_adapter, gpiozero_adapter):
    """Patch the backend classes at the sites `build_default_transport` imports."""
    return (
        mock.patch.object(spidev_spi_module, "SpiDevTransport", spidev_adapter),
        mock.patch.object(
            gpiozero_spi_module, "GpiozeroSpiTransport", gpiozero_adapter
        ),
    )


class TestMCP4xxxConstructorWiring(unittest.TestCase):
    """
    Testing how chip constructors build or accept a transport.
    """

    def test_no_spi_kwargs_builds_default_transport(self):
        """
        A bare constructor builds the default spidev transport.
        """
        with mock.patch.object(spidev_spi_module, "SpiDevTransport") as adapter:
            adapter.return_value.transfer.return_value = [0xFE, 0]
            pot = MCP4231(r_ab=10e3)
        adapter.assert_called_once_with(bus=0, device=0)
        self.assertIs(pot.transport, adapter.return_value)

    def test_device_kwarg_builds_spidev_transport(self):
        """
        device= alone stays on the default spidev backend.
        """
        with mock.patch.object(spidev_spi_module, "SpiDevTransport") as adapter:
            adapter.return_value.transfer.return_value = [0xFE, 0]
            pot = MCP4231(r_ab=10e3, device=1)
        adapter.assert_called_once_with(bus=0, device=1)
        self.assertIs(pot.transport, adapter.return_value)

    def test_pin_kwargs_select_gpiozero_transport(self):
        """
        A pin keyword opts into the gpiozero backend with all keywords forwarded.
        """
        with mock.patch.object(gpiozero_spi_module, "GpiozeroSpiTransport") as adapter:
            adapter.return_value.transfer.return_value = [0xFE, 0]
            MCP4231(r_ab=10e3, port=0, device=1, clock_pin=11)
        adapter.assert_called_once_with(port=0, device=1, clock_pin=11)

    def test_channel_kwarg_is_rejected(self):
        """
        channel= is not an accepted constructor keyword and is rejected.
        """
        spidev_adapter = mock.MagicMock()
        gpiozero_adapter = mock.MagicMock()
        spidev_patch, gpiozero_patch = _patch_backends(spidev_adapter, gpiozero_adapter)
        with spidev_patch, gpiozero_patch:
            self.assertRaises(TypeError, MCP4231, r_ab=10e3, channel=1, device=0)
        spidev_adapter.assert_not_called()
        gpiozero_adapter.assert_not_called()

    def test_mcp4xxx_forwards_port_and_device(self):
        """
        The base MCP4xxx constructor maps port/device onto the spidev bus/device.
        """
        with mock.patch.object(spidev_spi_module, "SpiDevTransport") as adapter:
            pot = mcp4xxx_module.MCP4xxx(port=1, device=1)
        adapter.assert_called_once_with(bus=1, device=1)
        self.assertIs(pot.transport, adapter.return_value)

    def test_spi_args_attribute_is_backend_agnostic(self):
        """
        _SPI_ARGS stays public without importing gpiozero.
        """
        self.assertEqual(
            mcp4xxx_module.MCP4xxx._SPI_ARGS,
            ("port", "device", "clock_pin", "mosi_pin", "miso_pin", "select_pin"),
        )

    def test_explicit_spi_is_used_directly(self):
        """
        spi= bypasses backend construction and becomes the device transport.
        """
        stub = _StubSpi()
        spidev_adapter = mock.MagicMock()
        gpiozero_adapter = mock.MagicMock()
        spidev_patch, gpiozero_patch = _patch_backends(spidev_adapter, gpiozero_adapter)
        with spidev_patch, gpiozero_patch:
            pot = MCP4231(r_ab=10e3, spi=stub)
        spidev_adapter.assert_not_called()
        gpiozero_adapter.assert_not_called()
        self.assertIs(pot.transport, stub)

    def test_explicit_transport_rejects_device_keyword(self):
        """
        transport= cannot be combined with backend keywords and names the offender.
        """
        fake = FakeSpiTransport(default=[0xFE, 0])
        with self.assertRaises(TypeError) as raised:
            MCP4231(r_ab=10e3, device=0, transport=fake)
        self.assertIn("device", str(raised.exception))

    def test_mcp4251_constructs_through_adapter(self):
        """
        An 8-bit dual pot constructs through the same default backend path.
        """
        with mock.patch.object(spidev_spi_module, "SpiDevTransport") as adapter:
            adapter.return_value.transfer.return_value = [0xFE, 0]
            pot = MCP4251(r_ab=10e3, device=0)
        adapter.assert_called_once_with(bus=0, device=0)
        self.assertEqual(pot.channels_num, 2)

    def test_mcp4232_constructs_through_adapter(self):
        """
        A rheostat constructs through the same default backend path.
        """
        with mock.patch.object(spidev_spi_module, "SpiDevTransport") as adapter:
            adapter.return_value.transfer.return_value = [0xFE, 0]
            pot = MCP4232(r_ab=10e3, device=1)
        adapter.assert_called_once_with(bus=0, device=1)
        self.assertEqual(pot.channels_num, 2)


if __name__ == "__main__":
    unittest.main()
