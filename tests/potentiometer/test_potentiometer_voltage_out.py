"""Tests for Potentiometer class."""

import unittest

import numpy as np

try:
    from src.BDPotentiometer import Potentiometer
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer


class TestPotentiometerVoltageOut(unittest.TestCase):
    """
    Testing Potentiometer.
    """

    def test_voltage_out(self):
        """Testing correctness of output voltage calculation."""
        pot = Potentiometer(r_ab=10e3, r_w=75)
        pot.r_a = 0.0
        pot.r_b = 0.0
        pot.r_load = 1e6
        pot.v_b = 0.0
        pot.v_load = 0.0
        # Zero input voltage should result in zero output voltage
        pot.v_a = 0.0
        for pos in np.linspace(0, 1.0, num=101, endpoint=True):
            pot.wiper_position = pos
            self.assertEqual(pot.v_w, 0.0)
        # Zero load resistance should result in zero output voltage
        pot.r_load = 0
        pot.v_a = 5.0
        for pos in np.linspace(0, 1.0, num=101, endpoint=True):
            pot.wiper_position = pos
            self.assertEqual(pot.v_w, 0.0)
        # Testing range of input voltages
        for voltage in np.linspace(-5, 5, num=101, endpoint=True):
            pot.v_a = voltage
            for pos in np.linspace(0, 1.0, num=101, endpoint=True):
                pot.wiper_position = pos
                if voltage == 0:
                    self.assertEqual(pot.v_w, 0.0)
                    continue
                pot.r_a = 0.0
                pot.r_load = 1e100
                np.testing.assert_allclose(pot.v_w, pot.v_a * pos)
        pot.v_a = 5.0
        pot.r_a = 0.0
        pot.r_b = 0.0
        pot.r_w = 0.0
        pot.r_load = 1.0e10
        for voltage in np.linspace(0.0, 5.0, num=101, endpoint=True):
            pot.v_w = voltage
            np.testing.assert_allclose(pot.v_w, voltage)

    def test_voltage_out_zero_load(self):
        """Zero load resistance shorts the wiper to v_load."""
        pot = Potentiometer(r_ab=10e3, r_w=75)
        pot.r_a = 0.0
        pot.r_b = 0.0
        pot.r_load = 0.0
        pot.v_a = 5.0
        pot.v_b = 0.0
        pot.v_load = 1.0
        for pos in np.linspace(0, 1.0, num=101, endpoint=True):
            pot.wiper_position = pos
            np.testing.assert_allclose(pot.v_w, pot.v_load)

    def test_voltage_out_with_load_source(self):
        """The v_load source reaches the wiper through r_w."""
        pot = Potentiometer(r_ab=10e3, r_w=75)
        pot.r_a = 0.0
        pot.r_b = 0.0
        pot.r_load = 1e3
        pot.v_a = 5.0
        pot.v_b = 0.0
        pot.v_load = 1.0
        pot.wiper_position = 0.5
        self.assertAlmostEqual(pot.v_w, 1.419580, places=6)

    def test_voltage_out_round_trip(self):
        """Setting v_w to the measured value keeps the wiper position."""
        pot = Potentiometer(r_ab=10e3, r_w=75)
        pot.r_a = 0.0
        pot.r_b = 0.0
        pot.r_load = 1e3
        pot.v_a = 5.0
        pot.v_b = 0.0
        pot.v_load = 1.0
        pot.wiper_position = 0.5
        voltage = pot.v_w
        pot.v_w = voltage
        self.assertAlmostEqual(pot.wiper_position, 0.5, places=6)

    def test_voltage_out_wrong_type(self):
        """Testing TypeError is raised on wrong type voltage out input."""
        pot = Potentiometer(r_ab=10e3, r_w=75)
        pot.r_a = 0.0
        pot.r_b = 0.0
        pot.r_load = 1e6
        pot.v_b = 0.0
        pot.v_load = 0.0
        # Zero input voltage should result in zero output voltage
        pot.v_a = 5.0
        # Wrong type
        for v_w in [None, "100.2"]:
            with self.assertRaises(TypeError):
                pot.v_w = v_w

    def test_voltage_out_root_below_v_b_with_finite_load(self):
        """
        A finite load shifts the wiper node outside the rail span, so the
        saturation shortcut must not discard the quadratic root.
        """
        pot = Potentiometer(
            r_ab=100,
            r_a=0.0,
            r_b=0.0,
            r_w=0.0,
            r_load=10.0,
            v_a=10.0,
            v_b=5.0,
            v_load=0.0,
        )
        pot.wiper_position = 0.0
        pot.v_w = 4.0
        np.testing.assert_allclose(pot.wiper_position, 0.029570778197981994, rtol=1e-9)
        np.testing.assert_allclose(pot.v_w, 4.0, atol=1e-9)

    def test_voltage_out_root_below_v_b_with_load_source(self):
        """
        Mirror of the finite-load case: the load source pushes the node above
        the rails and the root below v_b must still be found.
        """
        pot = Potentiometer(
            r_ab=100,
            r_a=0.0,
            r_b=0.0,
            r_w=0.0,
            r_load=10.0,
            v_a=0.0,
            v_b=5.0,
            v_load=100.0,
        )
        pot.wiper_position = 0.0
        pot.v_w = 6.0
        np.testing.assert_allclose(pot.wiper_position, 0.0010706711835039512, rtol=1e-9)
        np.testing.assert_allclose(pot.v_w, 6.0, atol=1e-9)

    def test_voltage_out_near_v_load_uses_stable_root(self):
        """
        A target close to v_load keeps the load current tiny; the root must be
        computed without catastrophic cancellation.
        """
        pot = Potentiometer(
            r_ab=100,
            r_a=0.0,
            r_b=0.0,
            r_w=0.0,
            r_load=1e10,
            v_a=10.0,
            v_b=-10.0,
            v_load=0.0,
        )
        pot.wiper_position = 0.5
        pot.v_w = 1e-9
        np.testing.assert_allclose(pot.wiper_position, 0.5, atol=1e-6)
        np.testing.assert_allclose(pot.v_w, 1e-9, atol=1e-12)

    def test_voltage_out_marginal_root_below_zero_is_clamped(self):
        """
        A root just below zero is clamped to the B terminal instead of being
        discarded, which used to leave the wiper at its previous position.
        """
        pot = Potentiometer(
            r_ab=100,
            r_a=0.0,
            r_b=5.0,
            r_w=1.0,
            r_load=10.0,
            v_a=10.0,
            v_b=5.0,
            v_load=7.0,
        )
        pot.wiper_position = 0.0
        lowest = pot.v_w
        pot.wiper_position = 0.5
        pot.v_w = lowest - 1e-13
        self.assertEqual(pot.wiper_position, 0.0)
        np.testing.assert_allclose(pot.v_w, lowest, atol=1e-12)

    def test_voltage_out_marginal_root_above_one_is_clamped(self):
        """
        A root just above one is clamped to the A terminal instead of being
        discarded, which used to leave the wiper at its previous position.
        """
        pot = Potentiometer(
            r_ab=100,
            r_a=5.0,
            r_b=5.0,
            r_w=1.0,
            r_load=10.0,
            v_a=10.0,
            v_b=5.0,
            v_load=9.0,
        )
        pot.wiper_position = 1.0
        highest = pot.v_w
        pot.wiper_position = 0.5
        pot.v_w = highest + 1e-13
        self.assertEqual(pot.wiper_position, 1.0)
        np.testing.assert_allclose(pot.v_w, highest, atol=1e-12)

    def test_voltage_out_equal_rails_unreachable_target_warns(self):
        """
        Equal rails make v_load unreachable for every position; the wiper must
        not move and the failure must be logged at warning level.
        """
        label = "bdpot-test-v-w-equal-rails"
        pot = Potentiometer(
            r_ab=100,
            r_a=0.0,
            r_b=0.0,
            r_w=0.0,
            r_load=1e10,
            v_a=5.0,
            v_b=5.0,
            v_load=1.0,
            label=label,
        )
        pot.wiper_position = 0.3
        with self.assertLogs(label, level="WARNING"):
            pot.v_w = 1.0
        self.assertEqual(pot.wiper_position, 0.3)

    def test_voltage_out_no_solution_warns_and_holds(self):
        """
        A target that no position can produce is reported at warning level and
        leaves the wiper untouched.
        """
        label = "bdpot-test-v-w-no-solution"
        pot = Potentiometer(
            r_ab=100,
            r_a=0.0,
            r_b=0.0,
            r_w=0.0,
            r_load=1e6,
            v_a=0.0,
            v_b=0.0,
            v_load=0.0,
            label=label,
        )
        pot.wiper_position = 0.4
        with self.assertLogs(label, level="WARNING"):
            pot.v_w = 5.0
        self.assertEqual(pot.wiper_position, 0.4)

    def test_voltage_out_near_equal_rails_does_not_divide_by_zero(self):
        """
        Rails one ulp apart with a far-away v_load used to make the unloaded
        solution divide by a k + 1 denominator that rounds to exactly zero.
        """
        label = "bdpot-test-v-w-near-equal-rails"
        pot = Potentiometer(
            r_ab=1e5,
            r_a=0.0,
            r_b=0.0,
            r_w=0.0,
            r_load=1e6,
            v_a=1.0,
            v_b=0.9999999999999999,
            v_load=1e6,
            label=label,
        )
        pot.wiper_position = 0.5
        with self.assertLogs(label, level="WARNING"):
            pot.v_w = pot.v_load
        self.assertEqual(pot.wiper_position, 1.0)
        self.assertEqual(pot.v_w, 1.0)

    def test_voltage_out_saturates_at_nearest_loaded_endpoint(self):
        """
        A huge series r_a limits the loaded output far below the rail span; the
        unreachable target must saturate at the endpoint with the higher output
        instead of being compared with the rails and held.
        """
        label = "bdpot-test-v-w-nearest-endpoint"
        pot = Potentiometer(
            r_ab=1e3,
            r_a=1e6,
            r_b=0.0,
            r_w=0.0,
            r_load=1e10,
            v_a=10.0,
            v_b=0.0,
            v_load=0.0,
            label=label,
        )
        pot.wiper_position = 0.5
        with self.assertLogs(label, level="WARNING"):
            pot.v_w = 9.0
        self.assertEqual(pot.wiper_position, 1.0)
        np.testing.assert_allclose(pot.v_w, 0.009990008992007094, rtol=1e-12)

    def test_voltage_out_rail_equal_to_v_load_saturates_with_warning(self):
        """
        With v_b == v_load the loaded divider cannot reach v_load at x = 0, so
        the endpoint is a saturation, not a solution, and must be reported.
        """
        label = "bdpot-test-v-w-rail-equal-v-load"
        pot = Potentiometer(
            r_ab=100,
            r_a=0.0,
            r_b=10.0,
            r_w=0.0,
            r_load=10.0,
            v_a=10.0,
            v_b=5.0,
            v_load=5.0,
            label=label,
        )
        pot.wiper_position = 0.5
        with self.assertLogs(label, level="WARNING"):
            pot.v_w = 5.0
        self.assertEqual(pot.wiper_position, 0.0)
        np.testing.assert_allclose(pot.v_w, 110.0 / 21.0, rtol=1e-12)
        self.assertNotEqual(pot.v_w, pot.v_load)

    def test_voltage_out_near_v_load_with_dominant_wiper_resistance(self):
        """
        With r_load << r_w the load pulls the output within a few hundred ppb of
        v_load, so the divider equation cancels its leading terms. The scaled
        solve must still find the position instead of holding the wiper.
        """
        pot = Potentiometer(
            r_ab=1e5,
            r_a=0.0,
            r_b=1.14e5,
            r_w=2.28e6,
            r_load=0.041,
            v_a=10.0,
            v_b=-100.0,
            v_load=1.0,
        )
        pot.wiper_position = 0.0
        target = pot.v_w
        pot.wiper_position = 0.5
        pot.v_w = target
        self.assertEqual(pot.wiper_position, 0.0)
        np.testing.assert_allclose(pot.v_w, target, rtol=1e-12)

    def test_voltage_out_finite_values(self):
        """v_w accepts numpy floats and rejects non-finite values."""
        pot = Potentiometer(r_ab=10e3, r_w=75)
        pot.r_a = 0.0
        pot.r_b = 0.0
        pot.r_load = 1e6
        pot.v_a = 5.0
        pot.v_b = 0.0
        pot.v_load = 0.0
        pot.wiper_position = 0.3
        pot.v_w = np.float32(1.5)
        np.testing.assert_allclose(pot.v_w, 1.5, rtol=1e-5)
        position = pot.wiper_position
        for voltage in [float("inf"), float("-inf"), float("nan")]:
            with self.assertRaises(ValueError):
                pot.v_w = voltage
            self.assertEqual(pot.wiper_position, position)


if __name__ == "__main__":
    unittest.main()
