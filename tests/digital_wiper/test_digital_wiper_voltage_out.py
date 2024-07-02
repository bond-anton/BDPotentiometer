""" Tests for DigitalWiper output voltage property. """

import unittest
import numpy as np

try:
    from src.BDPotentiometer import Potentiometer, DigitalWiper
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, DigitalWiper


class TestDigitalWiperVoltageOut(unittest.TestCase):
    """
    Testing DigitalWiper `voltage_out`.
    """

    def test_voltage_out(self):
        """
        Test output voltage property and methods.
        """
        pot = Potentiometer(r_ab=101e3, r_w=185)
        for max_value in [1, 15, 33]:
            digital_wiper = DigitalWiper(potentiometer=pot, max_value=max_value)
            digital_wiper.potentiometer.r_a = 123.5
            digital_wiper.potentiometer.r_b = 0
            digital_wiper.potentiometer.r_load = 1e6
            digital_wiper.potentiometer.v_b = 0
            digital_wiper.potentiometer.v_load = 0
            # Correct values (positive float numbers)
            digital_wiper.potentiometer.v_a = 5
            for voltage in np.linspace(0, 5, num=13, endpoint=True):
                digital_wiper.v_w = voltage
                np.testing.assert_allclose(
                    digital_wiper.v_w, digital_wiper.potentiometer.v_w
                )
            digital_wiper.potentiometer.v_a = -5
            for voltage in np.linspace(-5, 0, num=13, endpoint=True):
                digital_wiper.v_w = voltage
                np.testing.assert_allclose(
                    digital_wiper.v_w, digital_wiper.potentiometer.v_w
                )
            for voltage in np.linspace(0, 5, num=13, endpoint=True):
                digital_wiper.v_w = voltage
                self.assertEqual(digital_wiper.v_w, 0)
            digital_wiper.potentiometer.v_a = 0
            for voltage in np.linspace(-5, 5, num=13, endpoint=True):
                digital_wiper.v_w = voltage
                self.assertEqual(digital_wiper.v_w, 0)
            digital_wiper.potentiometer.r_load = 0
            digital_wiper.potentiometer.v_a = 5
            for voltage in np.linspace(-5, 5, num=13, endpoint=True):
                digital_wiper.v_w = voltage
                self.assertEqual(digital_wiper.v_w, 0)
            # Wrong type
            for voltage in [None, "100.2"]:
                with self.assertRaises(TypeError):
                    digital_wiper.v_w = voltage


if __name__ == "__main__":
    unittest.main()
