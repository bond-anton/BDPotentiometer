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
        for rheostat in [True, False]:
            for locked in [True, False]:
                # Normal values
                for r_ab in [1, 1e3, 10e3, np.float64(1.1e3), np.float32(1.1e3)]:
                    pot = Potentiometer(
                        r_ab=r_ab, r_w=75, rheostat=rheostat, parameters_locked=locked
                    )
                    self.assertEqual(pot.r_ab, r_ab)
                    # Test default values (zero) for r_lim, r_load, voltage_in are set.
                    self.assertEqual(pot.r_lim, 0)
                    self.assertEqual(pot.r_load, 0)
                    self.assertEqual(pot.voltage_in, 0)
                # Wrong values
                for r_ab in [-1.0, 0, 0.0, -1e3, -10e3]:
                    with self.assertRaises(ValueError):
                        _ = Potentiometer(
                            r_ab=r_ab,
                            r_w=75,
                            rheostat=rheostat,
                            parameters_locked=locked,
                        )
                # Wrong type
                for r_ab in ["1.0e3", "10", "1", [1e3], (1e3,), None]:
                    with self.assertRaises(TypeError):
                        _ = Potentiometer(
                            r_ab=r_ab,
                            r_w=75,
                            rheostat=rheostat,
                            parameters_locked=locked,
                        )

    def test_r_w(self) -> None:
        """
        Test r_w parameter.
        """
        for rheostat in [True, False]:
            for locked in [True, False]:
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
                    pot = Potentiometer(
                        r_ab=10e3, r_w=r_w, rheostat=rheostat, parameters_locked=locked
                    )
                    self.assertEqual(pot.r_w, r_w)
                    # Test default values (zero) for r_lim, r_load, voltage_in are set.
                    self.assertEqual(pot.r_lim, 0)
                    self.assertEqual(pot.r_load, 0)
                    self.assertEqual(pot.voltage_in, 0)
                # Wrong values
                for r_w in [-1.0, -1e3, -10e3]:
                    with self.assertRaises(ValueError):
                        _ = Potentiometer(
                            r_ab=10e3,
                            r_w=r_w,
                            rheostat=rheostat,
                            parameters_locked=locked,
                        )
                # Wrong type
                for r_w in ["1.0e3", "10", "1", [1e3], (1e3,), None]:
                    with self.assertRaises(TypeError):
                        pot = Potentiometer(
                            r_ab=10e3,
                            r_w=r_w,
                            rheostat=rheostat,
                            parameters_locked=locked,
                        )

    def test_rheostat(self) -> None:
        """
        Test rheostat parameter.
        """
        # Normal values and strange ones. All will be converted to bool
        for rheostat in [True, False, 1, 0, "1.0e3", "10", "1", [1e3], (1e3,), None]:
            pot = Potentiometer(
                r_ab=10e3, r_w=75, rheostat=rheostat, parameters_locked=False
            )
            self.assertEqual(pot.rheostat, bool(rheostat))
            # Test default values (zero) for r_lim, r_load, voltage_in are set.
            self.assertEqual(pot.r_lim, 0)
            self.assertEqual(pot.r_load, 0)
            self.assertEqual(pot.voltage_in, 0)

    def test_locked(self) -> None:
        """
        Test locked parameter.
        """
        # Normal values and strange ones. All will be converted to bool
        for rheostat in [True, False]:
            for locked in [True, False, 1, 0, "1.0e3", "10", "1", [1e3], (1e3,), None]:
                pot = Potentiometer(
                    r_ab=10e3, r_w=75, rheostat=rheostat, parameters_locked=locked
                )
                self.assertEqual(pot.parameters_locked, bool(locked))
                # Test default values (zero) for r_lim, r_load, voltage_in are set.
                self.assertEqual(pot.r_lim, 0)
                self.assertEqual(pot.r_load, 0)
                self.assertEqual(pot.voltage_in, 0)


if __name__ == "__main__":
    unittest.main()
