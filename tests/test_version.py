""" Test package version is correctly set """
import unittest

try:
    from src.BDPotentiometer import __version__ as v
except ModuleNotFoundError:
    from BDPotentiometer import __version__ as v


class TestVersion(unittest.TestCase):
    """
    Test _version.py has correct version number assigned to global __version__ variable.
    """

    def test_check_version_numbering(self) -> None:
        """Version must be string with three integers separated by dot"""
        self.assertTrue(isinstance(v, str))
        v_l = v.split(".")
        self.assertEqual(len(v_l), 3)
        v_maj = int(v_l[0])
        self.assertTrue(v_maj >= 0)
        v_min = int(v_l[1])
        self.assertTrue(v_min >= 0)
        v_patch = int(v_l[2])
        self.assertTrue(v_patch >= 1)


if __name__ == "__main__":
    unittest.main()
