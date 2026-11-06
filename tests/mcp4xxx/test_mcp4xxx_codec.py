"""Tests for MCP4XXX pure codec helpers."""

import unittest

try:
    from src.BDPotentiometer.mcp4xxx.mcp4xxx import (
        _decode_wiper_read,
        _encode_wiper_read,
        _encode_wiper_write,
    )
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx.mcp4xxx import (
        _decode_wiper_read,
        _encode_wiper_read,
        _encode_wiper_write,
    )


class MCP4xxxCodecTestCase(unittest.TestCase):
    """
    MCP4XXX wiper command encoding and response decoding.
    """

    def test_encode_wiper_write_channel_0(self):
        """Test write frame for channel 0."""
        self.assertEqual(_encode_wiper_write(0, 43), [0b00000000, 43])

    def test_encode_wiper_write_channel_1(self):
        """Test write frame for channel 1."""
        self.assertEqual(_encode_wiper_write(1, 43), [0b00010000, 43])

    def test_encode_wiper_read_channel_0(self):
        """Test read frame for channel 0."""
        self.assertEqual(_encode_wiper_read(0), [0b00001100, 0])

    def test_encode_wiper_read_channel_1(self):
        """Test read frame for channel 1."""
        self.assertEqual(_encode_wiper_read(1), [0b00011100, 0])

    def test_decode_wiper_read(self):
        """Test read response decoding."""
        self.assertEqual(_decode_wiper_read([0, 43]), 43)

    def test_decode_wiper_read_invalid(self):
        """Test malformed read response raises ValueError."""
        with self.assertRaises(ValueError):
            _decode_wiper_read(None)


if __name__ == "__main__":
    unittest.main()
