""" Module to operate SPI digital potentiometer devices """

# pylint: disable=invalid-name

from ._version import __version__
from .potentiometer import Potentiometer
from .digital_winder import DigitalWinder, SpiDigitalWinder
from .digital_potentiometer import DigitalPotentiometerDevice

try:
    from .__gpiozero_helpers import fix_gpiozero_dual_cs_spi
except ModuleNotFoundError:
    from .__gpiozero_helpers import fix_gpiozero_dual_cs_spi_dummy as fix_gpiozero_dual_cs_spi
