""" Test Potentiometer resistors properties setters and getters. """

import unittest
import numpy as np

try:
    from src.BDPotentiometer import Potentiometer
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer


class TestPotentiometerFixedResistors(unittest.TestCase):
    """
    Testing Potentiometer properties r_ab, r_w, r_lim, r_load.
    """

    def setUp(self) -> None:
        self.pot = None

    def test_r_ab(self) -> None:
        """
        Test r_ab property.
        For unlocked potentiometer and rheostat result is the same.
        """
        for rheostat in [True, False]:
            self.pot = Potentiometer(r_ab=10e3, r_w=75, rheostat=rheostat, locked=False)
            self.assertEqual(self.pot.r_ab, 10e3)
            # Normal values
            for r_ab in [1, 1e3, 10e3, np.float64(1.1e3), np.float32(1.1e3)]:
                self.pot.r_ab = r_ab
                self.assertEqual(self.pot.r_ab, r_ab)
                self.assertIsInstance(self.pot.r_ab, float)
            # Wrong values
            for r_ab in [-1.0, 0, 0.0, -1e3, -10e3]:
                with self.assertRaises(ValueError):
                    self.pot.r_ab = r_ab
            # Wrong type
            for r_ab in ["1.0e3", "10", "1", [1e3], (1e3,), None]:
                with self.assertRaises(TypeError):
                    self.pot.r_ab = r_ab

    def test_r_w(self) -> None:
        """
        Test r_w property.
        For unlocked potentiometer and rheostat result is the same.
        """
        for rheostat in [True, False]:
            self.pot = Potentiometer(r_ab=10e3, r_w=75, rheostat=rheostat, locked=False)
            self.assertEqual(self.pot.r_w, 75)
            # Normal values
            for r_w in [0, 0.0, 1, 1e3, 10e3, np.float64(1.1e3), np.float32(1.1e3)]:
                self.pot.r_w = r_w
                self.assertEqual(self.pot.r_w, r_w)
                self.assertIsInstance(self.pot.r_w, float)
            # Wrong values
            for r_w in [-1.0, -1e3, -10e3]:
                with self.assertRaises(ValueError):
                    self.pot.r_w = r_w
            # Wrong type
            for r_w in ["1.0e3", "10", "1", [1e3], (1e3,), None]:
                with self.assertRaises(TypeError):
                    self.pot.r_w = r_w

    def test_r_lim(self) -> None:
        """
        Test r_lim property.
        For unlocked potentiometer and rheostat result is the same.
        """
        for rheostat in [True, False]:
            self.pot = Potentiometer(r_ab=10e3, r_w=75, rheostat=rheostat, locked=False)
            self.assertEqual(self.pot.r_lim, 0)
            # Normal values
            for r_lim in [0, 0.0, 1, 1e3, 10e3, np.float64(1.1e3), np.float32(1.1e3)]:
                self.pot.r_lim = r_lim
                self.assertEqual(self.pot.r_lim, r_lim)
                self.assertIsInstance(self.pot.r_lim, float)
            # Wrong values
            for r_lim in [-1.0, -1e3, -10e3]:
                with self.assertRaises(ValueError):
                    self.pot.r_lim = r_lim
            # Wrong type
            for r_lim in ["1.0e3", "10", "1", [1e3], (1e3,), None]:
                with self.assertRaises(TypeError):
                    self.pot.r_lim = r_lim

    def test_r_load(self) -> None:
        """
        Test r_load property.
        For unlocked potentiometer and rheostat result is the same.
        """
        for rheostat in [True, False]:
            self.pot = Potentiometer(r_ab=10e3, r_w=75, rheostat=rheostat, locked=False)
            self.assertEqual(self.pot.r_load, 0)
            # Normal values
            for r_load in [0, 0.0, 1, 1e3, 10e3, np.float64(1.1e3), np.float32(1.1e3)]:
                self.pot.r_load = r_load
                self.assertEqual(self.pot.r_load, r_load)
                self.assertIsInstance(self.pot.r_load, float)
            # Wrong values
            for r_load in [-1.0, -1e3, -10e3]:
                with self.assertRaises(ValueError):
                    self.pot.r_load = r_load
            # Wrong type
            for r_load in ["1.0e3", "10", "1", [1e3], (1e3,), None]:
                with self.assertRaises(TypeError):
                    self.pot.r_load = r_load


if __name__ == "__main__":
    unittest.main()
