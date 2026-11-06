"""Constructor validation for the MCP4XX chip classes.

Every argument is validated before a transport is built, so a rejected
constructor leaves no SPI device open and performs no transfer.
"""

import unittest
from unittest import mock

try:
    from src.BDPotentiometer.mcp4xxx import MCP4131, MCP4231, MCP4232, MCP4251
    from src.BDPotentiometer.transport import FakeSpiTransport
    from src.BDPotentiometer.transport import gpiozero_spi as gpiozero_spi_module
    from src.BDPotentiometer.transport import spidev_spi as spidev_spi_module
except ModuleNotFoundError:
    from BDPotentiometer.mcp4xxx import MCP4131, MCP4231, MCP4232, MCP4251
    from BDPotentiometer.transport import FakeSpiTransport
    from BDPotentiometer.transport import gpiozero_spi as gpiozero_spi_module
    from BDPotentiometer.transport import spidev_spi as spidev_spi_module


class _NullTransfer:
    """Transport that accepts a request but reports no response."""

    def __init__(self) -> None:
        self.closed = False

    def transfer(self, tx):
        """Return no response, which the wiper must reject."""
        return None

    def close(self) -> None:
        """Mark the transport closed."""
        self.closed = True


class TestConstructorValidationOrder(unittest.TestCase):
    """Invalid arguments are rejected before the transport is built."""

    def test_invalid_r_ab_opens_no_spidev(self):
        """A rejected r_ab never reaches the spidev backend."""
        with (
            mock.patch.object(spidev_spi_module, "SpiDevTransport") as adapter,
            self.assertRaises(ValueError),
        ):
            MCP4131(r_ab=1e3, port=1, device=0)
        adapter.assert_not_called()

    def test_invalid_max_value_opens_no_spidev(self):
        """A rejected max_value never reaches the spidev backend."""
        with (
            mock.patch.object(spidev_spi_module, "SpiDevTransport") as adapter,
            self.assertRaisesRegex(ValueError, "128"),
        ):
            MCP4131(max_value=256, port=1, device=0)
        adapter.assert_not_called()

    def test_invalid_channels_opens_no_spidev(self):
        """A rejected channel count never reaches the spidev backend."""
        with (
            mock.patch.object(spidev_spi_module, "SpiDevTransport") as adapter,
            self.assertRaisesRegex(ValueError, "1..2"),
        ):
            MCP4251(channels=3, port=1, device=0)
        adapter.assert_not_called()

    def test_invalid_arguments_open_no_gpiozero_backend(self):
        """A rejected argument never reaches the gpiozero backend."""
        with (
            mock.patch.object(gpiozero_spi_module, "GpiozeroSpiTransport") as adapter,
            self.assertRaises(ValueError),
        ):
            MCP4231(max_value=256, clock_pin=11)
        adapter.assert_not_called()

    def test_invalid_r_ab_performs_no_transfer(self):
        """A rejected r_ab leaves an injected transport untouched."""
        fake = FakeSpiTransport(default=[0xFE, 0x00])
        with self.assertRaises(ValueError):
            MCP4131(r_ab=1e3, transport=fake)
        self.assertEqual(fake.calls, [])
        self.assertFalse(fake.closed)

    def test_invalid_max_value_performs_no_transfer(self):
        """A rejected max_value leaves an injected transport untouched."""
        fake = FakeSpiTransport(default=[0xFE, 0x00])
        with self.assertRaises(ValueError):
            MCP4251(max_value=128, transport=fake)
        self.assertEqual(fake.calls, [])
        self.assertFalse(fake.closed)

    def test_invalid_channels_performs_no_transfer(self):
        """A rejected channel count leaves an injected transport untouched."""
        fake = FakeSpiTransport(default=[0xFE, 0x00])
        with self.assertRaises(ValueError):
            MCP4131(channels=2, transport=fake)
        self.assertEqual(fake.calls, [])
        self.assertFalse(fake.closed)

    def test_failure_after_transport_is_built_closes_it(self):
        """A read failure during construction releases the transport."""
        transport = _NullTransfer()
        with self.assertRaises(ValueError):
            MCP4251(transport=transport)
        self.assertTrue(transport.closed)


