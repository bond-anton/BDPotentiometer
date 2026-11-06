"""Tests for Potentiometer constructor."""

import unittest

import numpy as np

try:
    from src.BDPotentiometer import Potentiometer
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer


class TestPotentiometerConstructor(unittest.TestCase):
    """
    Testing Potentiometer constructor.
    """

    def test_r_ab(self) -> None:
        """
        Test r_ab parameter.
        """
        # Normal values
        for r_ab in [1, 1e3, 10e3, np.float64(1.1e3), np.float32(1.1e3)]:
            pot = Potentiometer(r_ab=r_ab)
            self.assertEqual(pot.r_ab, r_ab)
            # Test default values (zero) for r_lim, r_load, voltage_in are set.
            self.assertEqual(pot.r_w, 0)
            self.assertEqual(pot.r_a, 0)
            self.assertEqual(pot.r_b, 0)
            self.assertEqual(pot.r_load, 1.0e10)
            self.assertEqual(pot.v_a, 0)
            self.assertEqual(pot.v_b, 0)
            self.assertEqual(pot.v_load, 0)
        # Wrong values
        for r_ab in [-1.0, 0, 0.0, -1e3, -10e3]:
            with self.assertRaises(ValueError):
                _ = Potentiometer(r_ab=r_ab)
        # Wrong type
        for r_ab in ["1.0e3", "10", "1", [1e3], (1e3,), None]:
            with self.assertRaises(TypeError):
                _ = Potentiometer(r_ab=r_ab)

    def test_r_w(self) -> None:
        """
        Test r_w parameter.
        """
        # Normal values
        for r_w in [
            0,
            0.0,
            1,
            100.134,
            1e3,
            10e3,
            np.float64(1.1e3),
            np.float32(1.1e3),
        ]:
            pot = Potentiometer(r_ab=10e3, r_w=r_w)
            self.assertEqual(pot.r_w, r_w)
            # Test default values (zero) for r_lim, r_load, voltage_in are set.
            self.assertEqual(pot.r_a, 0)
            self.assertEqual(pot.r_b, 0)
            self.assertEqual(pot.r_load, 1.0e10)
            self.assertEqual(pot.v_a, 0)
            self.assertEqual(pot.v_b, 0)
            self.assertEqual(pot.v_load, 0)
        # Wrong values
        for r_w in [-1.0, -1e3, -10e3]:
            with self.assertRaises(ValueError):
                _ = Potentiometer(r_ab=10e3, r_w=r_w)
        # Wrong type
        for r_w in ["1.0e3", "10", "1", [1e3], (1e3,), None]:
            with self.assertRaises(TypeError):
                pot = Potentiometer(r_ab=10e3, r_w=r_w)

    def test_numeric_arguments_are_floats(self) -> None:
        """
        Integer constructor inputs produce the same types as float inputs.
        """
        int_pot = Potentiometer(
            r_ab=10000,
            wiper_position=1,
            r_w=75,
            r_a=1,
            r_b=2,
            v_a=0,
            v_b=1,
            v_load=2,
            r_load=1000,
        )
        float_pot = Potentiometer(
            r_ab=10e3,
            wiper_position=1.0,
            r_w=75.0,
            r_a=1.0,
            r_b=2.0,
            v_a=0.0,
            v_b=1.0,
            v_load=2.0,
            r_load=1000.0,
        )
        for attribute in (
            "r_ab",
            "r_w",
            "r_a",
            "r_b",
            "v_a",
            "v_b",
            "v_load",
            "r_load",
            "wiper_position",
        ):
            int_value = getattr(int_pot, attribute)
            float_value = getattr(float_pot, attribute)
            self.assertIsInstance(int_value, float)
            self.assertIsInstance(float_value, float)
            self.assertEqual(int_value, float_value)


if __name__ == "__main__":
    unittest.main()
