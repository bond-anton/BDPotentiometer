""" Tests for Potentiometer constructor. """

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


if __name__ == "__main__":
    unittest.main()
