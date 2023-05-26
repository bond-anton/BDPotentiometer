""" Module contains basic digital winder class implementation """

from typing import Union
from gpiozero import SPI

from .__helpers import check_integer, check_positive, check_not_negative, coerce


class DigitalWinder:
    """
    Generic digital winder class.
    Digital winder change position by discrete movement between 0 and `max_value`.
    Property `parameters_locked` is used to disable change of `max_value`
    parameter after object is created, only winder position change is allowed.
    """

    def __init__(self, max_value: int = 128, channel: int = 0,
                 parameters_locked: bool = False) -> None:
        self.__locked: bool = bool(parameters_locked)
        self.__channel: int = check_not_negative(check_integer(channel))
        self.__max_value: int = check_positive(check_integer(max_value))
        self.__value: int = 0
        self.read()

    @property
    def locked(self) -> bool:
        """
        Check if parameters of the winder are locked.

        :return: True if locked and False otherwise
        """
        return self.__locked

    @property
    def channel(self) -> int:
        """ Winder channel number """
        return self.__channel

    @channel.setter
    def channel(self, channel: int) -> None:
        self.__channel = check_not_negative(check_integer(channel))

    @property
    def min_value(self) -> int:
        """
        Returns minimal winder position, which is always zero.
        :return: Always return 0.
        """
        return 0

    @property
    def max_value(self) -> int:
        """
        Returns device max winder position value.

        :return: Max winder position value as int.
        """
        return self.__max_value

    @max_value.setter
    def max_value(self, max_value: int) -> None:
        if not self.locked:
            self.__max_value = check_positive(check_integer(max_value))
            self.value = self.__value

    def _set_value(self, value: int) -> int:
        """
        Set given winder position to `value`.

        :param value: Requested value as int.
        :return: Value actually set as int.
        """
        value = coerce(value, 0, self.max_value)
        return value

    def _read_value(self) -> int:
        """
        Read value of winder position.

        :return: Winder position value (int).
        """
        return self.__value

    def read(self) -> None:
        """
        Read winder position into value property.
        """
        self.__value = self._read_value()

    @property
    def value(self) -> int:
        """
        Current winder position.

        :return: Winder position value (int).
        """
        self.read()
        return self.__value

    @value.setter
    def value(self, value: int) -> None:
        value = coerce(check_integer(value), 0, self.max_value)
        data = self._set_value(value)
        self.__value = data


class SpiDigitalWinder(DigitalWinder):
    """ Digital winder with SPI interface """

    def __init__(self, spi: Union[SPI, None] = None,
                 max_value: int = 128, channel: int = 0,
                 parameters_locked: bool = False):
        super().__init__(max_value=max_value, channel=channel, parameters_locked=parameters_locked)
        self.__spi = None
        if isinstance(spi, SPI):
            self.__spi = spi

    @property
    def spi(self) -> Union[SPI, None]:
        """
        Get SPI interface
        :return: SPI interface (gpiozero.SPI)
        """
        return self.__spi

    @spi.setter
    def spi(self, spi: Union[SPI, None]) -> None:
        if isinstance(spi, SPI):
            self.__spi = spi
        self.__spi = None
