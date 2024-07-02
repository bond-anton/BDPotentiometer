""" Tests for DigitalWiper channel numbering. """

import unittest

try:
    from src.BDPotentiometer import Potentiometer, DigitalWiper
except ModuleNotFoundError:
    from BDPotentiometer import Potentiometer, DigitalWiper


class TestDigitalWiperChannelNumbering(unittest.TestCase):
    """
    Testing DigitalWiper channel numbering.
    """

    def test_channel_numbering(self):
        """
        Testing channel numbering.
        DigitalWiper Channel is a channel of the actual digital potentiometer device,
        numbered in int numbers starting from 0.
        """
        pot = Potentiometer(r_ab=20e3, r_w=50)
        for max_value in [1, 64, 128, 256]:
            digital_wiper = DigitalWiper(potentiometer=pot, max_value=max_value)
            self.assertEqual(digital_wiper.channel, 0)  # default channel number is 0
            # Correct channel numbers
            for channel_number in [3, 4.0, 1234, 0, 17]:
                digital_wiper.channel = channel_number
                self.assertEqual(digital_wiper.channel, channel_number)
                self.assertIsInstance(digital_wiper.channel, int)
            # Wrong channel number value
            for channel_number_ in [-1, 1.12]:
                with self.assertRaises(ValueError):
                    digital_wiper.channel = channel_number_
            # Wrong channel number type
            for channel_number_ in ["1", None]:
                with self.assertRaises(TypeError):
                    digital_wiper.channel = channel_number_
            self.assertEqual(
                digital_wiper.channel, channel_number
            )  # Check that channel number did not_change


if __name__ == "__main__":
    unittest.main()
