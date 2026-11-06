"""Full-scale wiper writes for 8-bit and 7-bit MCP4XXX parts."""

import unittest

from scietex.hal.spi import FakeSpiTransport

try:
    from src.BDPotentiometer.mcp4xxx import MCP4231, MCP4251
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx import MCP4231, MCP4251


class TestMCP4xxxFullScale(unittest.TestCase):
    """Both families reach full scale at their step count."""

    def _build(self, chip, **kwargs):
        fake = FakeSpiTransport(default=[0xFE, 0x00])
        device = chip(r_ab=10e3, transport=fake, **kwargs)
        fake.calls.clear()
        return device, fake

    def test_mcp4251_value_256_is_full_scale(self):
        """Code 256 sets D8 and reaches terminal A."""
        device, fake = self._build(MCP4251)
        self.assertEqual(device.channels[0].max_value, 256)
        self.assertEqual(device.channels[0].max_code, 256)
        fake.queue([0, 0])
        device.channels[0].value = 256
        self.assertEqual(fake.calls, [[0x01, 0x00]])
        self.assertEqual(device.channels[0].potentiometer.wiper_position, 1.0)
        fake.queue([0xFF, 0x00])
        self.assertEqual(device.channels[0].value, 256)

    def test_mcp4251_value_257_clamps_to_256(self):
        """A value above the 8-bit code range is clamped before encoding."""
        device, fake = self._build(MCP4251)
        fake.queue([0, 0])
        device.channels[0].value = 257
        self.assertEqual(fake.calls, [[0x01, 0x00]])
        self.assertEqual(device.channels[0].potentiometer.wiper_position, 1.0)
        fake.queue([0xFF, 0x00])
        self.assertEqual(device.channels[0].value, 256)

    def test_mcp4251_value_255(self):
        """Code 255 is transmitted with D8 clear."""
        device, fake = self._build(MCP4251)
        fake.queue([0, 0], [0xFE, 0xFF])
        device.channels[0].value = 255
        self.assertEqual(fake.calls, [[0x00, 0xFF]])
        self.assertEqual(device.channels[0].value, 255)

    def test_mcp4231_value_128_is_full_scale(self):
        """The 7-bit full-scale code is 128, transmitted as 0x80."""
        device, fake = self._build(MCP4231)
        self.assertEqual(device.channels[0].max_code, 128)
        fake.queue([0, 0])
        device.channels[0].value = 128
        self.assertEqual(fake.calls, [[0x00, 0x80]])
        self.assertEqual(device.channels[0].potentiometer.wiper_position, 1.0)
        fake.queue([0xFE, 0x80])
        self.assertEqual(device.channels[0].value, 128)

    def test_mcp4231_value_129_clamps_to_128(self):
        """A value above the 7-bit code range is clamped before encoding."""
        device, fake = self._build(MCP4231)
        fake.queue([0, 0])
        device.channels[0].value = 129
        self.assertEqual(fake.calls, [[0x00, 0x80]])
        self.assertEqual(device.channels[0].potentiometer.wiper_position, 1.0)
        fake.queue([0xFE, 0x80])
        self.assertEqual(device.channels[0].value, 128)

    def test_mcp4251_invert_value_0(self):
        """Inverted 8-bit wiper maps 0 to code 256 and back."""
        device, fake = self._build(MCP4251, invert=True)
        fake.queue([0, 0], [0xFF, 0x00])
        device.channels[0].value = 0
        self.assertEqual(fake.calls, [[0x01, 0x00]])
        self.assertEqual(device.channels[0].value, 0)


if __name__ == "__main__":
    unittest.main()
