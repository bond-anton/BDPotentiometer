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
        pot = Potentiometer(r_ab=10e3, r_w=75, rheostat=False, parameters_locked=False)
        # Normal constructor parameters
        for locked in [True, False]:
            for max_value in [1, 10, 128, 1024]:
                digital_wiper = DigitalWiper(
                    potentiometer=pot, max_value=max_value, parameters_locked=locked
                )
                self.assertEqual(digital_wiper.potentiometer, pot)
                self.assertEqual(digital_wiper.parameters_locked, locked)
                self.assertEqual(digital_wiper.max_value, max_value)
        # Wrong potentiometer type
        for locked in [True, False]:
            for pot_ in [None, "pot"]:
                with self.assertRaises(TypeError):
                    _ = DigitalWiper(
                        potentiometer=pot_, max_value=128, parameters_locked=locked
                    )
        # Wrong max_value type
        for locked in [True, False]:
            for max_value in [None, "128"]:
                with self.assertRaises(TypeError):
                    _ = DigitalWiper(
                        potentiometer=pot, max_value=max_value, parameters_locked=locked
                    )
        # Wrong max_value value
        for locked in [True, False]:
            for max_value in [0, -128, 12.6]:
                with self.assertRaises(ValueError):
                    _ = DigitalWiper(
                        potentiometer=pot, max_value=max_value, parameters_locked=locked
                    )


if __name__ == "__main__":
    unittest.main()
