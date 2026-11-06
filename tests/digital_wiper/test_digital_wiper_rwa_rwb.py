"""Tests for DigitalWiper `r_wa` and `r_wb` calculations."""

import unittest

try:
    from src.BDPotentiometer import DigitalWiper, Potentiometer
except ModuleNotFoundError:
    from BDPotentiometer import DigitalWiper, Potentiometer


class TestDigitalWiperRwaRwb(unittest.TestCase):
    """
    Testing DigitalWiper `r_wa` and `r_wb` calculations.
    """

    def test_rwa_sets_wiper_position(self):
        """
        Setting `r_wa` moves the potentiometer wiper from A to B.
        """
        potentiometer = Potentiometer(r_ab=111e3, r_w=174)
        for max_value in [1, 26, 41]:
            wiper = DigitalWiper(potentiometer=potentiometer, max_value=max_value)
            for resistance, expected_position in [
                (potentiometer.r_w, 1.0),
                (potentiometer.r_w + potentiometer.r_ab / 2, 0.5),
                (potentiometer.r_w + potentiometer.r_ab, 0.0),
            ]:
                wiper.r_wa = resistance
                self.assertAlmostEqual(
                    wiper.potentiometer.wiper_position, expected_position
                )
                self.assertAlmostEqual(wiper.r_wa, resistance)

    def test_rwb_sets_wiper_position(self):
        """
        Setting `r_wb` moves the potentiometer wiper from B to A.
        """
        potentiometer = Potentiometer(r_ab=111e3, r_w=174)
        for max_value in [1, 26, 41]:
            wiper = DigitalWiper(potentiometer=potentiometer, max_value=max_value)
            for resistance, expected_position in [
                (potentiometer.r_w, 0.0),
                (potentiometer.r_w + potentiometer.r_ab / 2, 0.5),
                (potentiometer.r_w + potentiometer.r_ab, 1.0),
            ]:
                wiper.r_wb = resistance
                self.assertAlmostEqual(
                    wiper.potentiometer.wiper_position, expected_position
                )
                self.assertAlmostEqual(wiper.r_wb, resistance)

    def test_low_resistance_is_clamped_to_wiper_resistance(self):
        """
        Values below `r_w` are clamped to the wiper resistance.
        """
        potentiometer = Potentiometer(r_ab=111e3, r_w=174)
        wiper = DigitalWiper(potentiometer=potentiometer, max_value=128)
        for resistance in [-10.2, 0, potentiometer.r_w - 0.1, potentiometer.r_w]:
            wiper.r_wa = resistance
            self.assertEqual(wiper.r_wa, potentiometer.r_w)
            self.assertEqual(wiper.potentiometer.wiper_position, 1.0)
            wiper.r_wb = resistance
            self.assertEqual(wiper.r_wb, potentiometer.r_w)
            self.assertEqual(wiper.potentiometer.wiper_position, 0.0)

    def test_high_resistance_is_clamped_to_full_scale(self):
        """
        Values above `r_ab + r_w` are clamped to full scale.
        """
        potentiometer = Potentiometer(r_ab=111e3, r_w=174)
        wiper = DigitalWiper(potentiometer=potentiometer, max_value=128)
        for resistance in [
            potentiometer.r_ab + potentiometer.r_w * 10,
            potentiometer.r_ab + potentiometer.r_w + 0.1,
            potentiometer.r_ab + potentiometer.r_w,
        ]:
            wiper.r_wa = resistance
            self.assertEqual(wiper.r_wa, potentiometer.r_ab + potentiometer.r_w)
            self.assertEqual(wiper.potentiometer.wiper_position, 0.0)
            wiper.r_wb = resistance
            self.assertEqual(wiper.r_wb, potentiometer.r_ab + potentiometer.r_w)
            self.assertEqual(wiper.potentiometer.wiper_position, 1.0)

    def test_wrong_value_type_raises(self):
        """
        Non-numeric resistances are rejected.
        """
        potentiometer = Potentiometer(r_ab=111e3, r_w=174)
        wiper = DigitalWiper(potentiometer=potentiometer, max_value=128)
        for resistance in [None, "5.1"]:
            with self.assertRaises(TypeError):
                wiper.r_wa = resistance
            with self.assertRaises(TypeError):
                wiper.r_wb = resistance


if __name__ == "__main__":
    unittest.main()
