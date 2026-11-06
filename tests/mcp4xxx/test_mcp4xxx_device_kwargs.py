"""Tests for keyword forwarding through the MCP4XX chip constructors."""

import unittest

try:
    from src.BDPotentiometer.mcp4xxx import MCP4251, MCP4252
    from src.BDPotentiometer.transport import FakeSpiTransport
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx import MCP4251, MCP4252
    from BDPotentiometer.transport import FakeSpiTransport


class TestMCP4xxDeviceKwargs(unittest.TestCase):
    """
    Testing that constructor keywords reach every collaborator.
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

    def test_mcp4251_forwards_label(self) -> None:
        """
        MCP4251(label=...) keeps the label on the device and its channels.
        """
        fake = FakeSpiTransport(default=[0, 0])
        pot = MCP4251(r_ab=10e3, transport=fake, label="Deck pot")
        self.assertEqual(pot.logger.name, "Deck pot")
        self.assertEqual(pot.channels[0].logger.name, "Deck pot")


if __name__ == "__main__":
    unittest.main()
