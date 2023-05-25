import unittest

from BDPotentiometer import DigitalRheostatDevice


class TestRheostat(unittest.TestCase):

    def setUp(self) -> None:
        self.rheostat = DigitalRheostatDevice(max_value=128, default_value=64, channels=1, r_ab=10e3, r_w=75)

    def test_create_object(self) -> None:
        rheo = DigitalRheostatDevice(max_value=128, default_value=64, channels=1, r_ab=10e3, r_w=75)
        self.assertEqual(rheo.max_value, 128)
        self.assertEqual(rheo.default_value, 64)
        self.assertEqual(rheo.channels_num, 1)
        self.assertEqual(rheo.r_ab, 10.0e3)
        self.assertEqual(rheo.r_w, 75)
        with self.assertRaises(ValueError):
            _ = DigitalRheostatDevice(max_value=-128, default_value=64, channels=1, r_ab=10e3, r_w=75)
        with self.assertRaises(ValueError):
            _ = DigitalRheostatDevice(max_value=128.1, default_value=64, channels=1, r_ab=10e3, r_w=75)
        with self.assertRaises(ValueError):
            _ = DigitalRheostatDevice(max_value=-128.1, default_value=64, channels=1, r_ab=10e3, r_w=75)
        with self.assertRaises(ValueError):
            _ = DigitalRheostatDevice(max_value=None, default_value=64, channels=1, r_ab=10e3, r_w=75)
        with self.assertRaises(ValueError):
            _ = DigitalRheostatDevice(max_value='a', default_value=64, channels=1, r_ab=10e3, r_w=75)
        rheo = DigitalRheostatDevice(max_value=128.0, default_value=64, channels=1, r_ab=10e3, r_w=75)
        self.assertEqual(rheo.max_value, 128)
        with self.assertRaises(ValueError):
            rheo = DigitalRheostatDevice(max_value=128, default_value=-64, channels=1, r_ab=10e3, r_w=75)
        with self.assertRaises(ValueError):
            rheo = DigitalRheostatDevice(max_value=128, default_value=64.1, channels=1, r_ab=10e3, r_w=75)
        with self.assertRaises(ValueError):
            rheo = DigitalRheostatDevice(max_value=128, default_value='a', channels=1, r_ab=10e3, r_w=75)
        rheo = DigitalRheostatDevice(max_value=128, default_value=129, channels=1, r_ab=10e3, r_w=75)
        self.assertEqual(rheo.max_value, 128)
        self.assertEqual(rheo.default_value, 128)
        rheo = DigitalRheostatDevice(max_value=128, default_value=64, channels=1, r_ab=10e3, r_w=75)
        self.assertEqual(rheo.channels_num, 1)
        rheo = DigitalRheostatDevice(max_value=128, default_value=64, channels=10, r_ab=10e3, r_w=75)
        self.assertEqual(rheo.channels_num, 10)
        rheo = DigitalRheostatDevice(max_value=128, default_value=64, channels=2, r_ab=10e3, r_w=75)
        self.assertEqual(rheo.channels_num, 2)
        self.assertEqual(rheo.channels, (0, 1))
        self.assertEqual(rheo.value, (64, 64))
        with self.assertRaises(ValueError):
            _ = DigitalRheostatDevice(max_value=128, default_value=64, channels=2, r_ab=-10e3, r_w=75)
        with self.assertRaises(ValueError):
            _ = DigitalRheostatDevice(max_value=128, default_value=64, channels=2, r_ab=10.0e3, r_w=-75)

    def test_min_value(self):
        rheo = DigitalRheostatDevice(max_value=128, default_value=64, channels=1, r_ab=10e3, r_w=75)
        self.assertEqual(rheo.min_value, 0)
        with self.assertRaises(AttributeError):
            rheo.min_value = 1
        rheo.__min_value = 10
        self.assertEqual(rheo.min_value, 0)

    def test_max_value(self):
        rheo = DigitalRheostatDevice(max_value=128, default_value=64, channels=1, r_ab=10e3, r_w=75)
        self.assertEqual(rheo.max_value, 128)
        rheo.max_value = 64
        self.assertEqual(rheo.max_value, 64)
        self.assertEqual(rheo.default_value, 64)
        rheo.max_value = 63
        self.assertEqual(rheo.max_value, 63)
        self.assertEqual(rheo.default_value, 63)
        self.assertEqual(rheo.value, (63,))
        with self.assertRaises(ValueError):
            rheo.max_value = 0
        self.assertEqual(rheo.max_value, 63)
        with self.assertRaises(ValueError):
            rheo.max_value = 127.9
        with self.assertRaises(ValueError):
            rheo.max_value = -128.0
        with self.assertRaises(ValueError):
            rheo.max_value = -128
        with self.assertRaises(ValueError):
            rheo.max_value = None
        with self.assertRaises(ValueError):
            rheo.max_value = 'a'
        rheo.max_value = 128.0
        self.assertEqual(rheo.max_value, 128)
        rheo.max_value = 1
        self.assertEqual(rheo.max_value, 1)
        self.assertEqual(rheo.default_value, 1)
        self.assertEqual(rheo.value, (1,))

    def test_channels(self):
        rheo = DigitalRheostatDevice(max_value=128, default_value=64, channels=1, r_ab=10e3, r_w=75)
        self.assertEqual(rheo.value, (64,))
        rheo.channels_num = 2
        self.assertEqual(rheo.value, (64, 64))
        rheo.channels_num = 1
        self.assertEqual(rheo.value, (64,))

    def test_r_ab(self):
        rheo = DigitalRheostatDevice(max_value=128, default_value=64, channels=1, r_ab=10e3, r_w=75)
        self.assertEqual(rheo.r_ab, 10e3)
        rheo.r_ab = 500
        self.assertEqual(rheo.r_ab, 500)
        rheo.r_ab = 0
        self.assertEqual(rheo.r_ab, 0)
        with self.assertRaises(ValueError):
            rheo.r_ab = -10

    def test_r_w(self):
        rheo = DigitalRheostatDevice(max_value=128, default_value=64, channels=1, r_ab=10e3, r_w=75)
        self.assertEqual(rheo.r_w, 75)
        rheo.r_w = 500
        self.assertEqual(rheo.r_w, 500)
        rheo.r_w = 0
        self.assertEqual(rheo.r_w, 0)
        with self.assertRaises(ValueError):
            rheo.r_w = -10

    def test_coerce_value(self):
        rheo = DigitalRheostatDevice(max_value=128, default_value=64, channels=10,
                                     r_ab=10e3, r_w=75)
        self.assertEqual(rheo._coerce_value(129), 128)
        self.assertEqual(rheo._coerce_value(10), 10)
        self.assertEqual(rheo._coerce_value(-129), 0)

    def test_set_value(self):
        rheo = DigitalRheostatDevice(max_value=128, default_value=64, channels=10,
                                     r_ab=10e3, r_w=75)
        self.assertEqual(rheo._set_value(channel=0, value=129), 128)
        self.assertEqual(rheo._set_value(channel=0, value=10), 10)
        self.assertEqual(rheo._set_value(channel=0, value=-129), 0)
        with self.assertRaises(ValueError):
            rheo._set_value(channel=10, value=100)

    def test_set_read_value(self):
        rheo = DigitalRheostatDevice(max_value=128, default_value=64, channels=2, r_ab=10e3, r_w=75)
        self.assertEqual(rheo.value, (64, 64))
        self.assertEqual(rheo._read_value(0), 64)
        self.assertEqual(rheo._read_value(1), 64)
        rheo.set(channel=0, value=129)
        self.assertEqual(rheo.value, (128, 64))
        rheo.set(channel=1, value=19)
        self.assertEqual(rheo.value, (128, 19))
        self.assertEqual(rheo.read(0), 128)
        self.assertEqual(rheo.read(1), 19)
        with self.assertRaises(ValueError):
            rheo.set(channel=2, value=10)
        with self.assertRaises(ValueError):
            rheo.read(channel=2)
        rheo.value = [0, 0]
        self.assertEqual(rheo.value, (0, 0))
        rheo.value = (64, 128)
        self.assertEqual(rheo.value, (64, 128))
        with self.assertRaises(ValueError):
            rheo.value = [64, 'a']
        with self.assertRaises(ValueError):
            rheo.value = [64]

    def test_set_r(self):
        max_value = 128
        default_value = 64
        r_ab = 10e3
        r_w = 75
        rheo = DigitalRheostatDevice(max_value=max_value, default_value=64, channels=2,
                                     r_ab=r_ab, r_w=r_w)

        def r2v(r):
            return int(round((r - r_w) / r_ab * max_value))

        def v2r(v):
            return r_ab * v / max_value + r_w

        rheo.set_r(channel=0, resistance=11e3)
        self.assertEqual(rheo.value, (max_value, default_value))
        self.assertEqual(rheo.r_wb, (r_ab + r_w, v2r(default_value)))
        rheo.set_r(channel=1, resistance=1e3)
        v = r2v(1e3)
        r = rheo.r_wb[1]
        err = abs(1e3 - r)
        err1 = abs(1e3 - v2r(v - 1))
        err2 = abs(1e3 - v2r(v + 1))
        self.assertEqual(rheo.value, (max_value, v))
        self.assertTrue(err < err1)
        self.assertTrue(err < err2)
        self.assertTrue(err <= r_ab / max_value)

        rheo.r_wb = [1e3, 1e3]
        self.assertEqual(rheo.value, (v, v))
        with self.assertRaises(ValueError):
            rheo.r_wb = 1e3
        with self.assertRaises(ValueError):
            rheo.r_wb = [1e3]
        with self.assertRaises(ValueError):
            rheo.r_wb = [1e3, 'a']


if __name__ == '__main__':
    unittest.main()
