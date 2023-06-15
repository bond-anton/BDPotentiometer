""" Tests for Potentiometer `r_wa` and `r_wb` calculation. """

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
        """
        Testing correctness of r_wa and r_wb calculation for
        locked/unlocked potentiometer and rheostat configurations.
        """
        for rheostat in (False, True):
            for locked in (False, True):
                pot = Potentiometer(
                    r_ab=10e3, r_w=75, rheostat=rheostat, parameters_locked=locked
                )
                for pos in np.linspace(0, 1.0, num=101, endpoint=True):
                    r_wa = pot.r_wa(pos)
                    r_wb = pot.r_wb(pos)
                    np.testing.assert_allclose(r_wa, pot.r_w + (1 - pos) * pot.r_ab)
                    np.testing.assert_allclose(pot.r_wa_to_position(r_wa), pos)
                    np.testing.assert_allclose(r_wb, pot.r_w + pos * pot.r_ab)
                    np.testing.assert_allclose(pot.r_wb_to_position(r_wb), pos)
                    np.testing.assert_allclose(r_wa + r_wb, 2 * pot.r_w + pot.r_ab)
                # Out of range wiper position should coerce to 0
                pos = -0.1
                np.testing.assert_allclose(pot.r_wa(pos), pot.r_w + pot.r_ab)
                np.testing.assert_allclose(pot.r_wb(pos), pot.r_w)
                # Out of range wiper position should coerce to 1
                pos = 1.1
                np.testing.assert_allclose(pot.r_wa(pos), pot.r_w)
                np.testing.assert_allclose(pot.r_wb(pos), pot.r_w + pot.r_ab)
                # Out of range resistance should coerce to pot.r_ab + pot.r_w
                np.testing.assert_allclose(
                    pot.r_wa_to_position(pot.r_ab + 2 * pot.r_w),
                    pot.r_wa_to_position(pot.r_ab + pot.r_w),
                )
                np.testing.assert_allclose(
                    pot.r_wb_to_position(pot.r_ab + 2 * pot.r_w),
                    pot.r_wb_to_position(pot.r_ab + pot.r_w),
                )
                # Out of range resistance should coerce to pot.r_w
                np.testing.assert_allclose(
                    pot.r_wa_to_position(0), pot.r_wa_to_position(pot.r_w)
                )
                np.testing.assert_allclose(
                    pot.r_wb_to_position(0), pot.r_wb_to_position(pot.r_w)
                )
                # Out of range (negative) resistance should coerce to pot.r_w
                np.testing.assert_allclose(
                    pot.r_wa_to_position(-1), pot.r_wa_to_position(pot.r_w)
                )
                np.testing.assert_allclose(
                    pot.r_wb_to_position(-1), pot.r_wb_to_position(pot.r_w)
                )


if __name__ == "__main__":
    unittest.main()
