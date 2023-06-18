""" Tests for DigitalWiper input voltage property. """

import unittest
import numpy as np

try:
    from src.BDPotentiometer import Potentiometer, DigitalWiper
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, DigitalWiper


class TestDigitalWiperVoltageIn(unittest.TestCase):
    """
    Testing DigitalWiper `voltage_in`.
    """

    def test_voltage_in(self):
        """
        Test input voltage property and methods.
        """
        pot = Potentiometer(
            r_ab=104e3, r_w=275, rheostat=False, parameters_locked=False
        )
        for locked in [True, False]:
            for max_value in [1, 11, 37]:
                digital_wiper = DigitalWiper(
                    potentiometer=pot, max_value=max_value, parameters_locked=locked
                )
                # Correct values (positive float numbers)
                for voltage in np.linspace(-51, 51, num=107, endpoint=True):
                    digital_wiper.voltage_in = voltage
                    self.assertEqual(digital_wiper.voltage_in, voltage)
                    self.assertEqual(
                        digital_wiper.voltage_in, digital_wiper.potentiometer.voltage_in
                    )
                digital_wiper.voltage_in = 0
                self.assertEqual(digital_wiper.voltage_in, 0)
                self.assertEqual(
                    digital_wiper.voltage_in, digital_wiper.potentiometer.voltage_in
                )
                # Wrong type
                for voltage in [None, "100.2"]:
                    with self.assertRaises(TypeError):
                        digital_wiper.voltage_in = voltage


if __name__ == "__main__":
    unittest.main()
