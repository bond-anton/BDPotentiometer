"""Tests for DigitalWiper channel numbering."""

import unittest

try:
    from src.BDPotentiometer import DigitalWiper, Potentiometer
except ModuleNotFoundError:
    from BDPotentiometer import DigitalWiper, Potentiometer


class _RegisterWiper(DigitalWiper):
    """Wiper whose device state is one register per channel."""

    def __init__(self, potentiometer: Potentiometer, registers: dict, **kwargs):
        self.registers = dict(registers)
        super().__init__(potentiometer=potentiometer, **kwargs)

    def _read_value(self) -> int:
        return self.registers[self.channel]

    def _set_value(self, value: int) -> int:
        code = super()._set_value(value)
        self.registers[self.channel] = code
        return code


class _DisconnectedWiper(DigitalWiper):
    """Wiper whose reads fail once its bus is detached."""

    def __init__(self, potentiometer: Potentiometer, **kwargs):
        self.connected = True
        super().__init__(potentiometer=potentiometer, **kwargs)

    def _read_value(self) -> int:
        if not self.connected:
            raise ConnectionError("SPI interface not set")
        return 0


class TestDigitalWiperChannelNumbering(unittest.TestCase):
    """
    Testing DigitalWiper channel numbering.
    """

    def test_channel_numbering(self):
        """
        Testing channel numbering.
        DigitalWiper Channel is a channel of the actual digital potentiometer device,
        numbered in int numbers starting from 0.
        """
        pot = Potentiometer(r_ab=20e3, r_w=50)
        for max_value in [1, 64, 128, 256]:
            digital_wiper = DigitalWiper(potentiometer=pot, max_value=max_value)
            self.assertEqual(digital_wiper.channel, 0)  # default channel number is 0
            # Correct channel numbers
            for channel_number in [3, 4.0, 1234, 0, 17]:
                digital_wiper.channel = channel_number
                self.assertEqual(digital_wiper.channel, channel_number)
                self.assertIsInstance(digital_wiper.channel, int)
            # Wrong channel number value
            for channel_number_ in [-1, 1.12]:
                with self.assertRaises(ValueError):
                    digital_wiper.channel = channel_number_
            # Wrong channel number type
            for channel_number_ in ["1", None]:
                with self.assertRaises(TypeError):
                    digital_wiper.channel = channel_number_
            self.assertEqual(
                digital_wiper.channel, channel_number
            )  # Check that channel number did not_change

    def test_channel_change_reloads_cached_value(self):
        """The cached code after a channel change belongs to the new channel."""
        pot = Potentiometer(r_ab=20e3, r_w=50)
        registers = {0: 10, 1: 50}
        wiper = _RegisterWiper(potentiometer=pot, registers=registers, max_value=128)
        self.assertEqual(wiper.value, 10)
        wiper.channel = 1
        self.assertEqual(wiper.channel, 1)
        self.assertEqual(wiper.value, 50)

    def test_max_value_change_applies_to_current_channel(self):
        """`max_value` re-applies the new channel's code, not the old one."""
        pot = Potentiometer(r_ab=20e3, r_w=50)
        registers = {0: 10, 1: 50}
        wiper = _RegisterWiper(potentiometer=pot, registers=registers, max_value=128)
        wiper.channel = 1
        wiper.max_value = 64
        self.assertEqual(registers[0], 10)
        self.assertEqual(registers[1], 50)
        self.assertEqual(wiper.value, 50)

    def test_channel_change_without_bus_raises_after_assigning(self):
        """A detached bus-backed wiper raises ConnectionError from `read()`."""
        pot = Potentiometer(r_ab=20e3, r_w=50)
        wiper = _DisconnectedWiper(potentiometer=pot, max_value=128)
        wiper.connected = False
        with self.assertRaises(ConnectionError):
            wiper.channel = 1
        self.assertEqual(wiper.channel, 1)


if __name__ == "__main__":
    unittest.main()
