"""Tests for keyword forwarding through the MCP4XX chip constructors."""

import logging
import unittest
from unittest import mock

try:
    from src.BDPotentiometer.mcp4xxx import MCP4251, MCP4252
    from src.BDPotentiometer.transport import FakeSpiTransport
    from src.BDPotentiometer.transport import spidev_spi as spidev_spi_module
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx import MCP4251, MCP4252
    from BDPotentiometer.transport import FakeSpiTransport
    from BDPotentiometer.transport import spidev_spi as spidev_spi_module


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
        fake.queue([0, 0], [0, 246])
        value = pot.set_value(0, 10)
        self.assertEqual(fake.calls, [[0b00000000, 246], [0b00001100, 0]])
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
        with self.assertRaisesRegex(TypeError, "invertt"):
            MCP4251(r_ab=10e3, transport=fake, invertt=True)

    def test_transport_with_device_keyword_raises_type_error(self) -> None:
        """
        transport= plus a backend keyword is rejected instead of dropped.
        """
        fake = FakeSpiTransport(default=[0, 0])
        with self.assertRaisesRegex(TypeError, "device.*transport"):
            MCP4251(r_ab=10e3, transport=fake, device=0)

    def test_spi_with_pin_keywords_raises_type_error(self) -> None:
        """
        spi= plus several backend keywords names every offender.
        """
        fake = FakeSpiTransport(default=[0, 0])
        with self.assertRaisesRegex(TypeError, "port, clock_pin"):
            MCP4251(r_ab=10e3, spi=fake, port=0, clock_pin=11)

    def test_backend_keywords_without_transport_still_build(self) -> None:
        """
        Backend keywords without transport= keep selecting the default backend.
        """
        with mock.patch.object(spidev_spi_module, "SpiDevTransport") as adapter:
            adapter.return_value.transfer.return_value = [0, 0]
            pot = MCP4251(r_ab=10e3, device=0)
        adapter.assert_called_once_with(bus=0, device=0)
        self.assertEqual(pot.channels_num, 2)

    def test_closed_calls_callable_transport_attribute(self) -> None:
        """
        A transport exposing closed as a method is interrogated, not trusted.
        """

        class CallableClosedTransport:
            """Transport whose closed attribute is a method."""

            def __init__(self) -> None:
                self.is_closed = False

            def transfer(self, tx):
                """Return a zero response."""
                return [0, 0]

            def close(self) -> None:
                """Mark the backend closed."""
                self.is_closed = True

            def closed(self) -> bool:
                """Report the backend state."""
                return self.is_closed

        transport = CallableClosedTransport()
        pot = MCP4251(r_ab=10e3, transport=transport)
        self.assertFalse(pot.closed)
        transport.is_closed = True
        self.assertTrue(pot.closed)
        transport.is_closed = False
        pot.close()
        self.assertTrue(pot.closed)
        self.assertTrue(transport.is_closed)


if __name__ == "__main__":
    unittest.main()
