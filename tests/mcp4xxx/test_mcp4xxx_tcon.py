"""Tests for MCP4XXX TCON and SHDN control over the SPI wire."""

import unittest

try:
    from src.BDPotentiometer.mcp4xxx import MCP4231
    from src.BDPotentiometer.mcp4xxx.mcp4xxx import (
        _check_status_response,
        _check_tcon_response,
        _tcon_to_cmd,
    )
    from src.BDPotentiometer.transport import FakeSpiTransport
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx import MCP4231
    from BDPotentiometer.mcp4xxx.mcp4xxx import (
        _check_status_response,
        _check_tcon_response,
        _tcon_to_cmd,
    )
    from BDPotentiometer.transport import FakeSpiTransport

# Command bytes from the MCP4XXX protocol. The TCON write frame sets D8 to 1,
# which Register 4-2 reserves and forces to 1.
_WRITE_TCON = 0b01000001
_READ_TCON = 0b01001100
_READ_STATUS = 0b01011100
_TCON_ALL_ON = 0xFF


class TestMCP4xxxTcon(unittest.TestCase):
    """TCON and SHDN requests are asserted at the wire frame level."""

    def _build(self):
        """Build a two-channel chip over a fake transport."""
        fake = FakeSpiTransport(default=[0xFF, _TCON_ALL_ON])
        device = MCP4231(r_ab=10e3, transport=fake)
        fake.calls.clear()
        return device, fake

    def test_read_tcon_frame_and_parse(self):
        """read_tcon sends the TCON read frame and decodes both nibbles."""
        device, fake = self._build()
        fake.queue([0xFF, 0b10010110])
        ch0, ch1 = device.read_tcon()
        self.assertEqual(fake.calls, [[_READ_TCON, 0]])
        self.assertEqual(ch0, {"shdn": True, "A": True, "W": True, "B": False})
        self.assertEqual(ch1, {"shdn": False, "A": False, "W": False, "B": True})

    def test_write_tcon_default_all_terminals_on(self):
        """The default TCON connects every terminal on both channels."""
        device, fake = self._build()
        fake.queue([0, 0], [0xFF, _TCON_ALL_ON])
        self.assertTrue(device.write_tcon())
        self.assertEqual(fake.calls, [[_WRITE_TCON, _TCON_ALL_ON], [_READ_TCON, 0]])

    def test_write_tcon_clears_individual_terminals(self):
        """Per-channel bits are packed into the low and high nibbles."""
        device, fake = self._build()
        ch0 = {"shdn": True, "A": False, "W": False, "B": True}
        ch1 = {"shdn": False, "A": False, "W": True, "B": False}
        fake.queue([0, 0], [0xFF, 0xA1])
        self.assertTrue(device.write_tcon(ch0=ch0, ch1=ch1))
        self.assertEqual(fake.calls, [[_WRITE_TCON, 0xA1], [_READ_TCON, 0]])

    def test_write_tcon_reports_read_back_mismatch(self):
        """A read-back that differs from the request reports failure."""
        device, fake = self._build()
        fake.queue([0, 0], [0xFF, 0x00])
        self.assertFalse(device.write_tcon())
        self.assertEqual(fake.calls, [[_WRITE_TCON, _TCON_ALL_ON], [_READ_TCON, 0]])

    def test_shdn_asserts_channel_0_only(self):
        """Selected channels gate the SHDN bit while keeping terminals on."""
        device, fake = self._build()
        fake.queue([0xFF, _TCON_ALL_ON], [0, 0], [0xFF, 0xF7])
        self.assertTrue(device.shdn(ch0=True, ch1=False))
        self.assertEqual(
            fake.calls,
            [[_READ_TCON, 0], [_WRITE_TCON, 0xF7], [_READ_TCON, 0]],
        )

    def test_shdn_asserts_channel_1_only(self):
        """The channel 1 shutdown bit lands in the high nibble."""
        device, fake = self._build()
        fake.queue([0xFF, _TCON_ALL_ON], [0, 0], [0xFF, 0x7F])
        self.assertTrue(device.shdn(ch0=False, ch1=True))
        self.assertEqual(
            fake.calls,
            [[_READ_TCON, 0], [_WRITE_TCON, 0x7F], [_READ_TCON, 0]],
        )

    def test_shdn_preserves_existing_terminal_connections(self):
        """Only the shutdown bit changes; read terminal states are kept."""
        device, fake = self._build()
        # Channel 0 has B connected only (0x9); channel 1 has every terminal on.
        fake.queue([0xFF, 0xF9], [0, 0], [0xFF, 0xF1])
        self.assertTrue(device.shdn(ch0=True))
        self.assertEqual(fake.calls[1], [_WRITE_TCON, 0xF1])

    def test_get_shdn_pin_status(self):
        """The SHDN status bit maps to True and False."""
        device, fake = self._build()
        fake.queue([0xFF, 0b11100010])
        self.assertTrue(device.get_shdn_pin_status())
        fake.queue([0xFF, 0b11100000])
        self.assertFalse(device.get_shdn_pin_status())
        self.assertEqual(fake.calls, [[_READ_STATUS, 0], [_READ_STATUS, 0]])

    def test_read_tcon_rejects_malformed_response(self):
        """A response without the reserved D8 bit raises ValueError."""
        device, fake = self._build()
        fake.queue([0xFE, 0xFF])
        with self.assertRaises(ValueError):
            device.read_tcon()

    def test_tcon_read_rejects_unframed_response(self):
        """Bits 15:9 must all be set, not only D8."""
        for data in ([0x01, 0x00], [0x7F, 0x00]):
            with self.assertRaises(ValueError):
                _check_tcon_response(data)

    def test_status_read_rejects_unframed_response(self):
        """Bits 15:9 must all be set, not only the forced D8:D5."""
        for data in ([0x01, 0xE0], [0x7F, 0xE0]):
            with self.assertRaises(ValueError):
                _check_status_response(data)

    def test_tcon_codec_rejects_too_short_response(self):
        """A truncated response raises ValueError before indexing."""
        for data in ([1], [], None):
            with self.assertRaises(ValueError):
                _check_tcon_response(data)

    def test_status_codec_rejects_too_short_response(self):
        """A truncated status response raises ValueError before indexing."""
        for data in ([1], [], None):
            with self.assertRaises(ValueError):
                _check_status_response(data)

    def test_tcon_to_cmd_maps_bits(self):
        """The bit mapping is unchanged: shutdown clears the hardware bit."""
        self.assertEqual(
            _tcon_to_cmd({"shdn": False, "A": True, "W": True, "B": True}), 0xF
        )
        self.assertEqual(
            _tcon_to_cmd({"shdn": True, "A": True, "W": True, "B": True}), 0x7
        )
        self.assertEqual(
            _tcon_to_cmd({"shdn": False, "A": False, "W": False, "B": False}), 0x8
        )

    def test_tcon_to_cmd_rejects_non_dict(self):
        """Anything but a dict is a TypeError."""
        for tcon in (None, [], "shdn"):
            with self.assertRaises(TypeError):
                _tcon_to_cmd(tcon)

    def test_tcon_to_cmd_rejects_wrong_keys(self):
        """The key set must be exactly shdn, A, W, and B."""
        with self.assertRaises(ValueError):
            _tcon_to_cmd({"shdn": False, "A": True, "W": True})
        with self.assertRaises(ValueError):
            _tcon_to_cmd({"shdn": False, "A": True, "W": True, "B": True, "X": True})

    def test_tcon_to_cmd_rejects_non_bool_values(self):
        """Truthy stand-ins such as "0" and 1 are rejected, not coerced."""
        for value in ("0", "1", 0, 1, None):
            with self.assertRaises(TypeError):
                _tcon_to_cmd({"shdn": value, "A": True, "W": True, "B": True})
        with self.assertRaises(TypeError):
            _tcon_to_cmd({"shdn": False, "A": True, "W": 1, "B": True})


if __name__ == "__main__":
    unittest.main()
