""" Tests for DigitalWiper class. """

from copy import deepcopy
import unittest
import numpy as np

try:
    from src.BDPotentiometer import Potentiometer, DigitalWiper, SpiDigitalWiper
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, DigitalWiper, SpiDigitalWiper


class TestDigitalWiper(unittest.TestCase):
    """
    Testing DigitalWiper.
    """

    def setUp(self) -> None:
        """
        Set up Unittest
        """
        self.pot = Potentiometer(r_ab=10e3, r_w=75, rheostat=False, locked=False)
        self.digital_wiper = DigitalWiper(
            potentiometer=self.pot, max_value=128, parameters_locked=False
        )
        self.digital_wiper_locked = DigitalWiper(
            potentiometer=self.pot, max_value=128, parameters_locked=True
        )
        self.spi_digital_wiper = SpiDigitalWiper(
            spi=None, potentiometer=self.pot, max_value=128, parameters_locked=False
        )

    def test_basic_properties(self):
        """
        Testing basic parameters.
        """
        self.assertEqual(self.digital_wiper.potentiometer, self.pot)
        self.assertEqual(self.digital_wiper.locked, False)
        self.assertEqual(self.digital_wiper_locked.locked, True)

    def test_channel_numbering(self):
        """
        Testing channel numbering.
        """
        self.assertEqual(self.digital_wiper.channel, 0)
        self.digital_wiper.channel = 3
        self.assertEqual(self.digital_wiper.channel, 3)
        with self.assertRaises(ValueError):
            self.digital_wiper.channel = -3
        with self.assertRaises(ValueError):
            self.digital_wiper.channel = "A"
        self.assertEqual(self.digital_wiper.channel, 3)

    def test_min_value(self):
        """
        Testing min_value property.
        """
        self.assertEqual(self.digital_wiper.min_value, 0)
        with self.assertRaises(AttributeError):
            self.digital_wiper.min_value = 1

    def test_max_value(self):
        """
        Testing max_value property.
        """
        self.assertEqual(self.digital_wiper.max_value, 128)
        self.digital_wiper.max_value = 1
        self.assertEqual(self.digital_wiper.max_value, 1)
        self.digital_wiper.max_value = 256
        self.assertEqual(self.digital_wiper.max_value, 256)
        with self.assertRaises(ValueError):
            self.digital_wiper.max_value = -10
        with self.assertRaises(ValueError):
            self.digital_wiper.max_value = 0
        with self.assertRaises(ValueError):
            self.digital_wiper.max_value = 128.5

    def test_value_get_set(self):
        """
        Testing value property and corresponding get_ and set_ methods.
        """
        self.assertEqual(self.digital_wiper.value, 0)
        self.digital_wiper.value = 10
        self.assertEqual(self.digital_wiper.value, 10)
        self.digital_wiper.value = 11.0
        self.assertEqual(self.digital_wiper.value, 11)
        with self.assertRaises(ValueError):
            self.digital_wiper.value = 12.5
        self.digital_wiper.value = -10
        self.assertEqual(self.digital_wiper.value, 0)
        self.digital_wiper.value = self.digital_wiper.max_value + 1
        self.assertEqual(self.digital_wiper.value, self.digital_wiper.max_value)

    def test_value_relative(self):
        """
        Test relative value calculation.
        """
        self.digital_wiper.value_relative = 0
        self.assertEqual(self.digital_wiper.value_relative, 0)
        self.assertEqual(self.digital_wiper.value, 0)
        self.digital_wiper.value_relative = -0.1
        self.assertEqual(self.digital_wiper.value_relative, 0)
        self.digital_wiper.value_relative = 1
        self.assertEqual(self.digital_wiper.value_relative, 1)
        self.digital_wiper.value_relative = 2.5
        self.assertEqual(self.digital_wiper.value_relative, 1)
        self.assertEqual(self.digital_wiper.value, self.digital_wiper.max_value)
        for value_rel in np.linspace(0, 1, num=501, endpoint=True):
            value_int = int(round(value_rel * self.digital_wiper.max_value))
            value_rel_coerced = value_int / self.digital_wiper.max_value
            self.digital_wiper.value_relative = value_rel
            self.assertEqual(self.digital_wiper.value, value_int)
            self.assertEqual(self.digital_wiper.value_relative, value_rel_coerced)

        with self.assertRaises(ValueError):
            self.digital_wiper.value_relative = "0.5"

    def test_voltage_in(self):
        """
        Test input voltage property and methods.
        """
        self.assertEqual(self.digital_wiper.voltage_in, 0)
        self.digital_wiper.voltage_in = 5
        self.assertEqual(self.digital_wiper.voltage_in, 5)
        self.digital_wiper.voltage_in = -5.1
        self.assertEqual(self.digital_wiper.voltage_in, -5.1)
        with self.assertRaises(ValueError):
            self.digital_wiper.voltage_in = "5.1"

    def test_rwa_rwb(self):
        """
        Test r_wa and r_wb settings.
        """
        for resistance in np.linspace(
            self.pot.r_w, self.pot.r_ab + self.pot.r_w, num=101, endpoint=True
        ):
            self.digital_wiper.r_wa = resistance
            pos = self.digital_wiper.value_relative
            self.assertEqual(
                self.digital_wiper.r_wa, self.digital_wiper.potentiometer.r_wa(pos)
            )
            self.assertEqual(
                self.digital_wiper.r_wb, self.digital_wiper.potentiometer.r_wb(pos)
            )
            self.digital_wiper.r_wb = resistance
            pos = self.digital_wiper.value_relative
            self.assertEqual(
                self.digital_wiper.r_wa, self.digital_wiper.potentiometer.r_wa(pos)
            )
            self.assertEqual(
                self.digital_wiper.r_wb, self.digital_wiper.potentiometer.r_wb(pos)
            )

    def test_r_lim(self):
        """
        Tets current limit resistor value altering
        """
        self.digital_wiper.r_lim = 0
        self.assertEqual(self.digital_wiper.r_lim, 0)
        self.digital_wiper.r_lim = 200.5
        self.assertEqual(self.digital_wiper.r_lim, 200.5)
        with self.assertRaises(ValueError):
            self.digital_wiper.r_lim = -200
        with self.assertRaises(ValueError):
            self.digital_wiper.r_lim = "200"

    def test_r_load(self):
        """
        Tets load resistor value altering
        """
        self.digital_wiper.r_load = 0
        self.assertEqual(self.digital_wiper.r_load, 0)
        self.digital_wiper.r_load = 2.5e3
        self.assertEqual(self.digital_wiper.r_load, 2.5e3)
        with self.assertRaises(ValueError):
            self.digital_wiper.r_load = -200
        with self.assertRaises(ValueError):
            self.digital_wiper.r_load = "200"

    def test_voltage_out(self):
        """
        Test output voltage correct calculation.
        """
        self.digital_wiper.r_lim = 200
        self.digital_wiper.r_load = 1e100
        self.digital_wiper.voltage_in = 5
        for voltage in np.linspace(0, 5, num=101, endpoint=True):
            self.digital_wiper.voltage_out = voltage
            np.testing.assert_allclose(
                self.digital_wiper.voltage_out,
                self.digital_wiper.potentiometer.voltage_out(
                    self.digital_wiper.value_relative
                ),
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

    def test_spi_digital_wiper(self):
        """
        Test SpiDigitalWiper constructor (without SPI interface).
        """
        digital_wiper = SpiDigitalWiper(
            spi=None, potentiometer=self.pot, max_value=128, parameters_locked=False
        )
        self.assertEqual(digital_wiper.spi, None)
        digital_wiper.spi = None
        self.assertEqual(digital_wiper.spi, None)

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
