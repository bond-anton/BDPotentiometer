"""Tests for MCP4XXX wiper value inversion over the SPI wire."""

import unittest

from scietex.hal.spi import FakeSpiTransport

try:
    from src.BDPotentiometer.mcp4xxx import MCP4231, MCP4251
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx import MCP4231, MCP4251

# Command bytes from the MCP4XXX protocol.
_WRITE_CH0 = 0b00000000
_READ_CH0 = 0b00001100


class TestMCP4xxxInvert(unittest.TestCase):
    """An inverted wiper transmits the complement of the requested code."""

    def _build(self, chip, invert: bool):
        """Build a chip with an inverted or non-inverted wiper."""
        fake = FakeSpiTransport(default=[0xFE, 0x00])
        device = chip(r_ab=10e3, transport=fake, invert=invert)
        fake.calls.clear()
        return device, fake

    def test_7bit_invert_value_0(self):
        """7-bit inverted value 0 is transmitted as full-scale code 128."""
        device, fake = self._build(MCP4231, invert=True)
        fake.queue([0, 0], [0xFE, 0x80])
        device.channels[0].value = 0
        self.assertEqual(fake.calls[0], [_WRITE_CH0, 0x80])
        self.assertEqual(device.channels[0].potentiometer.wiper_position, 1.0)
        self.assertEqual(device.channels[0].value, 0)
        self.assertEqual(fake.calls, [[_WRITE_CH0, 0x80], [_READ_CH0, 0]])

    def test_7bit_invert_value_128(self):
        """7-bit inverted full-scale value 128 is transmitted as code 0."""
        device, fake = self._build(MCP4231, invert=True)
        fake.queue([0, 0], [0xFE, 0x00])
        device.channels[0].value = 128
        self.assertEqual(fake.calls[0], [_WRITE_CH0, 0x00])
        self.assertEqual(device.channels[0].potentiometer.wiper_position, 0.0)
        self.assertEqual(device.channels[0].value, 128)
        self.assertEqual(fake.calls, [[_WRITE_CH0, 0x00], [_READ_CH0, 0]])

    def test_8bit_invert_value_0(self):
        """8-bit inverted value 0 is transmitted as full-scale code 256."""
        device, fake = self._build(MCP4251, invert=True)
        fake.queue([0, 0], [0xFF, 0x00])
        device.channels[0].value = 0
        self.assertEqual(fake.calls[0], [_WRITE_CH0 | 0x01, 0x00])
        self.assertEqual(device.channels[0].potentiometer.wiper_position, 1.0)
        self.assertEqual(device.channels[0].value, 0)
        self.assertEqual(fake.calls, [[_WRITE_CH0 | 0x01, 0x00], [_READ_CH0, 0]])

    def test_8bit_invert_value_255(self):
        """8-bit inverted code 255 is transmitted as code 1."""
        device, fake = self._build(MCP4251, invert=True)
        fake.queue([0, 0], [0xFE, 0x01])
        device.channels[0].value = 255
        self.assertEqual(fake.calls[0], [_WRITE_CH0, 0x01])
        self.assertEqual(device.channels[0].potentiometer.wiper_position, 1 / 256)
        self.assertEqual(device.channels[0].value, 255)
        self.assertEqual(fake.calls, [[_WRITE_CH0, 0x01], [_READ_CH0, 0]])

    def test_read_back_inverts_code(self):
        """The getter inverts a 7-bit code read from the device."""
        device, fake = self._build(MCP4231, invert=True)
        fake.queue([0xFE, 0x64])
        self.assertEqual(device.channels[0].value, 28)
        self.assertEqual(fake.calls, [[_READ_CH0, 0]])

    def test_read_back_inverts_8bit_code(self):
        """The getter inverts an 8-bit code against the 256-step scale."""
        device, fake = self._build(MCP4251, invert=True)
        fake.queue([0xFE, 0x64])
        self.assertEqual(device.channels[0].value, 156)
        self.assertEqual(fake.calls, [[_READ_CH0, 0]])

    def test_non_inverted_set_control(self):
        """Without inversion the requested code is transmitted unchanged."""
        device, fake = self._build(MCP4231, invert=False)
        fake.queue([0, 0], [0xFE, 0x2A])
        device.channels[0].value = 42
        self.assertEqual(fake.calls[0], [_WRITE_CH0, 42])
        self.assertEqual(device.channels[0].value, 42)

    def test_non_inverted_read_back_control(self):
        """Without inversion the read code is returned unchanged."""
        device, fake = self._build(MCP4231, invert=False)
        fake.queue([0xFE, 0x64])
        self.assertEqual(device.channels[0].value, 100)
        self.assertEqual(fake.calls, [[_READ_CH0, 0]])


if __name__ == "__main__":
    unittest.main()
