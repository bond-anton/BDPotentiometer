""" Tests for DigitalWiper constructor. """

import unittest

try:
    from src.BDPotentiometer import Potentiometer, DigitalWiper
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, DigitalWiper


class TestDigitalWiperConstructor(unittest.TestCase):
    """
    Testing DigitalWiper constructor.
    """

    def test_constructor(self) -> None:
        """
        Test DigitalWiper constructor
        """
        pot = Potentiometer(r_ab=10e3, r_w=75)
        # Normal constructor parameters
        for max_value in [1, 10, 128, 1024]:
            digital_wiper = DigitalWiper(potentiometer=pot, max_value=max_value)
            self.assertEqual(digital_wiper.potentiometer, pot)
            self.assertEqual(digital_wiper.max_value, max_value)
        # Wrong potentiometer type
        for pot_ in [None, "pot"]:
            with self.assertRaises(TypeError):
                _ = DigitalWiper(potentiometer=pot_, max_value=128)
        # Wrong max_value type
        for max_value in [None, "128"]:
            with self.assertRaises(TypeError):
                _ = DigitalWiper(potentiometer=pot, max_value=max_value)
        # Wrong max_value value
        for max_value in [0, -128, 12.6]:
            with self.assertRaises(ValueError):
                _ = DigitalWiper(potentiometer=pot, max_value=max_value)


if __name__ == "__main__":
    unittest.main()
