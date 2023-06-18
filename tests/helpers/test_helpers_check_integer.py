""" Testing helpers functions (check_integer). """

import unittest
import numpy as np

try:
    from src.BDPotentiometer.__helpers import check_integer
except ModuleNotFoundError:
    from BDPotentiometer.__helpers import check_integer


class TestHelpersCheckInteger(unittest.TestCase):
    """
    Testing check_integer function.
    """

    def test_check_integer_int(self):
        """Check integers."""
        for input_value in [-100, -3, -0, 0, 2, 100]:
            output_value = check_integer(input_value)
            self.assertEqual(output_value, input_value)
            self.assertIsInstance(output_value, int)
            # Check numpy integer types.
            for numpy_type in [np.int32, np.int64, np.int8]:
                np_input_value = numpy_type(input_value)
                output_value = check_integer(np_input_value)
                self.assertEqual(output_value, input_value)
                self.assertIsInstance(output_value, int)

    def test_check_integer_float(self):
        """Check floats."""
        for input_value in [-100.0, -3.0, float("-0.0"), 0.0, 2.0, 100.0]:
            output_value = check_integer(input_value)
            self.assertEqual(output_value, input_value)
            self.assertIsInstance(output_value, int)
        # Check numpy float types.
        for input_value in [-17.0, -2.0, -1.0, 0.0, 1.0, 137.0]:
            for numpy_type in [np.float32, np.float64]:
                np_input_value = numpy_type(input_value)
                output_value = check_integer(np_input_value)
                np.testing.assert_allclose(output_value, input_value)
                self.assertIsInstance(output_value, int)

    def test_check_integer_wrong_value(self):
        """
        Check ValueError is raised for not integer argument values,
        including special floats.
        """
        for input_value in [
            float("inf"),
            float("-inf"),
            float("nan"),
            np.inf,
            -np.inf,
            -27.1,
            -22.2,
            np.pi,
        ]:
            with self.assertRaises(ValueError):
                check_integer(input_value)

    def test_check_integer_wrong_type(self):
        """Check TypeError is raised for wrong argument type."""
        for input_value in [
            1.1 + 3.2j,  # Complex number
            3.14 + 0j,  # Complex number with zero imaginary part
            "-18.7",
            "b",
            [0.0],
            [1.1, 16.4],
            (np.pi,),
            (4, 2.3),
            None,
        ]:
            with self.assertRaises(TypeError):
                check_integer(input_value)


if __name__ == "__main__":
    unittest.main()
