""" Tests for DigitalWinder class. """

import unittest
import numpy as np

from src.BDPotentiometer import Potentiometer, DigitalWinder, SpiDigitalWinder


class TestDigitalWinder(unittest.TestCase):
    """
    Testing DigitalWinder.
    """

    def test_basic_properties(self):
        """
        Testing basic parameters.
        """
        pot = Potentiometer(r_ab=10e3, r_w=75, rheostat=False, locked=False)
        digital_winder = DigitalWinder(potentiometer=pot, max_value=128, parameters_locked=False)
        self.assertEqual(digital_winder.potentiometer, pot)
        self.assertEqual(digital_winder.locked, False)
        self.assertEqual(digital_winder.channel, 0)
        digital_winder.channel = 3
        self.assertEqual(digital_winder.channel, 3)
        with self.assertRaises(ValueError):
            digital_winder.channel = -3
        self.assertEqual(digital_winder.channel, 3)
        self.assertEqual(digital_winder.min_value, 0)
        with self.assertRaises(AttributeError):
            digital_winder.min_value = 1
        self.assertEqual(digital_winder.max_value, 128)
        digital_winder.max_value = 256
        self.assertEqual(digital_winder.max_value, 256)
        with self.assertRaises(ValueError):
            digital_winder.max_value = -10
        with self.assertRaises(ValueError):
            digital_winder.max_value = 128.5
        self.assertEqual(digital_winder.value, 0)
        digital_winder.value = 10
        self.assertEqual(digital_winder.value, 10)
        digital_winder.value = -10
        self.assertEqual(digital_winder.value, 0)
        digital_winder.value = 257
        self.assertEqual(digital_winder.value, 256)
        with self.assertRaises(ValueError):
            digital_winder.value = 12.5
        self.assertEqual(digital_winder.voltage_in, 0)
        digital_winder.voltage_in = 5
        self.assertEqual(digital_winder.voltage_in, 5)

    def test_rwa_rwb(self):
        """
        Test r_wa and r_wb settings.
        """
        pot = Potentiometer(r_ab=10e3, r_w=75, rheostat=False, locked=False)
        digital_winder = DigitalWinder(potentiometer=pot, max_value=128, parameters_locked=False)
        for resistance in np.linspace(pot.r_w, pot.r_ab + pot.r_w,
                                      num=101, endpoint=True):
            digital_winder.r_wa = resistance
            pos = digital_winder.value / digital_winder.max_value
            self.assertEqual(digital_winder.r_wa,
                             digital_winder.potentiometer.r_wa(pos))
            self.assertEqual(digital_winder.r_wb,
                             digital_winder.potentiometer.r_wb(pos))
            digital_winder.r_wb = resistance
            pos = digital_winder.value / digital_winder.max_value
            self.assertEqual(digital_winder.r_wa,
                             digital_winder.potentiometer.r_wa(pos))
            self.assertEqual(digital_winder.r_wb,
                             digital_winder.potentiometer.r_wb(pos))

    def test_voltage_out(self):
        """
        Test output voltage correct calculation.
        """
        pot = Potentiometer(r_ab=10e3, r_w=75, rheostat=False, locked=False)
        pot.r_lim = 200
        pot.r_load = 1e100
        digital_winder = DigitalWinder(potentiometer=pot, max_value=128, parameters_locked=False)
        digital_winder.voltage_in = 5
        for voltage in np.linspace(0, 5, num=101, endpoint=True):
            digital_winder.voltage_out = voltage
            pos = digital_winder.value / digital_winder.max_value
            np.testing.assert_allclose(digital_winder.voltage_out,
                                       digital_winder.potentiometer.voltage_out(pos))

    def test_spi_digital_winder(self):
        """
        Test SpiDigitalWinder constructor (without SPI interface).
        """
        pot = Potentiometer(r_ab=10e3, r_w=75, rheostat=False, locked=False)
        digital_winder = SpiDigitalWinder(spi=None, potentiometer=pot,
                                          max_value=128, parameters_locked=False)
        self.assertEqual(digital_winder.spi, None)
        digital_winder.spi = None
        self.assertEqual(digital_winder.spi, None)


if __name__ == '__main__':
    unittest.main()
