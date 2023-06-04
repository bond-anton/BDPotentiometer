""" Tests for DigitalPotentiometerDevice class. """

import unittest

try:
    from src.BDPotentiometer import (
        Potentiometer,
        DigitalWinder,
        DigitalPotentiometerDevice,
    )
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, DigitalWinder, DigitalPotentiometerDevice


class TestDigitalPotentiometer(unittest.TestCase):
    """
    Testing DigitalPotentiometerDevice.
    """

    def setUp(self) -> None:
        self.pot = Potentiometer(r_ab=10e3, r_w=75, rheostat=False, locked=False)
        digital_winder = DigitalWinder(
            potentiometer=self.pot, max_value=128, parameters_locked=False
        )
        self.digital_pot = DigitalPotentiometerDevice(winder=digital_winder, channels=2)
        self.digital_pot.set_channel_label(0, "CH A")
        self.digital_pot.set_channel_label(1, "CH B")

    def test_basic_properties(self):
        """
        Testing basic parameters.
        """
        pot = Potentiometer(r_ab=10e3, r_w=75, rheostat=False, locked=False)
        digital_winder = DigitalWinder(
            potentiometer=pot, max_value=128, parameters_locked=False
        )
        digital_pot = DigitalPotentiometerDevice(winder=digital_winder, channels=3)
        self.assertEqual(digital_pot.channels_num, 3)
        channels = digital_pot.channels
        for channel_number, winder in channels.items():
            self.assertEqual(winder.potentiometer.r_ab, pot.r_ab)
            self.assertEqual(winder.potentiometer.r_w, pot.r_w)
            self.assertEqual(winder.potentiometer.r_lim, pot.r_lim)
            self.assertEqual(winder.max_value, digital_winder.max_value)
            self.assertEqual(
                channel_number,
                digital_pot.get_channel_number_by_label(str(channel_number)),
            )
            self.assertEqual(
                channel_number,
                digital_pot._get_channel_number_by_label_or_id(str(channel_number)),
            )
            self.assertEqual(
                channel_number,
                digital_pot._get_channel_number_by_label_or_id(channel_number),
            )

    def test_channel_labels(self):
        """
        Test channels labeling system
        """
        self.digital_pot.set_channel_label(0, "CH A")
        self.digital_pot.set_channel_label(1, "CH B")
        self.assertEqual(0, self.digital_pot.get_channel_number_by_label("CH A"))
        self.assertEqual(1, self.digital_pot.get_channel_number_by_label("CH B"))
        self.assertEqual(0, self.digital_pot._get_channel_number_by_label_or_id(0))
        self.assertEqual(1, self.digital_pot._get_channel_number_by_label_or_id(1))
        self.assertEqual(1, self.digital_pot._get_channel_number_by_label_or_id("CH B"))
        self.assertIsNone(self.digital_pot.get_channel_number_by_label("CH C"))
        self.assertIsNone(self.digital_pot._get_channel_number_by_label_or_id("CH C"))
        self.assertIsNone(self.digital_pot._get_channel_number_by_label_or_id(3))
        with self.assertRaises(ValueError):
            self.digital_pot._get_channel_number_by_label_or_id(1.1)
        with self.assertRaises(ValueError):
            self.digital_pot._get_channel_number_by_label_or_id(-1)
        self.digital_pot.set_channel_label(0, None)
        self.assertEqual(0, self.digital_pot.get_channel_number_by_label("0"))
        self.digital_pot.set_channel_label(0, "CH A")
        with self.assertRaises(ValueError):
            self.digital_pot.set_channel_label(1, "CH A")
        with self.assertRaises(ValueError):
            self.digital_pot.set_channel_label(2, "CH A")
        with self.assertRaises(ValueError):
            self.digital_pot.set_channel_label(1.1, "CH C")
        with self.assertRaises(ValueError):
            self.digital_pot.set_channel_label(-1, "CH C")

    def test_value_set_and_get(self):
        """
        Test `set` and `read` functions, value property
        """
        self.digital_pot.set_value(0, 10)
        self.assertEqual(self.digital_pot.value[0], 10)
        self.assertEqual(self.digital_pot.get_value(0), 10)
        self.digital_pot.set_value("CH A", 20)
        self.assertEqual(self.digital_pot.value[0], 20)
        self.assertEqual(self.digital_pot.get_value("CH A"), 20)
        with self.assertRaises(ValueError):
            self.digital_pot.set_value("CH C", 20)
        with self.assertRaises(ValueError):
            self.digital_pot.set_value(2, 20)

        self.assertEqual(self.digital_pot.get_value(0), 20)
        self.assertEqual(self.digital_pot.get_value("CH A"), 20)
        with self.assertRaises(ValueError):
            self.digital_pot.get_value("CH C")
        with self.assertRaises(ValueError):
            self.digital_pot.get_value(2)

        self.digital_pot.value = (10, 20)
        self.assertEqual(self.digital_pot.value, (10, 20))
        with self.assertRaises(ValueError):
            self.digital_pot.value = 10
        with self.assertRaises(ValueError):
            self.digital_pot.value = (10, 20, 30)

    def test_rwa_rwb(self):
        """Test r_wa and r_wb control"""
        self.digital_pot.set_r_wa(0, self.pot.r_ab / 2)
        self.digital_pot.set_r_wa("CH A", self.pot.r_ab / 2)
        pos = self.digital_pot.value[0] / self.digital_pot.channels[0].max_value
        self.assertEqual(self.digital_pot.r_wa[0], self.pot.r_wa(pos))
        self.assertEqual(self.digital_pot.get_r_wa(0), self.pot.r_wa(pos))
        self.assertEqual(self.digital_pot.get_r_wa("CH A"), self.pot.r_wa(pos))
        with self.assertRaises(ValueError):
            self.digital_pot.set_r_wa(2, self.pot.r_ab / 2)
        self.digital_pot.set_r_wb(1, self.pot.r_ab / 3)
        self.digital_pot.set_r_wb("CH B", self.pot.r_ab / 3)
        pos = self.digital_pot.value[1] / self.digital_pot.channels[1].max_value
        self.assertEqual(self.digital_pot.r_wb[1], self.pot.r_wb(pos))
        self.assertEqual(self.digital_pot.get_r_wb(1), self.pot.r_wb(pos))
        self.assertEqual(self.digital_pot.get_r_wb("CH B"), self.pot.r_wb(pos))
        with self.assertRaises(ValueError):
            self.digital_pot.set_r_wb(2, self.pot.r_ab / 3)

        self.digital_pot.r_wa = (self.pot.r_ab / 2, self.pot.r_ab / 3)
        pos = self.digital_pot.value[0] / self.digital_pot.channels[0].max_value
        self.assertEqual(self.digital_pot.r_wa[0], self.pot.r_wa(pos))
        pos = self.digital_pot.value[1] / self.digital_pot.channels[1].max_value
        self.assertEqual(self.digital_pot.r_wa[1], self.pot.r_wa(pos))
        self.digital_pot.r_wb = (self.pot.r_ab / 2, self.pot.r_ab / 3)
        pos = self.digital_pot.value[0] / self.digital_pot.channels[0].max_value
        self.assertEqual(self.digital_pot.r_wb[0], self.pot.r_wb(pos))
        pos = self.digital_pot.value[1] / self.digital_pot.channels[1].max_value
        self.assertEqual(self.digital_pot.r_wb[1], self.pot.r_wb(pos))

        with self.assertRaises(ValueError):
            self.digital_pot.r_wa = (0, 0, 0)
        with self.assertRaises(TypeError):
            self.digital_pot.r_wa = 0

        with self.assertRaises(ValueError):
            self.digital_pot.r_wb = (0, 0, 0)
        with self.assertRaises(TypeError):
            self.digital_pot.r_wb = 0

        with self.assertRaises(ValueError):
            self.digital_pot.get_r_wa("CH ZZZ")
        with self.assertRaises(ValueError):
            self.digital_pot.get_r_wb("CH ZZZ")

    def test_voltage_in(self):
        """
        Test voltage_in setters and getters
        """
        self.assertEqual(self.digital_pot.voltage_in, (0, 0))
        self.digital_pot.voltage_in = (-5, 5)
        self.assertEqual(self.digital_pot.voltage_in, (-5, 5))
        self.assertEqual(self.digital_pot.get_voltage_in("CH A"), -5)
        self.assertEqual(self.digital_pot.get_voltage_in("CH B"), 5)
        with self.assertRaises(ValueError):
            self.digital_pot.get_voltage_in("CH XXX")
        with self.assertRaises(ValueError):
            self.digital_pot.voltage_in = (-5, 5, 0)
        with self.assertRaises(TypeError):
            self.digital_pot.voltage_in = 5
        self.digital_pot.set_voltage_in(0, 5)
        self.digital_pot.set_voltage_in("CH B", 15)
        self.assertEqual(self.digital_pot.voltage_in, (5, 15))
        with self.assertRaises(ValueError):
            self.digital_pot.set_voltage_in(2, 5)

    def test_voltage_out(self):
        """
        Test voltage_out setters and getters
        """
        self.assertEqual(self.digital_pot.voltage_out, (0, 0))
        self.digital_pot.voltage_in = (-5, 5)
        self.digital_pot.voltage_out = (-2.5, 2.5)
        self.assertEqual(
            self.digital_pot.voltage_out,
            (
                self.digital_pot.channels[0].voltage_out,
                self.digital_pot.channels[1].voltage_out,
            ),
        )
        self.assertEqual(
            self.digital_pot.get_voltage_out("CH A"),
            self.digital_pot.channels[0].voltage_out,
        )
        self.assertEqual(
            self.digital_pot.get_voltage_out("CH B"),
            self.digital_pot.channels[1].voltage_out,
        )
        with self.assertRaises(ValueError):
            self.digital_pot.get_voltage_out("CH XXX")
        with self.assertRaises(ValueError):
            self.digital_pot.voltage_out = (-5, 5, 0)
        with self.assertRaises(TypeError):
            self.digital_pot.voltage_out = 5
        self.digital_pot.set_voltage_out(0, -1)
        self.digital_pot.set_voltage_out("CH B", 1.5)
        self.assertEqual(
            self.digital_pot.voltage_out,
            (
                self.digital_pot.channels[0].voltage_out,
                self.digital_pot.channels[1].voltage_out,
            ),
        )
        with self.assertRaises(ValueError):
            self.digital_pot.set_voltage_out(2, 5)
        min_r_step = (self.pot.r_ab + self.pot.r_w) / self.digital_pot.channels[
            0
        ].max_value
        self.assertTrue(
            abs(self.digital_pot.channels[0].voltage_out - 1) < min_r_step * 5
        )

    def test_r_lim(self):
        self.digital_pot.r_lim = 200
        self.assertEqual(self.digital_pot.r_lim, (200, 200))
        self.digital_pot.r_lim = (100, 200)
        self.assertEqual(self.digital_pot.r_lim, (100, 200))
        self.assertEqual(self.digital_pot.get_r_lim("CH A"), 100)
        self.assertEqual(self.digital_pot.get_r_lim("CH B"), 200)
        self.digital_pot.set_r_lim("CH B", 300)
        self.assertEqual(self.digital_pot.get_r_lim("CH B"), 300)
        with self.assertRaises(ValueError):
            self.digital_pot.r_lim = (100, 200, 300)
        with self.assertRaises(ValueError):
            self.digital_pot.r_lim = ("A", 200)
        with self.assertRaises(ValueError):
            self.digital_pot.r_lim = "A"
        with self.assertRaises(ValueError):
            self.digital_pot.set_r_lim("CH XXX", 300)
        with self.assertRaises(ValueError):
            self.digital_pot.get_r_lim("CH XXX")
        with self.assertRaises(ValueError):
            self.digital_pot.set_r_lim("CH B", -300)

    def test_r_load(self):
        self.digital_pot.r_load = 1e6
        self.assertEqual(self.digital_pot.r_load, (1e6, 1e6))
        self.digital_pot.r_load = (1e6, 2e6)
        self.assertEqual(self.digital_pot.r_load, (1e6, 2e6))
        self.assertEqual(self.digital_pot.get_r_load("CH A"), 1e6)
        self.assertEqual(self.digital_pot.get_r_load("CH B"), 2e6)
        self.digital_pot.set_r_load("CH B", 3e6)
        self.assertEqual(self.digital_pot.get_r_load("CH B"), 3e6)
        with self.assertRaises(ValueError):
            self.digital_pot.r_load = (1e6, 2e6, 3e6)
        with self.assertRaises(ValueError):
            self.digital_pot.r_load = ("A", 2e6)
        with self.assertRaises(ValueError):
            self.digital_pot.r_load = "A"
        with self.assertRaises(ValueError):
            self.digital_pot.set_r_load("CH XXX", 3e6)
        with self.assertRaises(ValueError):
            self.digital_pot.get_r_load("CH XXX")
        with self.assertRaises(ValueError):
            self.digital_pot.set_r_load("CH B", -3e6)


if __name__ == "__main__":
    unittest.main()
