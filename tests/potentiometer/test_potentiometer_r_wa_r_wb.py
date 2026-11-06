"""Tests for Potentiometer `r_wa` and `r_wb` calculation."""

import unittest

import numpy as np

try:
    from src.BDPotentiometer import Potentiometer
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer


class TestPotentiometerRwaRwb(unittest.TestCase):
    """
    Testing Potentiometer `r_wa` and `r_wb` calculation.
    """

    def test_rwa_rwb(self):
        """Testing correctness of r_wa and r_wb calculation."""
        pot = Potentiometer(r_ab=10e3, r_w=75)
        for pos in np.linspace(0, 1.0, num=101, endpoint=True):
            pot.wiper_position = pos
            np.testing.assert_allclose(pot.r_wa, pot.r_w + (1 - pos) * pot.r_ab)
            np.testing.assert_allclose(pot.r_wb, pot.r_w + pos * pot.r_ab)
            np.testing.assert_allclose(pot.r_wa + pot.r_wb, 2 * pot.r_w + pot.r_ab)
        # Out of range wiper position should coerce to 0
        pot.wiper_position = -0.1
        np.testing.assert_allclose(pot.r_wa, pot.r_w + pot.r_ab)
        np.testing.assert_allclose(pot.r_wb, pot.r_w)
        # Out of range wiper position should coerce to 1
        pot.wiper_position = 1.1
        np.testing.assert_allclose(pot.r_wa, pot.r_w)
        np.testing.assert_allclose(pot.r_wb, pot.r_w + pot.r_ab)

    def test_rwb_setter_with_terminal_b_resistance(self):
        """r_wb setter clamps to the range reachable with r_b > 0."""
        pot = Potentiometer(r_ab=100, r_w=10, r_b=20)
        pot.r_wb = 120
        np.testing.assert_allclose(pot.r_wb, 120)
        np.testing.assert_allclose(pot.wiper_position, 0.9)
        pot.r_wb = 999
        np.testing.assert_allclose(pot.r_wb, 130)
        np.testing.assert_allclose(pot.wiper_position, 1.0)


if __name__ == "__main__":
    unittest.main()
