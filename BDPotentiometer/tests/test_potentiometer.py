import unittest

from BDPotentiometer import DigitalPotentiometerDevice


class MyTestCase(unittest.TestCase):
    def test_r_lim_r_l(self):
        pot = DigitalPotentiometerDevice(max_value=128, default_value=64, channels=1, r_ab=10e3, r_w=75,
                                         r_lim=100, r_l=1e6, max_voltage=5.0)
        self.assertEqual(pot.r_lim, (100,))
        self.assertEqual(pot.r_l, (1e6,))
        pot.r_lim = 200
        self.assertEqual(pot.r_lim, (200,))
        pot.r_l = 2e6
        self.assertEqual(pot.r_l, (2e6,))
        pot.channels_num = 2
        self.assertEqual(pot.r_lim, (200, 0))
        self.assertEqual(pot.r_l, (2e6, 1e6))


if __name__ == '__main__':
    unittest.main()
