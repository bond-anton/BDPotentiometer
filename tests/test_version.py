""" Test package version is correctly set """

import unittest

try:
    from src.BDPotentiometer import __version__ as version
except ModuleNotFoundError:
    from BDPotentiometer import __version__ as version


class TestVersion(unittest.TestCase):
    """
    Test _version.py has correct version number assigned to global __version__ variable.
    """

    def test_check_version_numbering(self) -> None:
        """
        Version must be string with three integers separated by dot.
        Example: `0.1.4` or `2.0.0`.
        All three digits must not negative and must not be equal to zero at the same time.
        """
        # Assert version is a string.
        self.assertTrue(isinstance(version, str))

        # Assert no extra space present. Example: " 0.1.1  " is not correct, "0.1.1" is correct.
        self.assertEqual(len(version), len(version.strip()))

        # Assert all three parts are present
        v_l = version.split(".")
        self.assertEqual(len(v_l), 3)

        # Assert no extra space present in each part.
        # Example: "0. 1 .1" is not correct, "0.1.1" is correct
        for i in range(3):
            self.assertEqual(len(v_l[i]), len(v_l[i].strip()))

        # Convert all parts of the version to int values
        v_maj = int(v_l[0])
        v_min = int(v_l[1])
        v_patch = int(v_l[2])

        # Assert all version numbers are not negative
        self.assertTrue(v_maj >= 0)
        self.assertTrue(v_min >= 0)
        self.assertTrue(v_patch >= 0)

        # Assert all version numbers are not equal to zero at the same time
        self.assertTrue(v_maj + v_min + v_patch > 0)


if __name__ == "__main__":
    unittest.main()
