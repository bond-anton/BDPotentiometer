"""Tests for DigitalPotentiometerDevice class."""

import unittest

import numpy as np

try:
    from src.BDPotentiometer import (
        DigitalPotentiometerDevice,
        DigitalWiper,
        Potentiometer,
    )
except ModuleNotFoundError:
    from BDPotentiometer import DigitalPotentiometerDevice, DigitalWiper, Potentiometer


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
        self.assertIsNone(self.digital_pot._get_channel_number_by_label_or_id(1.1))
        self.assertIsNone(self.digital_pot._get_channel_number_by_label_or_id(-1))
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

    def test_channel_label_rejects_non_str(self):
        """
        Non-string labels are rejected instead of silently coerced.
        """
        pot = Potentiometer(r_ab=10e3, r_w=75)
        wiper = DigitalWiper(potentiometer=pot, max_value=128)
        digital_pot = DigitalPotentiometerDevice(wiper=wiper, channels=2)
        for label in [5, 5.0, True, b"CH A", ["CH A"]]:
            with self.subTest(label=label), self.assertRaises(TypeError):
                digital_pot.set_channel_label(0, label)
        self.assertEqual(digital_pot._get_channel_number_by_label_or_id(0), 0)

    def test_channel_label_rejects_overlong_label(self):
        """
        A label longer than the limit is rejected before it is stored.
        """
        pot = Potentiometer(r_ab=10e3, r_w=75)
        wiper = DigitalWiper(potentiometer=pot, max_value=128)
        digital_pot = DigitalPotentiometerDevice(wiper=wiper, channels=2)
        digital_pot.set_channel_label(0, "x" * 64)
        self.assertEqual(digital_pot._get_channel_number_by_label_or_id("x" * 64), 0)
        with self.assertRaises(ValueError):
            digital_pot.set_channel_label(1, "x" * 65)
        self.assertEqual(digital_pot._get_channel_number_by_label_or_id("1"), 1)

    def test_channel_label_cannot_shadow_numeric_label(self):
        """
        A string label that equals another channel's default number is rejected.
        """
        pot = Potentiometer(r_ab=10e3, r_w=75)
        wiper = DigitalWiper(potentiometer=pot, max_value=128)
        digital_pot = DigitalPotentiometerDevice(wiper=wiper, channels=6)
        with self.assertRaises(ValueError):
            digital_pot.set_channel_label(0, "5")
        self.assertEqual(digital_pot._get_channel_number_by_label_or_id("0"), 0)
        self.assertEqual(digital_pot._get_channel_number_by_label_or_id("5"), 5)

    def test_channel_lookup_string_id_fallback(self):
        """
        A numeric string resolves as an id when no custom label matches it.
        """
        pot = Potentiometer(r_ab=10e3, r_w=75)
        wiper = DigitalWiper(potentiometer=pot, max_value=128)
        digital_pot = DigitalPotentiometerDevice(wiper=wiper, channels=3)
        digital_pot.set_channel_label(0, "CH A")
        digital_pot.set_channel_label(1, "CH B")
        digital_pot.set_channel_label(2, "CH C")
        # Custom labels hide the default numeric labels, but the ids still work.
        self.assertEqual(digital_pot._get_channel_number_by_label_or_id("0"), 0)
        self.assertEqual(digital_pot._get_channel_number_by_label_or_id(" 2 "), 2)
        self.assertEqual(digital_pot.get_value("2"), digital_pot.get_value(2))
        self.assertIsNone(digital_pot._get_channel_number_by_label_or_id("3"))
        self.assertIsNone(digital_pot._get_channel_number_by_label_or_id("-1"))
        self.assertIsNone(digital_pot._get_channel_number_by_label_or_id("1.0"))

    def test_channel_lookup_label_wins_over_id(self):
        """
        A string label takes precedence over the same id in the fallback.
        """
        pot = Potentiometer(r_ab=10e3, r_w=75)
        wiper = DigitalWiper(potentiometer=pot, max_value=128)
        digital_pot = DigitalPotentiometerDevice(wiper=wiper, channels=3)
        digital_pot.set_channel_label(0, "CH A")
        digital_pot.set_channel_label(2, "0")
        self.assertEqual(digital_pot._get_channel_number_by_label_or_id("0"), 2)
        self.assertEqual(digital_pot._get_channel_number_by_label_or_id(0), 0)

    def test_channel_label_reset_blocked_when_number_taken(self):
        """
        `label=None` raises when another channel holds the restored number.
        """
        pot = Potentiometer(r_ab=10e3, r_w=75)
        wiper = DigitalWiper(potentiometer=pot, max_value=128)
        digital_pot = DigitalPotentiometerDevice(wiper=wiper, channels=2)
        digital_pot.set_channel_label(0, "CH A")
        digital_pot.set_channel_label(1, "0")
        with self.assertRaises(ValueError):
            digital_pot.set_channel_label(0, None)
        self.assertEqual(digital_pot._get_channel_number_by_label_or_id("CH A"), 0)
        self.assertEqual(digital_pot._get_channel_number_by_label_or_id("0"), 1)

    def test_channels_property_returns_copy(self):
        """
        Callers cannot add or remove channels through the property.
        """
        channels = self.digital_pot.channels
        self.assertIsNot(channels, self.digital_pot.channels)
        channels[99] = channels[0]
        self.assertNotIn(99, self.digital_pot.channels)
        self.assertIs(channels[0], self.digital_pot.channels[0])

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
        # One wiper code step expressed in volts, so the tolerance below is
        # derived from the divider span rather than from a resistance.
        v_step = abs(self.digital_pot.v_a[0] - self.digital_pot.v_b[0]) / (
            self.digital_pot.channels[0].max_value
        )
        np.testing.assert_allclose(self.digital_pot.v_w, (-2.5, 2.5), atol=v_step)
        np.testing.assert_allclose(
            (self.digital_pot.get_v_w("CH A"), self.digital_pot.get_v_w("CH B")),
            (-2.5, 2.5),
            atol=v_step,
        )
        with self.assertRaises(ValueError):
            self.digital_pot.get_v_w("CH XXX")
        with self.assertRaises(ValueError):
            self.digital_pot.v_w = (-5, 5, 0)
        with self.assertRaises(TypeError):
            self.digital_pot.v_w = 5
        self.digital_pot.set_v_w(0, -1)
        self.digital_pot.set_v_w("CH B", 1.5)
        v_step = abs(self.digital_pot.v_a[0] - self.digital_pot.v_b[0]) / (
            self.digital_pot.channels[0].max_value
        )
        np.testing.assert_allclose(
            (self.digital_pot.get_v_w("CH A"), self.digital_pot.get_v_w("CH B")),
            (-1, 1.5),
            atol=v_step,
        )
        with self.assertRaises(ValueError):
            self.digital_pot.set_v_w(2, 5)

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

    def test_channel_lookup_invalid_input_returns_none(self):
        """
        Invalid channel identifiers are reported as "not found", not raised.
        """
        for channel in (-1, 1.5, True, "nope"):
            with self.subTest(channel=channel):
                self.assertIsNone(
                    self.digital_pot._get_channel_number_by_label_or_id(channel)
                )
        self.assertEqual(self.digital_pot._get_channel_number_by_label_or_id(0), 0)
        self.assertEqual(self.digital_pot._get_channel_number_by_label_or_id("CH A"), 0)

    def test_channel_label_strips_whitespace(self):
        """
        Labels are stripped, so whitespace variants cannot bypass uniqueness.
        """
        self.digital_pot.set_channel_label(0, "  CH A  ")
        self.assertEqual(self.digital_pot._get_channel_number_by_label_or_id("CH A"), 0)
        # Lookups strip too, so every whitespace variant reaches the channel.
        self.assertEqual(
            self.digital_pot._get_channel_number_by_label_or_id("  CH A  "), 0
        )
        self.assertEqual(
            self.digital_pot.get_value(" CH A "), self.digital_pot.get_value(0)
        )
        with self.assertRaises(ValueError):
            self.digital_pot.set_channel_label(1, " CH A ")
        with self.assertRaises(ValueError) as ctx:
            self.digital_pot.set_channel_label(1, "   ")
        self.assertIn("non-empty", str(ctx.exception))
        with self.assertRaises(ValueError):
            self.digital_pot.set_channel_label(1, "")
        self.assertEqual(self.digital_pot._get_channel_number_by_label_or_id("CH B"), 1)

    def test_sequence_setter_rejects_later_element_without_writing(self):
        """
        A bad element aborts the whole tuple setter before any channel is written.
        """
        self.digital_pot.value = (10, 20)
        with self.assertRaises(TypeError):
            self.digital_pot.value = (11, "bad")
        self.assertEqual(self.digital_pot.value, (10, 20))

        self.digital_pot.r_a = (100, 200)
        with self.assertRaises(ValueError):
            self.digital_pot.r_a = (300, -100)
        self.assertEqual(self.digital_pot.r_a, (100, 200))

        self.digital_pot.v_a = (-5, 5)
        with self.assertRaises(TypeError):
            self.digital_pot.v_a = (1, "bad")
        self.assertEqual(self.digital_pot.v_a, (-5, 5))

        self.digital_pot.v_b = (-5, 5)
        with self.assertRaises(ValueError):
            self.digital_pot.v_b = (0, float("nan"))
        self.assertEqual(self.digital_pot.v_b, (-5, 5))

    def test_invert_requires_bool(self):
        """
        Non-boolean invert values are rejected instead of being coerced.
        """
        self.assertEqual(self.digital_pot.invert, (False, False))
        with self.assertRaises(TypeError):
            self.digital_pot.set_invert(0, "false")
        self.assertEqual(self.digital_pot.invert, (False, False))
        with self.assertRaises(TypeError):
            self.digital_pot.invert = (True, 1)
        self.assertEqual(self.digital_pot.invert, (False, False))
        self.digital_pot.invert = (True, False)
        self.assertEqual(self.digital_pot.invert, (True, False))


if __name__ == "__main__":
    unittest.main()
