""" Module contains basic digital winder class implementation """

from copy import deepcopy
from typing import Union
from gpiozero import SPI

from .potentiometer import Potentiometer
from .__helpers import check_integer, check_positive, check_not_negative, coerce


class DigitalWinder:
    """
    Generic digital winder class.
    Digital winder change position by discrete movement between 0 and `max_value`.
    Property `parameters_locked` is used to disable change of `max_value`
    parameter after object is created, only winder position change is allowed.
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        potentiometer: Potentiometer,
        max_value: int = 128,
        parameters_locked: bool = False,
    ) -> None:
        self.__locked: bool = bool(parameters_locked)
        self.__potentiometer = potentiometer
        self.__channel: int = 0
        self.__max_value: int = check_integer(check_positive(max_value))
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
    def potentiometer(self) -> Potentiometer:
        """
        Access Potentiometer instance.
        :return: Potentiometer
        """
        return self.__potentiometer

    @property
    def channel(self) -> int:
        """Winder channel number"""
        return self.__channel

    @channel.setter
    def channel(self, channel: int) -> None:
        self.__channel = check_integer(check_not_negative(channel))

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
            self.__max_value = check_integer(check_positive(max_value))
            self.value = self.__value

    def _set_value(self, value: int) -> int:
        """
        Set given winder position to `value`.

        :param value: Requested value as int.
        :return: Value actually set as int.
        """
        value = int(round(coerce(value, 0, self.max_value)))
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
        value = check_integer(coerce(value, 0, self.max_value))
        data = self._set_value(value)
        self.__value = data

    @property
    def r_wb(self) -> float:
        """
        Calculates resistance between terminals B and W.

        :return: Resistance between terminals B and W (float).
        """
        return self.potentiometer.r_wb(self.value / self.max_value)

    @r_wb.setter
    def r_wb(self, resistance: float) -> None:
        self.value = int(
            round(self.potentiometer.r_wb_to_position(resistance) * self.max_value)
        )

    @property
    def r_wa(self) -> float:
        """
        Calculates resistance between terminals A and W.

        :return: Resistance between terminals A and W (float).
        """
        return self.potentiometer.r_wa(self.value / self.max_value)

    @r_wa.setter
    def r_wa(self, resistance: float) -> None:
        self.value = int(
            round(self.potentiometer.r_wa_to_position(resistance) * self.max_value)
        )

    @property
    def voltage_in(self) -> float:
        """
        Device input Voltage.

        :return: Input voltage (float).
        """
        return self.potentiometer.voltage_in

    @voltage_in.setter
    def voltage_in(self, voltage: float) -> None:
        self.potentiometer.voltage_in = voltage

    @property
    def voltage_out(self) -> float:
        """
        Calculates output voltage for given winder position.

        :return: Output voltage (float).
        """
        return self.potentiometer.voltage_out(self.value / self.max_value)

    @voltage_out.setter
    def voltage_out(self, voltage: float) -> None:
        self.value = int(
            round(
                self.potentiometer.voltage_out_to_winder_position(voltage)
                * self.max_value
            )
        )

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for key, value in self.__dict__.items():
            setattr(result, key, deepcopy(value, memo))
        return result


class SpiDigitalWinder(DigitalWinder):
    """Digital winder with SPI interface"""

    def __init__(
        self,
        potentiometer: Potentiometer,
        spi: Union[SPI, None] = None,
        max_value: int = 128,
        parameters_locked: bool = False,
    ):
        self.__spi = None
        if isinstance(spi, SPI):
            self.__spi = spi
        super().__init__(
            potentiometer=potentiometer,
            max_value=max_value,
            parameters_locked=parameters_locked,
        )

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

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for key, value in self.__dict__.items():
            if '_spi' in key:
                setattr(result, key, value)
            setattr(result, key, deepcopy(value, memo))
        return result
