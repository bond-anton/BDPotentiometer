"""Testing helpers functions."""

import unittest

import numpy as np

try:
    from src.BDPotentiometer.__helpers import (
        check_not_negative,
        check_positive,
        clamp,
    )
except ModuleNotFoundError:
    from BDPotentiometer.__helpers import (
        check_not_negative,
        check_positive,
        clamp,
    )


class TestHelpers(unittest.TestCase):
    """Test case for helpers functions"""

    def test_non_negative(self):
        """
        Testing check_not_negative function.
        """
        # Check integers.
        for input_value in [100, 3, -0, 0, 2]:
            output_value = check_not_negative(input_value)
            self.assertEqual(output_value, input_value)
            self.assertIsInstance(output_value, int)
        # Check floats.
        for input_value in [100.0, 3.0, float("-0.0"), 0.0, 2.0]:
            output_value = check_not_negative(input_value)
            self.assertEqual(output_value, input_value)
            self.assertIsInstance(output_value, float)
        # Check numpy integer types.
        for input_value in [17, 1, 0, 17]:
            for numpy_type in [np.int32, np.int64, np.int8]:
                np_input_value = numpy_type(input_value)
                output_value = check_not_negative(np_input_value)
                self.assertEqual(output_value, input_value)
                self.assertIsInstance(output_value, int)
        # Check numpy float types.
        for input_value in [17.4, 2.0, 1.234, float("-0.0"), 0.0, np.pi]:
            for numpy_type in [np.float32, np.float64]:
                np_input_value = numpy_type(input_value)
                output_value = check_not_negative(np_input_value)
                np.testing.assert_allclose(output_value, input_value)
                self.assertIsInstance(output_value, float)
        # Check ValueError raised for negative values.
        for input_value in [-100, -2, -17.1, -2.2, -np.pi]:
            with self.assertRaises(ValueError):
                check_not_negative(input_value)
        # Check ValueError raised for special floats +-inf, NaN.
        for input_value in [float("inf"), float("-inf"), float("nan")]:
            with self.assertRaises(ValueError):
                check_not_negative(input_value)
        # Check TypeError is raised for wrong argument type.
        for input_value in ["-17.3", "a", [0.0], [1.0, 17.2], (np.pi,), (2, 2.3), None]:
            with self.assertRaises(TypeError):
                check_not_negative(input_value)

    def test_positive(self):
        """
        Testing check_positive function.
        """
        # Check integers.
        for input_value in [100, 3, 2]:
            output_value = check_positive(input_value)
            self.assertEqual(output_value, input_value)
            self.assertIsInstance(output_value, int)
        # Check floats.
        for input_value in [100.0, 3.0, 2.0]:
            output_value = check_positive(input_value)
            self.assertEqual(output_value, input_value)
            self.assertIsInstance(output_value, float)
        # Check numpy integer types.
        for input_value in [17, 1, 17]:
            for numpy_type in [np.int32, np.int64, np.int8]:
                np_input_value = numpy_type(input_value)
                output_value = check_positive(np_input_value)
                self.assertEqual(output_value, input_value)
                self.assertIsInstance(output_value, int)
        # Check numpy float types.
        for input_value in [17.4, 2.0, 1.234, np.pi]:
            for numpy_type in [np.float32, np.float64]:
                np_input_value = numpy_type(input_value)
                output_value = check_positive(np_input_value)
                np.testing.assert_allclose(output_value, input_value)
                self.assertIsInstance(output_value, float)
        # Check ValueError raised for negative and zero values.
        for input_value in [-100, -2, -17.1, -2.2, -np.pi, 0, 0.0, float("-0.0")]:
            with self.assertRaises(ValueError):
                check_positive(input_value)
        # Check ValueError raised for special floats +-inf, NaN.
        for input_value in [float("inf"), float("-inf"), float("nan")]:
            with self.assertRaises(ValueError):
                check_positive(input_value)
        # Check TypeError is raised for wrong argument type.
        for input_value in ["-17.3", "a", [0.0], [1.0, 17.2], (np.pi,), (2, 2.3), None]:
            with self.assertRaises(TypeError):
                check_positive(input_value)

    def test_clamp(self):
        """
        Testing clamp function normal operation.
        """
        # Check non-zero width range.
        left = -0.1  # float
        right = 100  # int
        for input_value in [
            -1,
            -1.0,
            -0.1,
            0,
            1.5,
            12,
            100.0,
            100,
            101,
            101.0,
        ]:
            for output_value in [
                clamp(input_value, left, right),
                clamp(input_value, right, left),
            ]:
                if min(left, right) <= input_value <= max(left, right):
                    self.assertEqual(output_value, input_value)
                elif input_value < min(left, right):
                    self.assertEqual(output_value, min(left, right))
                elif input_value > max(left, right):
                    self.assertEqual(output_value, max(left, right))
                # If input is a float number clamp must return float
                if isinstance(input_value, float):
                    self.assertIsInstance(output_value, float)
        # Check zero width range.
        left = 100.0  # float
        right = 100  # int
        for input_value in [-1, -1.0, 0.0, 0, 100.0, 100, 101, 101.0]:
            for output_value in [
                clamp(input_value, left, right),
                clamp(input_value, right, left),
            ]:
                if min(left, right) <= input_value <= max(left, right):
                    self.assertEqual(output_value, input_value)
                if input_value < min(left, right):
                    self.assertEqual(output_value, min(left, right))
                if input_value > max(left, right):
                    self.assertEqual(output_value, max(left, right))
                # If input is a float number clamp must return float
                if isinstance(input_value, float):
                    self.assertIsInstance(output_value, float)

    def test_clamp_errors(self):
        """
        Testing clamp function errors.
        """
        # Check TypeError is raised for wrong argument type.
        for input_value in ["-17.3", "a", [0.0], [1.0, 17.2], (np.pi,), (2, 2.3), None]:
            with self.assertRaises(TypeError):
                clamp(input_value, -10.0, 10)
        for left in ["-17.3", "a", [0.0], [1.0, 17.2], (np.pi,), (2, 2.3), None]:
            with self.assertRaises(TypeError):
                clamp(10, left, 10.0)
        for right in ["-17.3", "a", [0.0], [1.0, 17.2], (np.pi,), (2, 2.3), None]:
            with self.assertRaises(TypeError):
                clamp(10, -10, right)


if __name__ == "__main__":
    unittest.main()
