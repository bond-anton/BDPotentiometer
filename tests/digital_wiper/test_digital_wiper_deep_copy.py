""" Tests for DigitalWiper class deep copy. """

from copy import deepcopy
import unittest

try:
    from src.BDPotentiometer import Potentiometer, DigitalWiper
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, DigitalWiper


class TestDigitalWiperDeepCopy(unittest.TestCase):
    """
    Testing DigitalWiper deep copy.
    """

    def setUp(self) -> None:
        """
        Set up Unittest
        """
        self.pot = Potentiometer(
            r_ab=10e3, r_w=75, rheostat=False, parameters_locked=False
        )
        self.digital_wiper = DigitalWiper(
            potentiometer=self.pot, max_value=128, parameters_locked=False
        )
        self.digital_wiper_locked = DigitalWiper(
            potentiometer=self.pot, max_value=128, parameters_locked=True
        )

    def test_deepcopy(self):
        """
        Test deepcopy.
        """
        self.digital_wiper.r_lim = 200
        self.digital_wiper.r_load = 1e100
        self.digital_wiper.voltage_in = 5
        dw_copy = deepcopy(self.digital_wiper)
        self.assertIsInstance(dw_copy, DigitalWiper)
        self.assertNotEqual(dw_copy, self.digital_wiper)
        self.assertNotEqual(dw_copy.potentiometer, self.digital_wiper.potentiometer)
        self.assertEqual(dw_copy.min_value, self.digital_wiper.min_value)
        self.assertEqual(dw_copy.max_value, self.digital_wiper.max_value)
        self.assertEqual(
            dw_copy.potentiometer.r_ab, self.digital_wiper.potentiometer.r_ab
        )
        self.assertEqual(
            dw_copy.potentiometer.r_w, self.digital_wiper.potentiometer.r_w
        )
        self.assertEqual(
            dw_copy.potentiometer.r_lim, self.digital_wiper.potentiometer.r_lim
        )
        self.assertEqual(
            dw_copy.potentiometer.r_load, self.digital_wiper.potentiometer.r_load
        )
        self.assertEqual(
            dw_copy.potentiometer.voltage_in,
            self.digital_wiper.potentiometer.voltage_in,
        )


if __name__ == "__main__":
    unittest.main()