class TestChipRangeEnforcement(unittest.TestCase):
    """Each chip accepts only its own full-scale divisor and channel count."""

    def test_7bit_chip_rejects_8bit_divisor(self):
        """MCP4131(max_value=256) is rejected before the bus is touched."""
        with self.assertRaisesRegex(ValueError, "128"):
            MCP4131(max_value=256, transport=FakeSpiTransport(default=[0xFE, 0x00]))

    def test_8bit_chip_rejects_7bit_divisor(self):
        """MCP4251(max_value=128) is rejected before the bus is touched."""
        with self.assertRaisesRegex(ValueError, "256"):
            MCP4251(max_value=128, transport=FakeSpiTransport(default=[0xFE, 0x00]))

    def test_7bit_chip_rejects_two_channels(self):
        """A single-channel 7-bit chip rejects channels=2."""
        with self.assertRaisesRegex(ValueError, "1..1"):
            MCP4131(channels=2, transport=FakeSpiTransport(default=[0xFE, 0x00]))

    def test_8bit_chip_rejects_three_channels(self):
        """A dual 8-bit chip rejects channels=3."""
        with self.assertRaisesRegex(ValueError, "1..2"):
            MCP4251(channels=3, transport=FakeSpiTransport(default=[0xFE, 0x00]))

    def test_rheostat_family_enforces_its_own_divisor(self):
        """The MCP4XX2 family validates against its own _MAX_VALUE."""
        with self.assertRaisesRegex(ValueError, "128"):
            MCP4232(max_value=256, transport=FakeSpiTransport(default=[0xFE, 0x00]))

    def test_dual_chip_accepts_one_channel(self):
        """Operating only channel 0 of a dual chip stays valid."""
        device = MCP4251(channels=1, transport=FakeSpiTransport(default=[0xFE, 0x00]))
        self.assertEqual(device.channels_num, 1)

    def test_chip_accepts_its_own_divisor(self):
        """The chip's own full-scale divisor is accepted."""
        device = MCP4251(
            max_value=256, transport=FakeSpiTransport(default=[0xFE, 0x00])
        )
        self.assertEqual(device.channels[0].max_value, 256)

    def test_fractional_max_value_is_rejected(self):
        """A fractional divisor is rejected as a value error."""
        with self.assertRaises(ValueError):
            MCP4131(max_value=128.5, transport=FakeSpiTransport(default=[0xFE, 0x00]))

    def test_non_numeric_max_value_is_rejected(self):
        """A non-numeric divisor is rejected as a type error."""
        with self.assertRaises(TypeError):
            MCP4131(max_value="128", transport=FakeSpiTransport(default=[0xFE, 0x00]))


class TestWiperFixedMaxValue(unittest.TestCase):
    """The wiper divisor is fixed by the chip and rejects reassignment."""

    def _build(self, chip=MCP4251):
        fake = FakeSpiTransport(default=[0xFE, 0x00])
        device = chip(r_ab=10e3, transport=fake)
        fake.calls.clear()
        return device, fake

    def test_setter_rejects_foreign_divisor(self):
        """max_value = 1000 is rejected and leaves the wiper unchanged."""
        device, fake = self._build()
        wiper = device.channels[0]
        fake.queue([0, 0])
        wiper.value = 42
        fake.calls.clear()
        with self.assertRaisesRegex(ValueError, "256"):
            wiper.max_value = 1000
        self.assertEqual(wiper.max_value, 256)
        self.assertEqual(wiper.potentiometer.wiper_position, 42 / 256)
        self.assertEqual(fake.calls, [])
        fake.queue([0xFE, 42])
        self.assertEqual(wiper.value, 42)

    def test_setter_rejects_7bit_divisor_on_8bit_wiper(self):
        """An 8-bit wiper rejects the 7-bit divisor 128."""
        device, _ = self._build()
        with self.assertRaisesRegex(ValueError, "256"):
            device.channels[0].max_value = 128
        self.assertEqual(device.channels[0].max_value, 256)

    def test_setter_rejects_8bit_divisor_on_7bit_wiper(self):
        """A 7-bit wiper rejects the 8-bit divisor 256."""
        device, _ = self._build(MCP4231)
        with self.assertRaisesRegex(ValueError, "128"):
            device.channels[0].max_value = 256
        self.assertEqual(device.channels[0].max_value, 128)

    def test_setter_accepts_the_fixed_divisor(self):
        """Assigning the chip's own divisor delegates to the base setter."""
        device, fake = self._build()
        wiper = device.channels[0]
        fake.queue([0, 0])
        wiper.max_value = 256
        self.assertEqual(wiper.max_value, 256)
        self.assertEqual(fake.calls, [[0b00000000, 0x00]])


if __name__ == "__main__":
    unittest.main()
