"""Testing helpers functions."""

import unittest

import numpy as np

try:
    from src.BDPotentiometer.__helpers import (
        LABEL_MAX_LENGTH,
        check_label,
        check_not_negative,
        check_positive,
        clamp,
    )
except ModuleNotFoundError:
    from BDPotentiometer.__helpers import (
        LABEL_MAX_LENGTH,
        check_label,
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
        for input_value in [
            "-17.3",
            "a",
            [0.0],
            [1.0, 17.2],
            (np.pi,),
            (2, 2.3),
            None,
            True,
        ]:
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
        for input_value in [
            "-17.3",
            "a",
            [0.0],
            [1.0, 17.2],
            (np.pi,),
            (2, 2.3),
            None,
            True,
        ]:
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
        for input_value in [
            "-17.3",
            "a",
            [0.0],
            [1.0, 17.2],
            (np.pi,),
            (2, 2.3),
            None,
            True,
        ]:
            with self.assertRaises(TypeError):
                clamp(input_value, -10.0, 10)
        for left in ["-17.3", "a", [0.0], [1.0, 17.2], (np.pi,), (2, 2.3), None, False]:
            with self.assertRaises(TypeError):
                clamp(10, left, 10.0)
        for right in ["-17.3", "a", [0.0], [1.0, 17.2], (np.pi,), (2, 2.3), None, True]:
            with self.assertRaises(TypeError):
                clamp(10, -10, right)


class TestHelpersCheckLabel(unittest.TestCase):
    """Test case for the `check_label` helper."""

    def test_check_label_returns_stripped_text(self):
        """Surrounding whitespace never becomes part of the stored label."""
        for input_value, expected in [
            ("a", "a"),
            (" a ", "a"),
            ("\tCH A\n", "CH A"),
            ("CH A", "CH A"),
        ]:
            with self.subTest(input_value=input_value):
                self.assertEqual(check_label(input_value), expected)

    def test_check_label_rejects_non_str(self):
        """Non-string labels are rejected instead of coerced to text."""
        for input_value in [5, 5.0, True, None, b"a", ["a"], ("a",)]:
            with self.subTest(input_value=input_value), self.assertRaises(TypeError):
                check_label(input_value)

    def test_check_label_rejects_empty(self):
        """A label that is empty or whitespace only is rejected."""
        for input_value in ["", " ", "\t", "\n  \t"]:
            with self.subTest(input_value=input_value), self.assertRaises(ValueError):
                check_label(input_value)

    def test_check_label_length_limit(self):
        """Labels up to the limit are accepted, longer ones are rejected."""
        self.assertEqual(check_label("x" * LABEL_MAX_LENGTH), "x" * LABEL_MAX_LENGTH)
        with self.assertRaises(ValueError):
            check_label("x" * (LABEL_MAX_LENGTH + 1))
        # Whitespace is stripped before the length is measured.
        self.assertEqual(
            check_label(" " + "x" * LABEL_MAX_LENGTH + " "), "x" * LABEL_MAX_LENGTH
        )


if __name__ == "__main__":
    unittest.main()
