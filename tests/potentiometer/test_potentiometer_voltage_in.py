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
        for rheostat in [True, False]:
            self.pot = Potentiometer(
                r_ab=10e3, r_w=75, rheostat=rheostat, parameters_locked=False
            )
            self.assertEqual(self.pot.voltage_in, 0.0)  # Zero is default input voltage
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
                self.pot.voltage_in = voltage
                self.assertEqual(self.pot.voltage_in, voltage)
                self.assertIsInstance(self.pot.voltage_in, float)
            for voltage in ["5.1", "a", None, [2.0], (1.1,)]:
                with self.assertRaises(TypeError):
                    self.pot.voltage_in = voltage
            for voltage in [float("nan"), float("-inf"), float("inf")]:
                with self.assertRaises(ValueError):
                    self.pot.voltage_in = voltage


if __name__ == "__main__":
    unittest.main()
