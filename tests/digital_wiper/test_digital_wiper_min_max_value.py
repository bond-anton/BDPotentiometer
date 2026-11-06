"""Tests for DigitalWiper min max value properties."""

import unittest

try:
    from src.BDPotentiometer import DigitalWiper, Potentiometer
except ModuleNotFoundError:
    from BDPotentiometer import DigitalWiper, Potentiometer


class _WriteFailPotentiometer(Potentiometer):
    """Potentiometer model whose wiper writes can be made to raise."""

    def __init__(self, **kwargs):
        self.fail_writes = False
        super().__init__(**kwargs)

    @property
    def wiper_position(self):
        return super().wiper_position

    @wiper_position.setter
    def wiper_position(self, position):
        if self.fail_writes:
            raise OSError("simulated bus failure")
        Potentiometer.wiper_position.fset(self, position)


class _NarrowCodeWiper(DigitalWiper):
    """Wiper whose code range is one less than its full-scale divisor."""

    @property
    def max_code(self) -> int:
        return self.max_value - 1


class TestDigitalWiperMinMaxValue(unittest.TestCase):
    """
    Testing DigitalWiper `min_value` and `max_value` properties.
    """

    def test_min_value(self):
        """
        Testing `min_value` property.
        Should always be zero and can not be changed&
        """
        pot = Potentiometer(r_ab=50e3, r_w=200)
        for max_value in [1, 32, 64, 256]:
            digital_wiper = DigitalWiper(potentiometer=pot, max_value=max_value)
            self.assertEqual(digital_wiper.min_value, 0)
            for min_value_ in [None, -1, 1, "1", "0", 0]:
                with self.assertRaises(AttributeError):
                    digital_wiper.min_value = min_value_

    def test_max_value(self):
        """
        Testing `max_value` property.
        In contrast with `min_value`, `max_value` can be altered unless wiper is locked.
        `max_value` must be positive int number.
        """
        pot = Potentiometer(r_ab=100e3, r_w=175)
        for max_value in [1, 16, 32, 2048]:
            digital_wiper = DigitalWiper(potentiometer=pot, max_value=max_value)
            self.assertEqual(digital_wiper.max_value, max_value)
            # Correct values
            for max_value_new in [1, 10, 128, 1024, 128.0]:
                digital_wiper.max_value = max_value_new
                # Check that parameters_locked locks the max_value
                self.assertEqual(digital_wiper.max_value, max_value_new)
                self.assertIsInstance(digital_wiper.max_value, int)
            # Wrong value
            for max_value_ in [0, -1, -10, 128.5]:
                with self.assertRaises(ValueError):
                    digital_wiper.max_value = max_value_
            # Wrong type
            for max_value_ in [None, "1"]:
                with self.assertRaises(TypeError):
                    digital_wiper.max_value = max_value_
            # Check that value did not change
            self.assertEqual(digital_wiper.max_value, max_value_new)


class TestDigitalWiperMaxValueRollback(unittest.TestCase):
    """Changing `max_value` restores the old state when the write fails."""

    def test_inverted_rollback_on_failed_write(self):
        """A failed re-application restores the divisor and the raw code."""
        pot = _WriteFailPotentiometer(r_ab=100e3, r_w=175)
        wiper = DigitalWiper(potentiometer=pot, max_value=128, invert=True)
        wiper.value = 100
        self.assertEqual(pot.wiper_position, 28 / 128)
        pot.fail_writes = True
        with self.assertRaises(OSError):
            wiper.max_value = 256
        self.assertEqual(wiper.max_value, 128)
        self.assertEqual(wiper.max_code, 128)
        self.assertEqual(wiper.value, 100)
        self.assertEqual(pot.wiper_position, 28 / 128)

    def test_rollback_can_be_retried(self):
        """Once the write path recovers, the same change succeeds."""
        pot = _WriteFailPotentiometer(r_ab=100e3, r_w=175)
        wiper = DigitalWiper(potentiometer=pot, max_value=128, invert=True)
        wiper.value = 100
        pot.fail_writes = True
        with self.assertRaises(OSError):
            wiper.max_value = 256
        pot.fail_writes = False
        wiper.max_value = 256
        self.assertEqual(wiper.max_value, 256)
        self.assertEqual(wiper.value, 100)
        self.assertEqual(pot.wiper_position, 156 / 256)

    def test_non_inverted_rollback_on_failed_write(self):
        """The direct (non-inverted) mapping is restored as well."""
        pot = _WriteFailPotentiometer(r_ab=100e3, r_w=175)
        wiper = DigitalWiper(potentiometer=pot, max_value=128)
        wiper.value = 100
        pot.fail_writes = True
        with self.assertRaises(OSError):
            wiper.max_value = 256
        self.assertEqual(wiper.max_value, 128)
        self.assertEqual(wiper.value, 100)
        self.assertEqual(pot.wiper_position, 100 / 128)


class TestDigitalWiperReadValueClamp(unittest.TestCase):
    """The read path never reports a code above `max_code`."""

    def test_full_scale_position_is_clamped(self):
        """A wiper position of 1.0 clamps to the highest accepted code."""
        pot = Potentiometer(r_ab=100e3, r_w=175)
        wiper = _NarrowCodeWiper(potentiometer=pot, max_value=256)
        self.assertEqual(wiper.max_code, 255)
        pot.wiper_position = 1.0
        self.assertEqual(wiper._read_value(), 255)
        self.assertEqual(wiper.value, 255)
        self.assertEqual(pot.wiper_position, 1.0)

    def test_mid_scale_position_is_unchanged(self):
        """Clamping does not alter an in-range code."""
        pot = Potentiometer(r_ab=100e3, r_w=175)
        wiper = _NarrowCodeWiper(potentiometer=pot, max_value=256)
        pot.wiper_position = 0.5
        self.assertEqual(wiper._read_value(), 128)


if __name__ == "__main__":
    unittest.main()
