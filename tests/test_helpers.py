""" Testing helpers functions. """

import unittest
import numpy as np

try:
    from src.BDPotentiometer.__helpers import (
        check_number,
        check_integer,
        check_not_negative,
        check_positive,
        coerce,
        build_tuple,
        adjust_tuple,
    )
except ModuleNotFoundError:
    from BDPotentiometer.__helpers import (
        check_number,
        check_integer,
        check_not_negative,
        check_positive,
        coerce,
        build_tuple,
        adjust_tuple,
    )


class TestHelpers(unittest.TestCase):
    """Test case for helpers functions"""

    def test_check_number(self):
        """
        Testing check_number function.
        Function checks if argument is a real number (not complex).
        return int or float depending on argument type or raises ValueError
        if argument is not a real number.
        check_number does not allow argument to be +-inf, or NaN.
        Special numbers `+0` and `-0` must be converted to just 0
        """
        # Check integer arguments.
        for input_value in [-17, -1, -0, 0, 1, 17]:
            output_value = check_number(input_value)
            self.assertEqual(output_value, input_value)
            self.assertIsInstance(output_value, int)
        # Check float arguments.
        for input_value in [-17.3, -2.0, -1.1, 0.0, 1.0, 17.2]:
            output_value = check_number(input_value)
            self.assertEqual(output_value, input_value)
            self.assertIsInstance(output_value, float)
        # Check numpy integer types.
        for input_value in [-17, -1, 0, 1, 17]:
            for numpy_type in [np.int32, np.int64, np.int8]:
                np_input_value = numpy_type(input_value)
                output_value = check_number(np_input_value)
                self.assertEqual(output_value, input_value)
                self.assertIsInstance(output_value, int)
        # Check numpy float types.
        for input_value in [-17.3, -2.0, -1.1, 0.0, 1.0, 17.2, np.pi]:
            for numpy_type in [np.float32, np.float64]:
                np_input_value = numpy_type(input_value)
                output_value = check_number(np_input_value)
                np.testing.assert_allclose(output_value, input_value)
                self.assertIsInstance(output_value, float)
        # Check +0 and -0 float numbers are converted to 0.0.
        for input_value in [float('+0.0'), float('-0.0')]:
            output_value = check_number(input_value)
            self.assertEqual(output_value, 0.0)
            self.assertIsInstance(output_value, float)
        # Check ValueError is raised for special float +-inf, NaN.
        for input_value in [float('+inf'), float('-inf'), float('nan')]:
            with self.assertRaises(ValueError):
                check_number(input_value)
        # Check TypeError is raised for wrong argument type.
        for input_value in ["-17.3", 'a', [0.0], [1.0, 17.2], (np.pi,), (2, 2.3), None]:
            with self.assertRaises(TypeError):
                check_number(input_value)

    def test_check_integer(self):
        """
        Testing check_integer function
        """
        # Check integers.
        for input_value in [-100, -3, -0, 0, 2, 100]:
            output_value = check_integer(input_value)
            self.assertEqual(output_value, input_value)
            self.assertIsInstance(output_value, int)
        # Check floats.
        for input_value in [-100.0, -3.0, float('-0.0'), 0.0, 2.0, 100.0]:
            output_value = check_integer(input_value)
            self.assertEqual(output_value, input_value)
            self.assertIsInstance(output_value, int)
        # Check numpy integer types.
        for input_value in [-17, -1, 0, 1, 17]:
            for numpy_type in [np.int32, np.int64, np.int8]:
                np_input_value = numpy_type(input_value)
                output_value = check_integer(np_input_value)
                self.assertEqual(output_value, input_value)
                self.assertIsInstance(output_value, int)
        # Check numpy float types.
        for input_value in [-17.0, -2.0, -1.0, 0.0, 1.0, 137.0]:
            for numpy_type in [np.float32, np.float64]:
                np_input_value = numpy_type(input_value)
                output_value = check_integer(np_input_value)
                np.testing.assert_allclose(output_value, input_value)
                self.assertIsInstance(output_value, int)
        # Check ValueError is raised for not integer argument values, including special floats.
        for input_value in [-17.1, -2.2, np.pi, float('inf'), float('-inf'), float('nan')]:
            with self.assertRaises(ValueError):
                check_integer(input_value)
        # Check TypeError is raised for wrong argument type.
        for input_value in ["-17.3", 'a', [0.0], [1.0, 17.2], (np.pi,), (2, 2.3), None]:
            with self.assertRaises(TypeError):
                check_integer(input_value)

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
        for input_value in [100.0, 3.0, float('-0.0'), 0.0, 2.0]:
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
        for input_value in [17.4, 2.0, 1.234, float('-0.0'), 0.0, np.pi]:
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
        for input_value in [float('inf'), float('-inf'), float('nan')]:
            with self.assertRaises(ValueError):
                check_not_negative(input_value)
        # Check TypeError is raised for wrong argument type.
        for input_value in ["-17.3", 'a', [0.0], [1.0, 17.2], (np.pi,), (2, 2.3), None]:
            with self.assertRaises(TypeError):
                check_not_negative(input_value)

    def test_positive(self):
        """
        Testing check_positive function
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
        for input_value in [-100, -2, -17.1, -2.2, -np.pi, 0, 0.0, float('-0.0')]:
            with self.assertRaises(ValueError):
                check_positive(input_value)
        # Check ValueError raised for special floats +-inf, NaN.
        for input_value in [float('inf'), float('-inf'), float('nan')]:
            with self.assertRaises(ValueError):
                check_positive(input_value)
        # Check TypeError is raised for wrong argument type.
        for input_value in ["-17.3", 'a', [0.0], [1.0, 17.2], (np.pi,), (2, 2.3), None]:
            with self.assertRaises(TypeError):
                check_positive(input_value)

    def test_coerce(self):
        """
        Testing coerce function
        """
        # Check non-zero width range.
        left = -0.1  # float
        right = 100  # int
        for input_value in [-1, -1.0, -0.1, 0.0, 0, 1.5, 12, 100.0, 100, 101, 101.0, 234, 235.0]:
            for output_value in [coerce(input_value, left, right),
                                 coerce(input_value, right, left)]:
                if min(left, right) <= input_value <= max(left, right):
                    self.assertEqual(output_value, input_value)
                if input_value < min(left, right):
                    self.assertEqual(output_value, min(left, right))
                if input_value > max(left, right):
                    self.assertEqual(output_value, max(left, right))
                # If input is a float number coerce must return float
                if isinstance(input_value, float):
                    self.assertIsInstance(output_value, float)
        # Check zero width range.
        left = 100.0  # float
        right = 100  # int
        for input_value in [-1, -1.0, 0.0, 0, 100.0, 100, 101, 101.0]:
            for output_value in [coerce(input_value, left, right),
                                 coerce(input_value, right, left)]:
                if min(left, right) <= input_value <= max(left, right):
                    self.assertEqual(output_value, input_value)
                if input_value < min(left, right):
                    self.assertEqual(output_value, min(left, right))
                if input_value > max(left, right):
                    self.assertEqual(output_value, max(left, right))
                # If input is a float number coerce must return float
                if isinstance(input_value, float):
                    self.assertIsInstance(output_value, float)
        # Check TypeError is raised for wrong argument type.
        for input_value in ["-17.3", 'a', [0.0], [1.0, 17.2], (np.pi,), (2, 2.3), None]:
            with self.assertRaises(TypeError):
                coerce(input_value, -10.0, 10)
        for left in ["-17.3", 'a', [0.0], [1.0, 17.2], (np.pi,), (2, 2.3), None]:
            with self.assertRaises(TypeError):
                coerce(10, left, 10.0)
        for right in ["-17.3", 'a', [0.0], [1.0, 17.2], (np.pi,), (2, 2.3), None]:
            with self.assertRaises(TypeError):
                coerce(10, -10, right)

    def test_build_tuple(self):
        """
        Testing build_tuple function
        """
        # Check normal operation: build tuple from single number.
        for input_value in [-1.1, -1, -1.0, 0, 0.0, 1.0, 1, 1.1]:
            for num in [1, 2, 3, 20, 3.0]:
                for func in [check_number, lambda x: 2 * x, None]:
                    output_value = build_tuple(input_value, num, func=func)
                    self.assertEqual(len(output_value), num)
                    for item in output_value:
                        if func is None:
                            self.assertEqual(item, input_value)
                        else:
                            self.assertEqual(item, func(input_value))
                        self.assertIsInstance(item, float)  # build_tuple returns tuple of floats
        # Check normal operation: apply func to given list or tuple.
        for input_value in [[-1.1, -1, 3], (-1.0, 0, 0.0, 1.0, 1, 1.1)]:
            for func in [check_number, lambda x: 2 * x, None]:
                output_value = build_tuple(input_value, len(input_value), func=func)
                self.assertEqual(len(output_value), len(input_value))
                for item_out, item_in in zip(output_value ,input_value):
                    if func is None:
                        self.assertEqual(item_out, item_in)
                    else:
                        self.assertEqual(item_out, func(item_in))
                    self.assertIsInstance(item_out, float)  # build_tuple returns tuple of floats
        # Check ValueError is raised for wrong number of elements
        for input_value in [[2.1, np.pi], (0, 3.14, -4, 5.2)]:
            with self.assertRaises(ValueError):
                build_tuple(input_value, 3, func=None)
        # Check ValueError is raised for wrong num parameter value
        for num in [-3, 2.1, np.pi]:
            with self.assertRaises(ValueError):
                build_tuple(-10, num, func=None)
        # Check TypeError is raised for wrong input value
        for input_value in ['a', "2", [2.2, '1.0'], None]:
            with self.assertRaises(TypeError):
                build_tuple(input_value, 2, func=None)
        # Check TypeError is raised for wrong num parameter value
        for num in ['a', [1, 2, 3], "2", None]:
            with self.assertRaises(TypeError):
                build_tuple(-10, num, func=None)
        # Check TypeError is raised for wrong func parameter value
        for func in [2, 'a', [1, 2, 3]]:
            with self.assertRaises(TypeError):
                build_tuple(-10, 2, func=func)

    def test_adjust_tuple(self):
        """
        Testing adjust_tuple function
        """
        # Check truncate tuple or list
        value = (1, 2.0, 3.0, 4.0, 5.0)  # int values will be converted to float
        self.assertEqual(adjust_tuple(value, 2, default_value=4), (1.0, 2.0))
        self.assertEqual(adjust_tuple(list(value), 2, default_value=4), (1.0, 2.0))
        self.assertEqual(adjust_tuple(list(value), 2.0, default_value=4), (1.0, 2.0))
        # Check grow tuple or list
        value = (1, 2.0)  # int values will be converted to float
        self.assertEqual(adjust_tuple(value, 4, default_value=4), (1.0, 2.0, 4.0, 4.0))
        self.assertEqual(adjust_tuple(list(value), 4, default_value=4), (1.0, 2.0, 4.0, 4.0))
        # Check leave tuple or least unchanged
        value = (1.0, 2.0, 3)  # int values will be converted to float
        self.assertEqual(adjust_tuple(value, 3, default_value=4), (1.0, 2.0, 3.0))
        self.assertEqual(adjust_tuple(list(value), 3, default_value=4), (1.0, 2.0, 3.0))
        # Check TypeError is raised for wrong input value
        for input_value in [1, 2.3, ['a', 2], (None, 1.1), None]:
            with self.assertRaises(TypeError):
                adjust_tuple(input_value, 2, default_value=4)
        # Check TypeError is raised for wrong num value
        for num in ["1", ['a', 2], (None, 1.1), None]:
            with self.assertRaises(TypeError):
                adjust_tuple((1.0, 2.2), num, default_value=4)
        # Check ValueError is raised for wrong num value
        for num in [-3, -1.0, 2.3]:
            with self.assertRaises(ValueError):
                adjust_tuple((1.0, 2.2), num, default_value=4)
        # Check TypeError is raised for wrong default value
        for default_value in ["1", ['a', 2], (None, 1.1), None]:
            with self.assertRaises(TypeError):
                adjust_tuple((1.0, 2.2), 2, default_value=default_value)


if __name__ == "__main__":
    unittest.main()
