""" Tests for SpiDigitalWiper class constructor. """

import unittest

try:
    from src.BDPotentiometer import Potentiometer, SpiDigitalWiper
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, SpiDigitalWiper


class TestSpiDigitalWiperConstructor(unittest.TestCase):
    """
    Testing SpiDigitalWiper constructor.
    """

    def setUp(self) -> None:
        """
        Set up Unittest
        """
        self.pot = Potentiometer(
            r_ab=10e3, r_w=75, rheostat=False, parameters_locked=False
        )
        self.spi_digital_wiper = SpiDigitalWiper(
            spi=None, potentiometer=self.pot, max_value=128, parameters_locked=False
        )

    def test_spi_digital_wiper(self):
        """
        Test SpiDigitalWiper constructor (without SPI interface).
        """
        digital_wiper = SpiDigitalWiper(
            spi=None, potentiometer=self.pot, max_value=128, parameters_locked=False
        )
        self.assertEqual(digital_wiper.spi, None)
        digital_wiper.spi = None
        self.assertEqual(digital_wiper.spi, None)


if __name__ == "__main__":
    unittest.main()
