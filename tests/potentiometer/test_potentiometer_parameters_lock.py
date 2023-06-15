""" Test access to Potentiometer locked/unlocked properties. """
import unittest

try:
    from src.BDPotentiometer import Potentiometer
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer


class TestPotentiometerLocked(unittest.TestCase):
    """
    Testing Potentiometer properties `r_ab` and `r_w`.
    """

    def setUp(self) -> None:
        self.pot = None
        self.pot_locked = None

    def test_locked(self):
        """
        Test locked potentiometer. Altering of `r_ab` and `r_w` properties should be ignored.
        Changing of any other property is allowed.
        """
        for rheostat in [True, False]:
            self.pot_locked = Potentiometer(
                r_ab=10e3, r_w=75, rheostat=rheostat, parameters_locked=True
            )
            # Assert the device is locked and that property is read-only.
            self.assertTrue(self.pot_locked.parameters_locked)
            with self.assertRaises(AttributeError):
                self.pot_locked.parameters_locked = False
            with self.assertRaises(AttributeError):
                self.pot_locked.parameters_locked = True
            # Try to change `r_ab`, check that the value was not changed.
            initial_value = self.pot_locked.r_ab
            new_value = 2 * initial_value
            self.pot_locked.r_ab = new_value
            self.assertEqual(self.pot_locked.r_ab, initial_value)
            # Try to change `r_w`, check that the value was not changed.
            initial_value = self.pot_locked.r_w
            new_value = 2 * initial_value
            self.pot_locked.r_w = new_value
            self.assertEqual(self.pot_locked.r_w, initial_value)
            # Check that `r_lim`, and `r_load`, and `voltage_in` are not locked.
            initial_value = self.pot_locked.r_lim
            new_value = 2 * initial_value
            self.pot_locked.r_lim = new_value
            self.assertEqual(self.pot_locked.r_lim, new_value)
            initial_value = self.pot_locked.r_load
            new_value = 2 * initial_value
            self.pot_locked.r_load = new_value
            self.assertEqual(self.pot_locked.r_load, new_value)
            initial_value = self.pot_locked.voltage_in
            new_value = 2 * initial_value
            self.pot_locked.voltage_in = new_value
            self.assertEqual(self.pot_locked.voltage_in, new_value)

    def test_unlocked(self):
        """
        Test unlocked potentiometer.
        Changing of any property is allowed.
        """
        for rheostat in [True, False]:
            self.pot = Potentiometer(
                r_ab=10e3, r_w=75, rheostat=rheostat, parameters_locked=False
            )
            # Assert the device is not locked and that property is read-only.
            self.assertFalse(self.pot.parameters_locked)
            with self.assertRaises(AttributeError):
                self.pot.parameters_locked = True
            with self.assertRaises(AttributeError):
                self.pot.parameters_locked = False
            # Try to change `r_ab`, check that the value was changed.
            initial_value = self.pot.r_ab
            new_value = 2 * initial_value
            self.pot.r_ab = new_value
            self.assertEqual(self.pot.r_ab, new_value)
            # Try to change `r_w`, check that the value was changed.
            initial_value = self.pot.r_w
            new_value = 2 * initial_value
            self.pot.r_w = new_value
            self.assertEqual(self.pot.r_w, new_value)
            # Check that `r_lim`, and `r_load`, and `voltage_in` are not locked.
            initial_value = self.pot.r_lim
            new_value = 2 * initial_value
            self.pot.r_lim = new_value
            self.assertEqual(self.pot.r_lim, new_value)
            initial_value = self.pot.r_load
            new_value = 2 * initial_value
            self.pot.r_load = new_value
            self.assertEqual(self.pot.r_load, new_value)
            initial_value = self.pot.voltage_in
            new_value = 2 * initial_value
            self.pot.voltage_in = new_value
            self.assertEqual(self.pot.voltage_in, new_value)


if __name__ == "__main__":
    unittest.main()
