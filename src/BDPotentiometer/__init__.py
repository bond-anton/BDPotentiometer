""" Module to operate SPI digital potentiometer devices """

# pylint: disable=invalid-name

__version__ = "0.0.4"

from .potentiometer import Potentiometer
from .digital_wiper import DigitalWiper, SpiDigitalWiper
from .digital_potentiometer import DigitalPotentiometerDevice

try:
    from .__gpiozero_helpers import fix_gpiozero_dual_cs_spi
except ModuleNotFoundError:
    from .__gpiozero_helpers import (
        fix_gpiozero_dual_cs_spi_dummy as fix_gpiozero_dual_cs_spi,
    )
