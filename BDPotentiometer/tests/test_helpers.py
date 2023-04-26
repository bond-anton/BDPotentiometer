import unittest

from BDPotentiometer.__helpers import (check_integer, check_not_negative, check_positive, coerce,
                                       build_tuple, adjust_tuple)


class TestHelpers(unittest.TestCase):
    def test_check_integer(self):
        a = 1
        self.assertEqual(check_integer(a), a)
        a = 0
        self.assertEqual(check_integer(a), a)
        a = 100
        self.assertEqual(check_integer(a), a)
        a = 100.0
        self.assertEqual(check_integer(a), a)
        a = -100.0
        self.assertEqual(check_integer(a), a)
        a = -0
        self.assertEqual(check_integer(a), a)
        a = -0.0
        self.assertEqual(check_integer(a), a)
        b = check_integer(a)
        self.assertEqual(b, a)
        self.assertIsInstance(b, int)
        with self.assertRaises(ValueError):
            check_integer(1.1)

    def test_non_negative(self):
        a = 1
        self.assertEqual(check_not_negative(a), a)
        a = 0
        self.assertEqual(check_not_negative(a), a)
        a = -0
        self.assertEqual(check_not_negative(a), a)
        a = -0.0
        self.assertEqual(check_not_negative(a), a)
        a = 0.1
        self.assertEqual(check_not_negative(a), a)
        a = 100.2
        self.assertEqual(check_not_negative(a), a)
        with self.assertRaises(ValueError):
            check_not_negative(-a)

    def test_positive(self):
        a = 1
        self.assertEqual(check_positive(a), a)
        a = 0.1
        self.assertEqual(check_positive(a), a)
        a = 100.2
        self.assertEqual(check_positive(a), a)
        with self.assertRaises(ValueError):
            check_positive(-a)
        with self.assertRaises(ValueError):
            check_positive(0)
        with self.assertRaises(ValueError):
            check_positive(-1)
        with self.assertRaises(ValueError):
            check_positive(-0.1)

    def test_coerce(self):
        a = 0
        b = 100
        c = 101
        self.assertEqual(coerce(c, a, b), b)
        self.assertEqual(coerce(c, b, a), b)
        c = -101
        self.assertEqual(coerce(c, a, b), a)
        self.assertEqual(coerce(c, b, a), a)
        with self.assertRaises(ValueError):
            coerce('a', 0, 10)
        with self.assertRaises(ValueError):
            coerce(10, None, 10)
        with self.assertRaises(ValueError):
            coerce(10, 0, None)

    def test_build_tuple(self):
        self.assertEqual(build_tuple(10, 2, func=None), (10, 10))
        with self.assertRaises(ValueError):
            build_tuple(-10, 2, func=check_not_negative)
        with self.assertRaises(ValueError):
            build_tuple(0, 2, func=check_positive)
        with self.assertRaises(ValueError):
            build_tuple(-10, 2, func=2)
        self.assertEqual(build_tuple(-10, 2, func=lambda x: 2 * x), (-20, -20))
        self.assertEqual(build_tuple([-10, -20], 2, func=lambda x: 2 * x), (-20, -40))

    def test_adjust_tuple(self):
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
