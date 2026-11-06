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
