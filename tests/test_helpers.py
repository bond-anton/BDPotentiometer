""" Testing helpers functions. """

import unittest

try:
    from src.BDPotentiometer.__helpers import (
        check_integer, check_not_negative, check_positive, coerce,
        build_tuple, adjust_tuple
    )
except ModuleNotFoundError:
    from BDPotentiometer.__helpers import (
        check_integer, check_not_negative, check_positive, coerce,
        build_tuple, adjust_tuple
    )


class TestHelpers(unittest.TestCase):
    """ Test case for helpers functions """

    def test_check_integer(self):
        """
        Testing check_integer function
        """
        input_value = 1
        self.assertEqual(check_integer(input_value), input_value)
        input_value = 0
        self.assertEqual(check_integer(input_value), input_value)
        input_value = 100
        self.assertEqual(check_integer(input_value), input_value)
        input_value = 100.0
        self.assertEqual(check_integer(input_value), input_value)
        input_value = -100.0
        self.assertEqual(check_integer(input_value), input_value)
        input_value = -0
        self.assertEqual(check_integer(input_value), input_value)
        input_value = -0.0
        self.assertEqual(check_integer(input_value), input_value)
        output_value = check_integer(input_value)
        self.assertEqual(output_value, input_value)
        self.assertIsInstance(output_value, int)
        with self.assertRaises(ValueError):
            input_value = 100.2
            check_integer(input_value)
        with self.assertRaises(ValueError):
            input_value = 'a'
            check_integer(input_value)

    def test_non_negative(self):
        """
        Testing check_not_negative function
        """
        input_value = 1
        self.assertEqual(check_not_negative(input_value), input_value)
        input_value = 0
        self.assertEqual(check_not_negative(input_value), input_value)
        input_value = -0
        self.assertEqual(check_not_negative(input_value), input_value)
        input_value = -0.0
        self.assertEqual(check_not_negative(input_value), input_value)
        input_value = 0.1
        self.assertEqual(check_not_negative(input_value), input_value)
        input_value = 100.2
        self.assertEqual(check_not_negative(input_value), input_value)
        with self.assertRaises(ValueError):
            input_value = -100.2
            check_not_negative(input_value)

    def test_positive(self):
        """
        Testing check_positive function
        """
        input_value = 1
        self.assertEqual(check_positive(input_value), input_value)
        input_value = 0.1
        self.assertEqual(check_positive(input_value), input_value)
        input_value = 100.2
        self.assertEqual(check_positive(input_value), input_value)
        with self.assertRaises(ValueError):
            check_positive(-input_value)
        with self.assertRaises(ValueError):
            check_positive(0)
        with self.assertRaises(ValueError):
            check_positive(-1)
        with self.assertRaises(ValueError):
            check_positive(-0.1)

    def test_coerce(self):
        """
        Testing coerce function
        """
        left = 0
        right = 100
        input_value = 101
        self.assertEqual(coerce(input_value, left, right), right)
        self.assertEqual(coerce(input_value, right, left), right)
        input_value = -101
        self.assertEqual(coerce(input_value, left, right), left)
        self.assertEqual(coerce(input_value, right, left), left)  # swap bounds
        with self.assertRaises(ValueError):
            coerce('a', 0, 10)
        with self.assertRaises(ValueError):
            coerce(10, None, 10)
        with self.assertRaises(ValueError):
            coerce(10, 0, None)

    def test_build_tuple(self):
        """
        Testing build_tuple function
        """
        self.assertEqual(build_tuple(10, 2, func=None), (10, 10))
        with self.assertRaises(ValueError):
            build_tuple(-10, 2, func=check_not_negative)
        with self.assertRaises(ValueError):
            build_tuple('string value', 2, func=check_not_negative)
        with self.assertRaises(ValueError):
            build_tuple(10, 'string value', func=check_not_negative)
        with self.assertRaises(ValueError):
            build_tuple(0, 2, func=check_positive)
        with self.assertRaises(ValueError):
            build_tuple(-10, 2, func=2)
        with self.assertRaises(ValueError):
            build_tuple([1, 2, 3], 2, func=check_positive)
        with self.assertRaises(ValueError):
            build_tuple([1, 2, 'a'], 3, func=None)
        self.assertEqual(build_tuple(-10, 2, func=lambda x: 2 * x), (-20, -20))
        self.assertEqual(build_tuple([-10, -20], 2, func=lambda x: 2 * x), (-20, -40))

    def test_adjust_tuple(self):
        """
        Testing adjust_tuple function
        """
        value = (1., 2., 3., 4., 5.)
        self.assertEqual(adjust_tuple(value, 2, default_value=4), (1., 2.))
        value = (1., 2.)
        self.assertEqual(adjust_tuple(value, 2, default_value=4), (1., 2.))
        self.assertEqual(adjust_tuple(value, 4, default_value=4), (1., 2., 4., 4.))
        with self.assertRaises(ValueError):
            adjust_tuple(1, 2, default_value=4)
        with self.assertRaises(ValueError):
            adjust_tuple((1.0, ), 'a', default_value=4)
        with self.assertRaises(ValueError):
            adjust_tuple((1.0, ), 2, default_value='a')


if __name__ == '__main__':
    unittest.main()
