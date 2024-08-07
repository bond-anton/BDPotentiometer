""" Tests for DigitalPotentiometerDevice class. """

# pylint: disable=protected-access

import unittest
import numpy as np

try:
    from src.BDPotentiometer import (
        Potentiometer,
        DigitalWiper,
        DigitalPotentiometerDevice,
    )
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, DigitalWiper, DigitalPotentiometerDevice


class TestDigitalPotentiometer(unittest.TestCase):
    """
    Testing DigitalPotentiometerDevice.
    """

    def setUp(self) -> None:
        self.pot = Potentiometer(r_ab=10e3, r_w=75)
        digital_wiper = DigitalWiper(potentiometer=self.pot, max_value=128)
        self.digital_pot = DigitalPotentiometerDevice(wiper=digital_wiper, channels=2)
        self.digital_pot.set_channel_label(0, "CH A")
        self.digital_pot.set_channel_label(1, "CH B")

    def test_basic_properties(self):
        """
        Testing basic parameters.
        """
        pot = Potentiometer(r_ab=10e3, r_w=75)
        digital_wiper = DigitalWiper(potentiometer=pot, max_value=128)
        digital_pot = DigitalPotentiometerDevice(wiper=digital_wiper, channels=3)
        self.assertEqual(digital_pot.channels_num, 3)
        channels = digital_pot.channels
        for channel_number, wiper in channels.items():
            self.assertEqual(wiper.potentiometer.r_ab, pot.r_ab)
            self.assertEqual(wiper.potentiometer.r_w, pot.r_w)
            self.assertEqual(wiper.potentiometer.r_a, pot.r_a)
            self.assertEqual(wiper.potentiometer.r_b, pot.r_b)
            self.assertEqual(wiper.potentiometer.r_load, pot.r_load)
            self.assertEqual(wiper.max_value, digital_wiper.max_value)
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
        self.assertEqual(0, self.digital_pot._get_channel_number_by_label_or_id("CH A"))
        self.assertEqual(1, self.digital_pot._get_channel_number_by_label_or_id("CH B"))
        self.assertEqual(0, self.digital_pot._get_channel_number_by_label_or_id(0))
        self.assertEqual(1, self.digital_pot._get_channel_number_by_label_or_id(1))
        self.assertIsNone(self.digital_pot._get_channel_number_by_label_or_id("CH C"))
        self.assertIsNone(self.digital_pot._get_channel_number_by_label_or_id(3))
        with self.assertRaises(ValueError):
            self.digital_pot._get_channel_number_by_label_or_id(1.1)
        with self.assertRaises(ValueError):
            self.digital_pot._get_channel_number_by_label_or_id(-1)
        self.digital_pot.set_channel_label(0, None)
        self.assertEqual(0, self.digital_pot._get_channel_number_by_label_or_id("0"))
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
        with self.assertRaises(TypeError):
            self.digital_pot.value = 10
        with self.assertRaises(ValueError):
            self.digital_pot.value = (10, 20, 30)
        values = np.arange(129)
        for value in values:
            self.digital_pot.set_value(0, value)
            self.digital_pot.set_value(1, value)
            self.assertEqual(self.digital_pot.value, (value, value))

    def test_rwa_rwb(self):
        """Test r_wa and r_wb control"""
        self.pot.r_wa = self.pot.r_ab / 2
        self.digital_pot.set_r_wa(0, self.pot.r_ab / 2)
        self.digital_pot.set_r_wa("CH A", self.pot.r_ab / 2)
        self.assertEqual(self.digital_pot.r_wa[0], self.pot.r_wa)
        self.assertEqual(self.digital_pot.get_r_wa(0), self.pot.r_wa)
        self.assertEqual(self.digital_pot.get_r_wa("CH A"), self.pot.r_wa)
        with self.assertRaises(ValueError):
            self.digital_pot.set_r_wa(2, self.pot.r_ab / 2)
        self.pot.r_wb = self.pot.r_ab / 3
        self.digital_pot.set_r_wb(1, self.pot.r_ab / 3)
        self.digital_pot.set_r_wb("CH B", self.pot.r_ab / 3)
        self.assertEqual(self.digital_pot.r_wb[1], self.pot.r_wb)
        self.assertEqual(self.digital_pot.get_r_wb(1), self.pot.r_wb)
        self.assertEqual(self.digital_pot.get_r_wb("CH B"), self.pot.r_wb)
        with self.assertRaises(ValueError):
            self.digital_pot.set_r_wb(2, self.pot.r_ab / 3)
        self.pot.r_wa = self.pot.r_ab / 2
        self.digital_pot.r_wa = (self.pot.r_ab / 2, self.pot.r_ab / 3)
        self.assertEqual(self.digital_pot.r_wa[0], self.pot.r_wa)
        self.pot.r_wa = self.pot.r_ab / 3
        self.assertEqual(self.digital_pot.r_wa[1], self.pot.r_wa)
        self.digital_pot.r_wb = (self.pot.r_ab / 2, self.pot.r_ab / 3)
        self.pot.r_wb = self.pot.r_ab / 2
        self.assertEqual(self.digital_pot.r_wb[0], self.pot.r_wb)
        self.pot.r_wb = self.pot.r_ab / 3
        self.assertEqual(self.digital_pot.r_wb[1], self.pot.r_wb)

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
        self.assertEqual(self.digital_pot.v_a, (0, 0))
        self.assertEqual(self.digital_pot.v_b, (0, 0))
        self.assertEqual(self.digital_pot.v_load, (0, 0))
        self.digital_pot.v_a = (-5, 5)
        self.assertEqual(self.digital_pot.v_a, (-5, 5))
        self.assertEqual(self.digital_pot.get_v_a("CH A"), -5)
        self.assertEqual(self.digital_pot.get_v_a("CH B"), 5)
        self.digital_pot.v_b = (-5, 5)
        self.assertEqual(self.digital_pot.v_b, (-5, 5))
        self.assertEqual(self.digital_pot.get_v_b("CH A"), -5)
        self.assertEqual(self.digital_pot.get_v_b("CH B"), 5)
        self.digital_pot.v_load = (-5, 5)
        self.assertEqual(self.digital_pot.v_load, (-5, 5))
        self.assertEqual(self.digital_pot.get_v_load("CH A"), -5)
        self.assertEqual(self.digital_pot.get_v_load("CH B"), 5)
        with self.assertRaises(ValueError):
            self.digital_pot.get_v_a("CH XXX")
        with self.assertRaises(ValueError):
            self.digital_pot.get_v_b("CH XXX")
        with self.assertRaises(ValueError):
            self.digital_pot.get_v_load("CH XXX")
        with self.assertRaises(ValueError):
            self.digital_pot.v_a = (-5, 5, 0)
        with self.assertRaises(ValueError):
            self.digital_pot.v_b = (-5, 5, 0)
        with self.assertRaises(ValueError):
            self.digital_pot.v_load = (-5, 5, 0)
        with self.assertRaises(TypeError):
            self.digital_pot.v_a = 5
        with self.assertRaises(TypeError):
            self.digital_pot.v_b = 5
        with self.assertRaises(TypeError):
            self.digital_pot.v_load = 5
        self.digital_pot.set_v_a(0, 5)
        self.digital_pot.set_v_a("CH B", 15)
        self.assertEqual(self.digital_pot.v_a, (5, 15))
        with self.assertRaises(ValueError):
            self.digital_pot.set_v_a(2, 5)
        with self.assertRaises(ValueError):
            self.digital_pot.set_v_b(2, 5)
        with self.assertRaises(ValueError):
            self.digital_pot.set_v_load(2, 5)

    def test_voltage_out(self):
        """
        Test voltage_out setters and getters
        """
        self.digital_pot.v_a = (0, 0)
        self.digital_pot.v_b = (0, 0)
        self.digital_pot.v_load = (0, 0)
        self.assertEqual(self.digital_pot.v_w, (0, 0))
        self.digital_pot.v_a = (-5, 5)
        self.digital_pot.v_w = (-2.5, 2.5)
        self.assertEqual(
            self.digital_pot.v_w,
            (
                self.digital_pot.channels[0].v_w,
                self.digital_pot.channels[1].v_w,
            ),
        )
        self.assertEqual(
            self.digital_pot.get_v_w("CH A"),
            self.digital_pot.channels[0].v_w,
        )
        self.assertEqual(
            self.digital_pot.get_v_w("CH B"),
            self.digital_pot.channels[1].v_w,
        )
        with self.assertRaises(ValueError):
            self.digital_pot.get_v_w("CH XXX")
        with self.assertRaises(ValueError):
            self.digital_pot.v_w = (-5, 5, 0)
        with self.assertRaises(TypeError):
            self.digital_pot.v_w = 5
        self.digital_pot.set_v_w(0, -1)
        self.digital_pot.set_v_w("CH B", 1.5)
        self.assertEqual(
            self.digital_pot.v_w,
            (
                self.digital_pot.channels[0].v_w,
                self.digital_pot.channels[1].v_w,
            ),
        )
        with self.assertRaises(ValueError):
            self.digital_pot.set_v_w(2, 5)
        min_r_step = (self.pot.r_ab + self.pot.r_w) / self.digital_pot.channels[
            0
        ].max_value
        self.assertTrue(abs(self.digital_pot.channels[0].v_w - 1) < min_r_step * 5)

    def test_r_lim(self):
        """
        Test r_lim property and corresponding get_ and set_ methods.
        """
        self.digital_pot.r_a = (200, 200)
        self.assertEqual(self.digital_pot.r_a, (200, 200))
        self.digital_pot.r_b = (100, 200)
        self.assertEqual(self.digital_pot.r_b, (100, 200))
        self.assertEqual(self.digital_pot.get_r_a("CH A"), 200)
        self.assertEqual(self.digital_pot.get_r_b("CH B"), 200)
        self.digital_pot.set_r_a("CH B", 300)
        self.assertEqual(self.digital_pot.get_r_a("CH B"), 300)
        with self.assertRaises(ValueError):
            self.digital_pot.r_a = (100, 200, 300)
        with self.assertRaises(ValueError):
            self.digital_pot.r_b = (100, 200, 300)
        with self.assertRaises(TypeError):
            self.digital_pot.r_a = ("A", 200)
        with self.assertRaises(TypeError):
            self.digital_pot.r_b = ("A", 200)
        with self.assertRaises(TypeError):
            self.digital_pot.r_a = "A"
        with self.assertRaises(TypeError):
            self.digital_pot.r_b = "A"
        with self.assertRaises(ValueError):
            self.digital_pot.set_r_a("CH XXX", 300)
        with self.assertRaises(ValueError):
            self.digital_pot.set_r_b("CH XXX", 300)
        with self.assertRaises(ValueError):
            self.digital_pot.get_r_a("CH XXX")
        with self.assertRaises(ValueError):
            self.digital_pot.get_r_b("CH XXX")
        with self.assertRaises(ValueError):
            self.digital_pot.set_r_a("CH B", -300)
        with self.assertRaises(ValueError):
            self.digital_pot.set_r_b("CH B", -300)

    def test_r_load(self):
        """
        Testing r_load property and corresponding get_ and set_ methods.
        """
        self.digital_pot.r_load = (1e6, 1e6)
        self.assertEqual(self.digital_pot.r_load, (1e6, 1e6))
        self.digital_pot.r_load = (1e6, 2e6)
        self.assertEqual(self.digital_pot.r_load, (1e6, 2e6))
        self.assertEqual(self.digital_pot.get_r_load("CH A"), 1e6)
        self.assertEqual(self.digital_pot.get_r_load("CH B"), 2e6)
        self.digital_pot.set_r_load("CH B", 3e6)
        self.assertEqual(self.digital_pot.get_r_load("CH B"), 3e6)
        with self.assertRaises(ValueError):
            self.digital_pot.r_load = (1e6, 2e6, 3e6)
        with self.assertRaises(TypeError):
            self.digital_pot.r_load = ("A", 2e6)
        with self.assertRaises(TypeError):
            self.digital_pot.r_load = "A"
        with self.assertRaises(ValueError):
            self.digital_pot.set_r_load("CH XXX", 3e6)
        with self.assertRaises(ValueError):
            self.digital_pot.get_r_load("CH XXX")
        with self.assertRaises(ValueError):
            self.digital_pot.set_r_load("CH B", -3e6)


if __name__ == "__main__":
    unittest.main()
