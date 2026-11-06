"""Tests for keyword forwarding through the MCP4XX chip constructors."""

import logging
import unittest

try:
    from src.BDPotentiometer.mcp4xxx import MCP4251, MCP4252
    from src.BDPotentiometer.transport import FakeSpiTransport
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx import MCP4251, MCP4252
    from BDPotentiometer.transport import FakeSpiTransport


class TestMCP4xxDeviceKwargs(unittest.TestCase):
    """
    Testing how constructor keywords are routed to collaborators.
    """

    def test_mcp4252_forwards_invert(self) -> None:
        """
        MCP4252(invert=True) reports inversion and writes the inverted code.
        """
        fake = FakeSpiTransport(default=[0, 0])
        pot = MCP4252(r_ab=10e3, transport=fake, invert=True)
        self.assertIs(pot.channels[0].invert, True)
        self.assertEqual(pot.invert, (True, True))
        fake.calls.clear()
        fake.queue([0, 0], [0, 245])
        value = pot.set_value(0, 10)
        self.assertEqual(fake.calls, [[0b00000000, 245], [0b00001100, 0]])
        self.assertEqual(value, 10)

    def test_mcp4251_routes_invert_label_and_log_level(self) -> None:
        """
        invert reaches the wiper; label and log_level reach the device only.
        """
        fake = FakeSpiTransport(default=[0, 0])
        pot = MCP4251(
            r_ab=10e3,
            transport=fake,
            invert=True,
            label="pot",
            log_level="DEBUG",
        )
        self.assertIs(pot.channels[0].invert, True)
        self.assertEqual(pot.logger.name, "pot")
        self.assertEqual(pot.logger.level, logging.DEBUG)
        self.assertEqual(pot.channels[0].logger.name, "Digital Wiper")
        self.assertEqual(pot.channels[0].potentiometer.logger.name, "Potentiometer")
        logger_names = (
            pot.logger.name,
            pot.channels[0].logger.name,
            pot.channels[0].potentiometer.logger.name,
        )
        self.assertEqual(logger_names.count("pot"), 1)

    def test_unknown_keyword_raises_type_error(self) -> None:
        """
        A misspelled keyword is rejected instead of being silently swallowed.
        """
        fake = FakeSpiTransport(default=[0, 0])
        with self.assertRaises(TypeError):
            MCP4251(transport=fake, invertt=True)


if __name__ == "__main__":
    unittest.main()
