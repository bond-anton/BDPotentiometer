"""Tests for MCP4XXX chips driven by an injected SPI transport."""

import unittest

try:
    from src.BDPotentiometer.mcp4xxx import MCP4231
    from src.BDPotentiometer.mcp4xxx import mcp4xxx as mcp4xxx_module
    from src.BDPotentiometer.transport import FakeSpiTransport, TransportClosed
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx import MCP4231
    from BDPotentiometer.mcp4xxx import mcp4xxx as mcp4xxx_module
    from BDPotentiometer.transport import FakeSpiTransport, TransportClosed


class TestMCP4xxxTransport(unittest.TestCase):
    """
    Testing MCP4231 wire bytes and transport sharing through a fake.
    """

    def _build(self):
        fake = FakeSpiTransport(default=[0, 0])
        pot = MCP4231(r_ab=10e3, transport=fake)
        fake.calls.clear()
        return pot, fake

    def test_write_channel_0(self):
        """
        Set value on channel 0 writes the channel 0 frame, then reads it back.
        """
        pot, fake = self._build()
        fake.queue([0, 43], [0, 43])
        value = pot.set_value(0, 43)
        self.assertEqual(
            fake.calls,
            [[0b00000000, 43], [0b00001100, 0]],
        )
        self.assertEqual(value, 43)
        self.assertEqual(pot.channels[0].potentiometer.wiper_position, 43 / 128)

    def test_write_channel_1(self):
        """
        Set value on channel 1 writes the channel 1 frame.
        """
        pot, fake = self._build()
        fake.queue([0, 43], [0, 43])
        value = pot.set_value(1, 43)
        self.assertEqual(
            fake.calls,
            [[0b00010000, 43], [0b00011100, 0]],
        )
        self.assertEqual(value, 43)
        self.assertEqual(pot.channels[1].potentiometer.wiper_position, 43 / 128)

    def test_read_channel_0(self):
        """
        Reading channel 0 submits the channel 0 read frame.
        """
        pot, fake = self._build()
        fake.queue([0, 43])
        self.assertEqual(pot.get_value(0), 43)
        self.assertEqual(fake.calls, [[0b00001100, 0]])

    def test_read_channel_1(self):
        """
        Reading channel 1 submits the channel 1 read frame.
        """
        pot, fake = self._build()
        fake.queue([0, 44])
        self.assertEqual(pot.get_value(1), 44)
        self.assertEqual(fake.calls, [[0b00011100, 0]])

    def test_transport_shared_by_all_channels(self):
        """
        The device and every channel reference the same transport object.
        """
        pot, fake = self._build()
        self.assertIs(pot.transport, fake)
        self.assertIs(pot.channels[0].transport, fake)
        self.assertIs(pot.channels[1].transport, fake)
        self.assertIs(pot.spi, fake)

    def test_close_delegates_to_transport(self):
        """
        close() closes the fake and later transfers raise TransportClosed.
        """
        pot, fake = self._build()
        pot.close()
        self.assertTrue(fake.closed)
        self.assertTrue(pot.closed)
        with self.assertRaises(TransportClosed):
            pot.set_value(0, 1)

    def test_missing_transport_raises_connection_error(self):
        """
        A device without a transport reports the documented ConnectionError.
        """
        # The constructor always builds a default transport, so bypass it to
        # exercise the legacy "no interface" guard without a pin factory.
        device = mcp4xxx_module.MCP4xxx.__new__(mcp4xxx_module.MCP4xxx)
        device._transport = None
        with self.assertRaises(ConnectionError) as context:
            device.get_shdn_pin_status()
        self.assertEqual(str(context.exception), "SPI interface not set")


if __name__ == "__main__":
    unittest.main()
