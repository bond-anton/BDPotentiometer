""" Tests for DigitalWiper min max value properties. """

import unittest

try:
    from src.BDPotentiometer import Potentiometer, DigitalWiper
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, DigitalWiper


class TestDigitalWiperMinMaxValue(unittest.TestCase):
    """
    Testing DigitalWiper `min_value` and `max_value` properties.
    """

    def test_min_value(self):
        """
        Testing `min_value` property.
        Should always be zero and can not be changed&
        """
        pot = Potentiometer(r_ab=50e3, r_w=200, rheostat=False, parameters_locked=False)
        for locked in [True, False]:
            for max_value in [1, 32, 64, 256]:
                digital_wiper = DigitalWiper(
                    potentiometer=pot, max_value=max_value, parameters_locked=locked
                )
                self.assertEqual(digital_wiper.min_value, 0)
                for min_value_ in [None, -1, 1, "1", "0", 0]:
                    with self.assertRaises(AttributeError):
                        digital_wiper.min_value = min_value_

    def test_max_value(self):
        """
        Testing `max_value` property.
        In contrast with `min_value`, `max_value` can be altered unless wiper is locked.
        `max_value` must be positive int number.
        """
        pot = Potentiometer(
            r_ab=100e3, r_w=175, rheostat=False, parameters_locked=False
        )
        for locked in [True, False]:
            for max_value in [1, 16, 32, 2048]:
                digital_wiper = DigitalWiper(
                    potentiometer=pot, max_value=max_value, parameters_locked=locked
                )
                self.assertEqual(digital_wiper.max_value, max_value)
                # Correct values
                for max_value_new in [1, 10, 128, 1024, 128.0]:
                    digital_wiper.max_value = max_value_new
                    if not digital_wiper.parameters_locked:
                        self.assertEqual(digital_wiper.max_value, max_value_new)
                    else:
                        self.assertEqual(digital_wiper.max_value, max_value)
                # Wrong value
                for max_value_ in [0, -1, -10, 128.5]:
                    with self.assertRaises(ValueError):
                        digital_wiper.max_value = max_value_
                # Wrong type
                for max_value_ in [None, "1"]:
                    with self.assertRaises(TypeError):
                        digital_wiper.max_value = max_value_
                # Check that value did not change
                if not digital_wiper.parameters_locked:
                    self.assertEqual(digital_wiper.max_value, max_value_new)
                else:
                    self.assertEqual(digital_wiper.max_value, max_value)


if __name__ == "__main__":
    unittest.main()
