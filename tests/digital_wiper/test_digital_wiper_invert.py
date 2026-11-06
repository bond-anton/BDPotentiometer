"""Tests for DigitalWiper value inversion."""

import unittest

try:
    from src.BDPotentiometer import DigitalWiper, Potentiometer
except ModuleNotFoundError:
    from BDPotentiometer import DigitalWiper, Potentiometer


class TestDigitalWiperInvert(unittest.TestCase):
    """Inverted wipers expose the complement of the wiper position code."""

    def _make(self, invert: bool, max_value: int = 128):
        """Build a wiper over a fresh potentiometer."""
        potentiometer = Potentiometer(r_ab=10e3, r_w=75)
        wiper = DigitalWiper(
            potentiometer=potentiometer, max_value=max_value, invert=invert
        )
        return wiper, potentiometer

    def test_invert_value_ends(self):
        """Inverted values 0 and max drive the wiper to opposite ends."""
        wiper, potentiometer = self._make(invert=True)
        wiper.value = 0
        self.assertEqual(potentiometer.wiper_position, 1.0)
        self.assertEqual(wiper.value, 0)
        wiper.value = 128
        self.assertEqual(potentiometer.wiper_position, 0.0)
        self.assertEqual(wiper.value, 128)

    def test_invert_value_middle(self):
        """Inversion reverses the direction without shifting the midpoint."""
        wiper, potentiometer = self._make(invert=True)
        wiper.value = 32
        self.assertEqual(potentiometer.wiper_position, 0.75)
        self.assertEqual(wiper.value, 32)

    def test_read_back_inverts_position(self):
        """The getter inverts a position written outside the wiper."""
        wiper, potentiometer = self._make(invert=True)
        potentiometer.wiper_position = 0.25
        self.assertEqual(wiper.value, 96)
        potentiometer.wiper_position = 0.5
        self.assertEqual(wiper.value, 64)

    def test_non_inverted_control(self):
        """A non-inverted wiper maps values straight to the position."""
        wiper, potentiometer = self._make(invert=False)
        wiper.value = 0
        self.assertEqual(potentiometer.wiper_position, 0.0)
        self.assertEqual(wiper.value, 0)
        wiper.value = 42
        self.assertEqual(potentiometer.wiper_position, 42 / 128)
        self.assertEqual(wiper.value, 42)

    def test_max_value_change_preserves_inverted_value(self):
        """Changing max_value keeps the user-facing value, not the raw code."""
        wiper, potentiometer = self._make(invert=True, max_value=128)
        wiper.value = 100
        self.assertEqual(potentiometer.wiper_position, 28 / 128)
        wiper.max_value = 256
        self.assertEqual(wiper.value, 100)
        self.assertEqual(potentiometer.wiper_position, 156 / 256)


if __name__ == "__main__":
    unittest.main()
