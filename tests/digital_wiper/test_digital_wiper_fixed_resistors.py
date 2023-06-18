""" Tests for DigitalWiper fixed resistors. """

import unittest
import numpy as np

try:
    from src.BDPotentiometer import Potentiometer, DigitalWiper
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, DigitalWiper


class TestDigitalWiperFixedResistors(unittest.TestCase):
    """
    Testing DigitalWiper fixed resistors.
    """

    def test_r_lim(self):
        """
        Tests current limiting resistor value altering.
        """
        pot = Potentiometer(
            r_ab=200e3, r_w=375, rheostat=False, parameters_locked=False
        )
        for locked in [True, False]:
            for max_value in [1, 14, 43]:
                digital_wiper = DigitalWiper(
                    potentiometer=pot, max_value=max_value, parameters_locked=locked
                )
                # Correct values (positive float numbers)
                for resistance in np.linspace(0, 104, num=101, endpoint=True):
                    digital_wiper.r_lim = resistance
                    self.assertEqual(digital_wiper.r_lim, resistance)
                    self.assertEqual(
                        digital_wiper.r_lim, digital_wiper.potentiometer.r_lim
                    )
                # Wrong values
                for resistance in [-200.4, -1]:
                    with self.assertRaises(ValueError):
                        digital_wiper.r_lim = resistance
                # Wrong type
                for resistance in [None, "100.2"]:
                    with self.assertRaises(TypeError):
                        digital_wiper.r_lim = resistance

    def test_r_load(self):
        """
        Tests load resistor value altering.
        """
        pot = Potentiometer(
            r_ab=170e3, r_w=145, rheostat=False, parameters_locked=False
        )
        for locked in [True, False]:
            for max_value in [1, 26, 51]:
                digital_wiper = DigitalWiper(
                    potentiometer=pot, max_value=max_value, parameters_locked=locked
                )
                # Correct values (positive float numbers)
                for resistance in np.linspace(0, 10e4, num=101, endpoint=True):
                    digital_wiper.r_load = resistance
                    self.assertEqual(digital_wiper.r_load, resistance)
                    self.assertEqual(
                        digital_wiper.r_load, digital_wiper.potentiometer.r_load
                    )
                # Wrong values
                for resistance in [-200.4, -1]:
                    with self.assertRaises(ValueError):
                        digital_wiper.r_load = resistance
                # Wrong type
                for resistance in [None, "100.2"]:
                    with self.assertRaises(TypeError):
                        digital_wiper.r_load = resistance


if __name__ == "__main__":
    unittest.main()
