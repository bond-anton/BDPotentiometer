""" Testing helpers functions (check_number). """

import unittest
import numpy as np

try:
    from src.BDPotentiometer.__helpers import check_number
except ModuleNotFoundError:
    from BDPotentiometer.__helpers import check_number


class TestHelpersCheckNumber(unittest.TestCase):
    """
    Testing check_number function.
    Function checks if argument is a real number (not complex).
    return int or float depending on argument type or raises ValueError
    if argument is not a real number.
    check_number does not allow argument to be +-inf, or NaN.
    Special numbers `+0` and `-0` must be converted to just 0
    """

    def test_check_number_int(self):
        """Check integer arguments."""
        for input_value in [-17, -1, -0, 0, 1, 17]:
            output_value = check_number(input_value)
            self.assertEqual(output_value, input_value)
            self.assertIsInstance(output_value, int)
            # Check numpy integer types.
            for numpy_type in [np.int32, np.int64, np.int8]:
                np_input_value = numpy_type(input_value)
                output_value = check_number(np_input_value)
                self.assertEqual(output_value, input_value)
                self.assertIsInstance(output_value, int)

    def test_check_number_float(self):
        """Check float arguments."""
        for input_value in [-17.3, -2.0, -1.1, 0.0, 1.0, 17.2]:
            output_value = check_number(input_value)
            self.assertEqual(output_value, input_value)
            self.assertIsInstance(output_value, float)
            # Check numpy float types.
            for numpy_type in [np.float32, np.float64]:
                np_input_value = numpy_type(input_value)
                output_value = check_number(np_input_value)
                np.testing.assert_allclose(output_value, input_value)
                self.assertIsInstance(output_value, float)
        # Check +0 and -0 float numbers are converted to 0.0.
        for input_value in [float("+0.0"), float("-0.0")]:
            output_value = check_number(input_value)
            self.assertEqual(output_value, 0.0)
            self.assertIsInstance(output_value, float)

    def test_check_number_float_inf_nan(self):
        """Check float inf and nan arguments."""
        # Check ValueError is raised for special float +-inf, NaN.
        for input_value in [
            float("+inf"),
            float("-inf"),
            float("nan"),
            np.inf,
            -np.inf,
        ]:
            with self.assertRaises(ValueError):
                check_number(input_value)

    def test_check_number_wrong_type(self):
        """Check TypeError is raised for wrong argument type."""
        for input_value in [
            1.1 + 3.5j,  # Complex value
            1.1 + 0j,  # Complex value with zero imaginary part
            "-17.3",
            "a",
            [0.0],
            [1.0, 17.2],
            (np.pi,),
            (2, 2.3),
            None,
        ]:
            with self.assertRaises(TypeError):
                check_number(input_value)


if __name__ == "__main__":
    unittest.main()
