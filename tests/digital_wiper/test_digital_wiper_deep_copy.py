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
        self.pot = Potentiometer(r_ab=10e3, r_w=75)
        self.digital_wiper = DigitalWiper(potentiometer=self.pot, max_value=128)
        self.digital_wiper_locked = DigitalWiper(potentiometer=self.pot, max_value=128)

    def test_deepcopy(self):
        """
        Test deepcopy.
        """
        self.digital_wiper.r_a = 200
        self.digital_wiper.r_b = 100
        self.digital_wiper.r_load = 1e100
        self.digital_wiper.v_a = 5
        self.digital_wiper.v_b = 0
        self.digital_wiper.v_load = 0
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
            dw_copy.potentiometer.r_a, self.digital_wiper.potentiometer.r_a
        )
        self.assertEqual(
            dw_copy.potentiometer.r_b, self.digital_wiper.potentiometer.r_b
        )
        self.assertEqual(
            dw_copy.potentiometer.r_load, self.digital_wiper.potentiometer.r_load
        )
        self.assertEqual(
            dw_copy.potentiometer.v_a, self.digital_wiper.potentiometer.v_a
        )
        self.assertEqual(
            dw_copy.potentiometer.v_b, self.digital_wiper.potentiometer.v_b
        )
        self.assertEqual(
            dw_copy.potentiometer.v_load, self.digital_wiper.potentiometer.v_load
        )


if __name__ == "__main__":
    unittest.main()
