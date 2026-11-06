"""Full-scale wiper writes for 8-bit MCP4XXX parts."""

import unittest

try:
    from src.BDPotentiometer.mcp4xxx import MCP4231, MCP4251
    from src.BDPotentiometer.transport import FakeSpiTransport
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx import MCP4231, MCP4251
    from BDPotentiometer.transport import FakeSpiTransport


class TestMCP4xxxFullScale(unittest.TestCase):
    """8-bit parts clamp to 255 and transmit a one-byte code."""

    def _build(self, chip, **kwargs):
        fake = FakeSpiTransport(default=[0, 0])
        device = chip(r_ab=10e3, transport=fake, **kwargs)
        fake.calls.clear()
        return device, fake

    def test_mcp4251_value_256_clamps_to_255(self):
        """A value above the 8-bit code range is clamped before encoding."""
        device, fake = self._build(MCP4251)
        self.assertEqual(device.channels[0].max_value, 256)
        self.assertEqual(device.channels[0].max_code, 255)
        fake.queue([0, 255])
        device.channels[0].value = 256
        self.assertEqual(fake.calls, [[0x00, 0xFF]])
        self.assertEqual(device.channels[0].potentiometer.wiper_position, 255 / 256)
        fake.queue([0, 255])
        self.assertEqual(device.channels[0].value, 255)

    def test_mcp4251_value_255(self):
        """The highest 8-bit code is transmitted unchanged."""
        device, fake = self._build(MCP4251)
        fake.queue([0, 255], [0, 255])
        device.channels[0].value = 255
        self.assertEqual(fake.calls, [[0x00, 0xFF]])
        self.assertEqual(device.channels[0].value, 255)

    def test_mcp4231_value_128(self):
        """7-bit parts keep their 129th code."""
        device, fake = self._build(MCP4231)
        self.assertEqual(device.channels[0].max_code, 128)
        fake.queue([0, 128])
        device.channels[0].value = 128
        self.assertEqual(fake.calls, [[0x00, 0x80]])
        self.assertEqual(device.channels[0].potentiometer.wiper_position, 128 / 128)
        fake.queue([0, 128])
        self.assertEqual(device.channels[0].value, 128)

    def test_mcp4251_invert_value_0(self):
        """Inverted 8-bit wiper maps 0 to code 255 and back."""
        device, fake = self._build(MCP4251, invert=True)
        fake.queue([0, 0x00], [0, 0xFF])
        device.channels[0].value = 0
        self.assertEqual(fake.calls, [[0x00, 0xFF]])
        self.assertEqual(device.channels[0].value, 0)


if __name__ == "__main__":
    unittest.main()
