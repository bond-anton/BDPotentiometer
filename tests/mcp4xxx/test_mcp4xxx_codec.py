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

    def test_encode_wiper_write_9bit_data_field(self):
        """D8 rides in bit 0 of the high byte."""
        self.assertEqual(_encode_wiper_write(0, 0x100), [0b00000001, 0x00])
        self.assertEqual(_encode_wiper_write(1, 0x100), [0b00010001, 0x00])
        self.assertEqual(_encode_wiper_write(0, 0xFF), [0b00000000, 0xFF])
        self.assertEqual(_encode_wiper_write(1, 0xFF), [0b00010000, 0xFF])

    def test_encode_wiper_write_out_of_range(self):
        """Values outside the 0..256 range raise ValueError."""
        with self.assertRaises(ValueError):
            _encode_wiper_write(0, 257)
        with self.assertRaises(ValueError):
            _encode_wiper_write(0, -1)

    def test_encode_wiper_read_channel_0(self):
        """Test read frame for channel 0."""
        self.assertEqual(_encode_wiper_read(0), [0b00001100, 0])

    def test_encode_wiper_read_channel_1(self):
        """Test read frame for channel 1."""
        self.assertEqual(_encode_wiper_read(1), [0b00011100, 0])

    def test_decode_wiper_read(self):
        """Test read response decoding."""
        self.assertEqual(_decode_wiper_read([0xFE, 43]), 43)

    def test_decode_wiper_read_full_scale(self):
        """D8 set in the high byte yields code 256."""
        self.assertEqual(_decode_wiper_read([0xFF, 0x00]), 256)

    def test_decode_wiper_read_255(self):
        """Code 255 is decoded with D8 clear."""
        self.assertEqual(_decode_wiper_read([0xFE, 0xFF]), 255)

    def test_decode_wiper_read_128_d8_clear(self):
        """A 7-bit full-scale response decodes to 128, not 0 or 256."""
        self.assertEqual(_decode_wiper_read([0xFE, 0x80]), 128)

    def test_decode_wiper_read_invalid(self):
        """Test malformed read response raises ValueError."""
        for data in (None, [], [0]):
            with self.assertRaises(ValueError):
                _decode_wiper_read(data)

    def test_encode_wiper_write_invalid_channel(self):
        """Channels outside 0 and 1 raise ValueError."""
        for channel in (2, -1, 1234):
            with self.assertRaises(ValueError):
                _encode_wiper_write(channel, 0)

    def test_encode_wiper_read_invalid_channel(self):
        """Channels outside 0 and 1 raise ValueError."""
        for channel in (2, -1, 1234):
            with self.assertRaises(ValueError):
                _encode_wiper_read(channel)


if __name__ == "__main__":
    unittest.main()
