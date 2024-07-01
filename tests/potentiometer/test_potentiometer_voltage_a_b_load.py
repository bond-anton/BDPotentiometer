""" Tests for Potentiometer input voltage property. """

import unittest
import numpy as np

try:
    from src.BDPotentiometer import Potentiometer
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer


class TestPotentiometerVoltageIn(unittest.TestCase):
    """
    Testing Potentiometer input voltage property.
    """

    def setUp(self) -> None:
        self.pot = None

    def test_voltage_in(self):
        """
        Input voltage testing.
        For unlocked potentiometer and rheostat result is the same.
        """
        self.pot = Potentiometer(r_ab=10e3, r_w=75)
        self.assertEqual(self.pot.v_a, 0.0)  # Zero is the default voltage
        self.assertEqual(self.pot.v_b, 0.0)  # Zero is the default voltage
        self.assertEqual(self.pot.v_load, 0.0)  # Zero is the default voltage
        for voltage in [
            -5,
            -4.5,
            0,
            0.0,
            float("-0.0"),
            4.5,
            5,
            np.float32(4.2),
            np.float64(5.2),
        ]:
            self.pot.v_a = voltage
            self.assertEqual(self.pot.v_a, voltage)
            self.assertIsInstance(self.pot.v_a, float)
            self.pot.v_b = voltage
            self.assertEqual(self.pot.v_b, voltage)
            self.assertIsInstance(self.pot.v_b, float)
            self.pot.v_load = voltage
            self.assertEqual(self.pot.v_load, voltage)
            self.assertIsInstance(self.pot.v_load, float)
        for voltage in ["5.1", "a", None, [2.0], (1.1,)]:
            with self.assertRaises(TypeError):
                self.pot.v_a = voltage
            with self.assertRaises(TypeError):
                self.pot.v_b = voltage
            with self.assertRaises(TypeError):
                self.pot.v_load = voltage
        for voltage in [float("nan"), float("-inf"), float("inf")]:
            with self.assertRaises(ValueError):
                self.pot.v_a = voltage
            with self.assertRaises(ValueError):
                self.pot.v_b = voltage
            with self.assertRaises(ValueError):
                self.pot.v_load = voltage


if __name__ == "__main__":
    unittest.main()
