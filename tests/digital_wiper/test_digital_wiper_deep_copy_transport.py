"""Tests for SpiDigitalWiper deep copy with an injected transport."""

import unittest
from copy import deepcopy

try:
    from src.BDPotentiometer import Potentiometer, SpiDigitalWiper
    from src.BDPotentiometer.transport import FakeSpiTransport
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, SpiDigitalWiper
    from BDPotentiometer.transport import FakeSpiTransport


class TestSpiDigitalWiperDeepCopyTransport(unittest.TestCase):
    """
    Testing SpiDigitalWiper deep copy keeps the bus handle shared.
    """

    def setUp(self) -> None:
        """
        Set up Unittest
        """
        self.pot = Potentiometer(r_ab=10e3, r_w=75)
        self.transport = FakeSpiTransport()
        self.spi_digital_wiper = SpiDigitalWiper(
            potentiometer=self.pot, transport=self.transport, max_value=128
        )

    def test_transport_shared(self):
        """
        Test the copied wiper shares the transport by identity.
        """
        self.spi_digital_wiper.value = 43
        dw_copy = deepcopy(self.spi_digital_wiper)
        self.assertIs(dw_copy.transport, self.transport)
        self.assertIs(dw_copy.transport, self.spi_digital_wiper.transport)

    def test_rest_deep_copied(self):
        """
        Test everything except the transport is still deep-copied.
        """
        self.spi_digital_wiper.r_a = 200
        self.spi_digital_wiper.r_b = 400
        self.spi_digital_wiper.r_load = 1e100
        self.spi_digital_wiper.v_a = 5
        self.spi_digital_wiper.v_b = 2
        self.spi_digital_wiper.v_load = -1
        dw_copy = deepcopy(self.spi_digital_wiper)
        self.assertIsInstance(dw_copy, SpiDigitalWiper)
        self.assertNotEqual(dw_copy, self.spi_digital_wiper)
        self.assertIsNot(dw_copy.potentiometer, self.spi_digital_wiper.potentiometer)
        self.assertEqual(dw_copy.min_value, self.spi_digital_wiper.min_value)
        self.assertEqual(dw_copy.max_value, self.spi_digital_wiper.max_value)
        self.assertEqual(
            dw_copy.potentiometer.r_ab, self.spi_digital_wiper.potentiometer.r_ab
        )
        self.assertEqual(
            dw_copy.potentiometer.r_w, self.spi_digital_wiper.potentiometer.r_w
        )
        self.assertEqual(
            dw_copy.potentiometer.r_a, self.spi_digital_wiper.potentiometer.r_a
        )
        self.assertEqual(
            dw_copy.potentiometer.r_b, self.spi_digital_wiper.potentiometer.r_b
        )
        self.assertEqual(
            dw_copy.potentiometer.r_load, self.spi_digital_wiper.potentiometer.r_load
        )
        self.assertEqual(
            dw_copy.potentiometer.v_a, self.spi_digital_wiper.potentiometer.v_a
        )
        self.assertEqual(
            dw_copy.potentiometer.v_b, self.spi_digital_wiper.potentiometer.v_b
        )
        self.assertEqual(
            dw_copy.potentiometer.v_load, self.spi_digital_wiper.potentiometer.v_load
        )
        self.assertEqual(dw_copy.spi, self.spi_digital_wiper.spi)


if __name__ == "__main__":
    unittest.main()
