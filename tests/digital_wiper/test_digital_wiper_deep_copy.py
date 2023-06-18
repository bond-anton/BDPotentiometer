""" Tests for DigitalWiper class deep copy. """

from copy import deepcopy
import unittest

try:
    from src.BDPotentiometer import Potentiometer, DigitalWiper, SpiDigitalWiper
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, DigitalWiper, SpiDigitalWiper


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
        self.spi_digital_wiper = SpiDigitalWiper(
            spi=None, potentiometer=self.pot, max_value=128, parameters_locked=False
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

    def test_spi_deepcopy(self):
        """
        Test deepcopy for SpiDigitalWiper.
        """

        self.spi_digital_wiper.r_lim = 200
        self.spi_digital_wiper.r_load = 1e100
        self.spi_digital_wiper.voltage_in = 5
        dw_copy = deepcopy(self.spi_digital_wiper)
        self.assertIsInstance(dw_copy, SpiDigitalWiper)
        self.assertNotEqual(dw_copy, self.spi_digital_wiper)
        self.assertNotEqual(dw_copy.potentiometer, self.spi_digital_wiper.potentiometer)
        self.assertEqual(dw_copy.min_value, self.spi_digital_wiper.min_value)
        self.assertEqual(dw_copy.max_value, self.spi_digital_wiper.max_value)
        self.assertEqual(
            dw_copy.potentiometer.r_ab, self.spi_digital_wiper.potentiometer.r_ab
        )
        self.assertEqual(
            dw_copy.potentiometer.r_w, self.spi_digital_wiper.potentiometer.r_w
        )
        self.assertEqual(
            dw_copy.potentiometer.r_lim, self.spi_digital_wiper.potentiometer.r_lim
        )
        self.assertEqual(
            dw_copy.potentiometer.r_load, self.spi_digital_wiper.potentiometer.r_load
        )
        self.assertEqual(
            dw_copy.potentiometer.voltage_in,
            self.spi_digital_wiper.potentiometer.voltage_in,
        )
        self.assertEqual(dw_copy.spi, self.spi_digital_wiper.spi)


if __name__ == "__main__":
    unittest.main()
