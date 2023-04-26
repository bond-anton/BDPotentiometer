import unittest


class TestVersion(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_check_if_integer(self) -> None:
        from BDPotentiometer._version import __version__ as v
        self.assertTrue(isinstance(v, str))
        v_l = v.split('.')
        self.assertEqual(len(v_l), 3)
        v_maj = int(v_l[0])
        self.assertTrue(v_maj >= 0)
        v_min = int(v_l[1])
        self.assertTrue(v_min >= 0)
        v_patch = int(v_l[2])
        self.assertTrue(v_patch >= 1)


if __name__ == '__main__':
    unittest.main()
