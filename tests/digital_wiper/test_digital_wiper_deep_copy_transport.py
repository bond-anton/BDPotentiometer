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
        pot = Potentiometer(r_ab=10e3, r_w=75)
        self.transport = FakeSpiTransport()
        self.spi_digital_wiper = SpiDigitalWiper(
            potentiometer=pot, transport=self.transport, max_value=128
        )

    def test_transport_shared(self):
        """
        Test the copied wiper shares the transport by identity.
        """
        self.spi_digital_wiper.value = 43
        dw_copy = deepcopy(self.spi_digital_wiper)
        self.assertIs(dw_copy.transport, self.transport)
        self.assertIs(dw_copy.transport, self.spi_digital_wiper.transport)
        self.assertIs(dw_copy.spi, self.spi_digital_wiper.spi)
        self.assertIsNot(dw_copy.potentiometer, self.spi_digital_wiper.potentiometer)
        self.assertEqual(
            dw_copy.potentiometer.r_ab, self.spi_digital_wiper.potentiometer.r_ab
        )
        self.assertEqual(
            dw_copy.potentiometer.r_w, self.spi_digital_wiper.potentiometer.r_w
        )
        self.assertEqual(dw_copy.value, self.spi_digital_wiper.value)


if __name__ == "__main__":
    unittest.main()
