""" Tests for DigitalWiper value get and set operations. """

import unittest
import numpy as np

try:
    from src.BDPotentiometer import Potentiometer, DigitalWiper
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, DigitalWiper


class TestDigitalWiperValue(unittest.TestCase):
    """
    Testing DigitalWiper `value` property.
    """

    def test_value_get_set(self):
        """
        Testing `value` property.
        """
        pot = Potentiometer(
            r_ab=100e3, r_w=175, rheostat=False, parameters_locked=False
        )
        for locked in [True, False]:
            for max_value in [1, 16, 31]:
                digital_wiper = DigitalWiper(
                    potentiometer=pot, max_value=max_value, parameters_locked=locked
                )
                # Correct values
                for value_new in np.arange(max_value):
                    digital_wiper.value = value_new
                    self.assertEqual(digital_wiper.value, value_new)
                # Check correct float values
                for value_new in [0.0, 1.0]:
                    digital_wiper.value = value_new
                    self.assertEqual(digital_wiper.value, value_new)
                # Values less than 0 will be clamped to zero
                for value_new in [-10, -1, 0]:
                    digital_wiper.value = value_new
                    self.assertEqual(digital_wiper.value, 0)
                # Values greater than max_value will be clamped to max_value
                for value_new in [max_value, max_value + 1, max_value + 10]:
                    digital_wiper.value = value_new
                    self.assertEqual(digital_wiper.value, max_value)
                    self.assertEqual(digital_wiper.value, digital_wiper.max_value)
        # Wrong parameter value (non int number)
        for value_new in [-1.1, 0.2, 12.5]:
            with self.assertRaises(ValueError):
                digital_wiper.value = value_new
        # Wrong parameter type
        for value_new in [None, "1"]:
            with self.assertRaises(TypeError):
                digital_wiper.value = value_new

    def test_value_relative(self):
        """
        Test relative value calculation.
        """
        pot = Potentiometer(
            r_ab=100e3, r_w=175, rheostat=False, parameters_locked=False
        )
        for locked in [True, False]:
            for max_value in [1, 16, 31]:
                digital_wiper = DigitalWiper(
                    potentiometer=pot, max_value=max_value, parameters_locked=locked
                )
                # Correct values
                for value_r_new in np.linspace(0, 1, num=51, endpoint=True):
                    digital_wiper.value_relative = value_r_new
                    value_int = int(round(value_r_new * digital_wiper.max_value))
                    value_r_new_coerced = value_int / digital_wiper.max_value
                    self.assertEqual(digital_wiper.value_relative, value_r_new_coerced)
                    self.assertEqual(digital_wiper.value, value_int)
                # Values less than 0 will be clamped to zero
                for value_r_new in [-10.2, -3.3, -1, 0, 0.0]:
                    digital_wiper.value_relative = value_r_new
                    self.assertEqual(digital_wiper.value_relative, 0)
                    self.assertEqual(digital_wiper.value, 0)
                # Values greater than 1 will be clamped to 1
                for value_r_new in [1, 1.0, 1.1, 12, 35.6]:
                    digital_wiper.value_relative = value_r_new
                    self.assertEqual(digital_wiper.value_relative, 1)
                    self.assertEqual(digital_wiper.value, max_value)
                    self.assertEqual(digital_wiper.value, digital_wiper.max_value)
        # Wrong parameter type
        for value_r_new in [None, "1"]:
            with self.assertRaises(TypeError):
                digital_wiper.value_relative = value_r_new


if __name__ == "__main__":
    unittest.main()
