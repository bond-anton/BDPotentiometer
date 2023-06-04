""" Tests for DigitalPotentiometerDevice class. """

import unittest

try:
    from src.BDPotentiometer.mcp4xxx.mcp4xxx import (
        resistance_list,
        _coerce_max_value,
        _coerce_r_ab,
        _check_write_response,
        _check_read_response,
        # _check_status_response,
        # _check_tcon_response,
        # _parse_tcon_response,
        # _tcon_to_cmd,
    )
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx.mcp4xxx import (
        resistance_list,
        _coerce_max_value,
        _coerce_r_ab,
        _check_write_response,
        _check_read_response,
        # _check_status_response,
        # _check_tcon_response,
        # _parse_tcon_response,
        # _tcon_to_cmd,
    )


class MCP4xxxTestCase(unittest.TestCase):
    """
    MCP4XXX class testing.
    """

    def test_resistance_list(self):
        """Test r_ab resistance list is correct."""
        self.assertEqual(resistance_list, (5e3, 10e3, 50e3, 100e3))

    def test_coerce_max_value(self):
        """test correct coercion of max_value."""
        self.assertEqual(_coerce_max_value(128), 128)
        self.assertEqual(_coerce_max_value(256), 256)
        with self.assertRaises(ValueError):
            _coerce_max_value(512)
        with self.assertRaises(ValueError):
            _coerce_max_value("a")

    def test_coerce_r_ab(self):
        """test correct coercion of r_ab."""
        for r_ab in resistance_list:
            self.assertEqual(_coerce_r_ab(r_ab), r_ab)
        with self.assertRaises(ValueError):
            _coerce_r_ab(20e3)
        with self.assertRaises(ValueError):
            _coerce_r_ab("a")

    def test_write_response(self):
        """Test write response checker."""
        with self.assertRaises(ValueError):
            _check_write_response(None)

    def test_read_response(self):
        """Test read response checker."""
        with self.assertRaises(ValueError):
            _check_read_response(None)


if __name__ == "__main__":
    unittest.main()
