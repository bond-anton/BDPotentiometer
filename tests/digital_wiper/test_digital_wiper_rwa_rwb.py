""" Tests for DigitalWiper `r_wa` and `r_wb` calculations. """

import unittest
import numpy as np

try:
    from src.BDPotentiometer import Potentiometer, DigitalWiper
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, DigitalWiper


class TestDigitalWiperRwaRwb(unittest.TestCase):
    """
    Testing DigitalWiper `r_wa` and `r_wb` calculations.
    """

    def test_rwa_rwb(self):
        """
        Test `r_wa` and `r_wb` properties.
        """
        pot = Potentiometer(r_ab=111e3, r_w=174)
        for max_value in [1, 26, 41]:
            digital_wiper = DigitalWiper(potentiometer=pot, max_value=max_value)
            # Correct values
            for resistance in np.linspace(
                pot.r_w, pot.r_ab + pot.r_w, num=101, endpoint=True
            ):
                digital_wiper.r_wa = resistance
                self.assertEqual(digital_wiper.r_wa, digital_wiper.potentiometer.r_wa)
                self.assertEqual(digital_wiper.r_wb, digital_wiper.potentiometer.r_wb)
                digital_wiper.r_wb = resistance
                self.assertEqual(digital_wiper.r_wa, digital_wiper.potentiometer.r_wa)
                self.assertEqual(digital_wiper.r_wb, digital_wiper.potentiometer.r_wb)
            # Values less than r_w are clamped to r_w
            for resistance in [-10.2, 0, pot.r_w - 0.1, pot.r_w]:
                digital_wiper.r_wa = resistance
                digital_wiper.r_wa = pot.r_w
                self.assertEqual(digital_wiper.r_wa, digital_wiper.potentiometer.r_wa)
                self.assertEqual(digital_wiper.r_wb, digital_wiper.potentiometer.r_wb)
                digital_wiper.r_wb = resistance
                digital_wiper.r_wb = pot.r_w
                self.assertEqual(digital_wiper.r_wa, digital_wiper.potentiometer.r_wa)
                self.assertEqual(digital_wiper.r_wb, digital_wiper.potentiometer.r_wb)
            # Values greater than r_ab + r_w are clamped to r_ab + r_w
            for resistance in [
                pot.r_ab + pot.r_w * 10,
                pot.r_ab + pot.r_w + 0.1,
                pot.r_ab + pot.r_w,
            ]:
                digital_wiper.r_wa = resistance
                self.assertEqual(digital_wiper.r_wa, pot.r_ab + pot.r_w)
                digital_wiper.r_wb = resistance
                self.assertEqual(digital_wiper.r_wb, pot.r_ab + pot.r_w)
            # Wrong value type
            for resistance in [None, "5.1"]:
                with self.assertRaises(TypeError):
                    digital_wiper.r_wa = resistance
                with self.assertRaises(TypeError):
                    digital_wiper.r_wb = resistance


if __name__ == "__main__":
    unittest.main()
