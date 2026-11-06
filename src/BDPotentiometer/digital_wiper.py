"""Module contains basic digital wiper class implementation"""

from copy import deepcopy
from typing import Union, cast

from .__helpers import check_integer, check_not_negative, check_positive, clamp
from .__logger import get_logger
from .potentiometer import Potentiometer
from .transport.base import SpiTransport, is_spi_transport


class DigitalWiper:
    """
    Generic digital wiper class.
    Digital wiper change position by discrete movement between 0 and `max_value`.
    """

    def __init__(
        self,
        potentiometer: Potentiometer,
        max_value: int = 128,
        invert: bool = False,
        **kwargs,
    ) -> None:
        if isinstance(potentiometer, Potentiometer):
            self.__potentiometer: Potentiometer = potentiometer
        else:
            raise TypeError(
                f"Expected an instance of Potentiometer class, got {type(potentiometer)}"
            )
        self.__channel: int = 0
        self.__invert: bool = bool(invert)
        self.__max_value: int = check_integer(check_positive(max_value))
        self.__value: int = 0
        self.logger = get_logger(
            kwargs.get("label", "Digital Wiper"),
            kwargs.get("log_level"),
        )
        self.read()

    @property
    def potentiometer(self) -> Potentiometer:
        """
        Access Potentiometer instance.
        :return: Potentiometer
        """
        return self.__potentiometer

    @property
    def channel(self) -> int:
        """Wiper channel number"""
        return self.__channel

    @channel.setter
    def channel(self, channel_id: int):
        self.__channel = check_integer(check_not_negative(channel_id))

    @property
    def invert(self) -> bool:
        """Wiper inversion"""
        return self.__invert

    @invert.setter
    def invert(self, invert: bool) -> None:
        self.__invert = bool(invert)
        self.logger.debug("Set wiper INVERT to %s", self.__invert)

    @property
    def min_value(self) -> int:
        """
        Returns minimal wiper position, which is always zero.
        :return: Always return 0.
        """
        return 0

    @property
    def max_value(self) -> int:
        """
        Returns device max wiper position value.

        :return: Max wiper position value as int.
        """
        return self.__max_value

    @max_value.setter
    def max_value(self, max_value: int) -> None:
        self.__max_value = check_integer(check_positive(max_value))
        self.logger.debug("Set max value to %d", self.__max_value)
        self.value = self.__value

    def _read_value(self) -> int:
        """
        Read value of wiper position.

        :return: Wiper position value (int).
        """
        return int(round(self.potentiometer.wiper_position * self.max_value))

    def _set_value(self, value: int) -> int:
        """
        Calculate proper wiper position value.
        """
        value = int(round(clamp(value, 0, self.max_value)))
        value = self.max_value - value if self.invert else value
        self.logger.debug("Setting value to %d", value)
        self.potentiometer.wiper_position = value / self.max_value
        return value

    def read(self) -> None:
        """
        Read wiper position into value property.
        """
        value = self._read_value()
        if self.__value != value:
            self.__value = value
            self.logger.debug("Wiper position updated to %d", value)

    @property
    def value(self) -> int:
        """
        Current wiper position.

        :return: Wiper position value (int).
        """
        self.read()
        if self.invert:
            return self.max_value - self.__value
        return self.__value

    @value.setter
    def value(self, value: int) -> None:
        """
        Set wiper position value.
        """
        self.__value = self._set_value(value)

    @property
    def value_relative(self) -> float:
        """
        Relative wiper position value in the range 0..1.
        :return: Relative wiper position (float)
        """
        return self.value / self.max_value

    @value_relative.setter
    def value_relative(self, value: float) -> None:
        value = clamp(value, 0, 1)
        value_int = int(round(value * self.max_value))
        self.value = value_int

    @property
    def r_wb(self) -> float:
        """
        Calculates resistance between terminals B and W.

        :return: Resistance between terminals B and W (float).
        """
        return self.potentiometer.r_wb

    @r_wb.setter
    def r_wb(self, resistance: float) -> None:
        self.potentiometer.r_wb = resistance
        self.read()

    @property
    def r_wa(self) -> float:
        """
        Calculates resistance between terminals A and W.

        :return: Resistance between terminals A and W (float).
        """
        return self.potentiometer.r_wa

    @r_wa.setter
    def r_wa(self, resistance: float) -> None:
        self.potentiometer.r_wa = resistance
        self.read()

    @property
    def v_w(self) -> float:
        """Voltage at wiper terminal"""
        return self.potentiometer.v_w

    @v_w.setter
    def v_w(self, voltage: float) -> None:
        self.potentiometer.v_w = voltage
        self.read()

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for key, value in self.__dict__.items():
            setattr(result, key, deepcopy(value, memo))
        return result


class SpiDigitalWiper(DigitalWiper):
    """Digital wiper with SPI interface"""

    def __init__(
        self,
        potentiometer: Potentiometer,
        spi: Union[SpiTransport, None] = None,
        max_value: int = 128,
        invert: bool = False,
        transport: Union[SpiTransport, None] = None,
        **kwargs,
    ):
        self._transport = self._resolve_transport(
            transport if transport is not None else spi
        )
        super().__init__(
            potentiometer=potentiometer, max_value=max_value, invert=invert, **kwargs
        )

    @staticmethod
    def _resolve_transport(value: object) -> Union[SpiTransport, None]:
        if value is None:
            return None
        if is_spi_transport(value):
            return cast(SpiTransport, value)
        raise TypeError(f"Expected an SPI transport with transfer(), got {type(value)}")

    def _require_transport(self) -> SpiTransport:
        if self._transport is None:
            raise ConnectionError("SPI interface not set")
        return self._transport

    @property
    def transport(self) -> Union[SpiTransport, None]:
        """Canonical SPI transport; ``spi`` is a compatibility accessor."""
        return self._transport

    @transport.setter
    def transport(self, value: Union[SpiTransport, None]) -> None:
        self._transport = self._resolve_transport(value)
        self.logger.debug("Transport set to %s", self._transport)

    @property
    def spi(self) -> Union[SpiTransport, None]:
        """
        Compatibility accessor for the SPI interface; ``transport`` is canonical.
        :return: SPI interface (raw gpiozero SPI if wrapped, else the transport)
        """
        if self._transport is None:
            return None
        return getattr(self._transport, "raw", self._transport)

    @spi.setter
    def spi(self, spi: Union[SpiTransport, None]) -> None:
        self.transport = spi if spi is None or is_spi_transport(spi) else None

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for key, value in self.__dict__.items():
            if key == "_transport":
                setattr(result, key, value)
                continue
            setattr(result, key, deepcopy(value, memo))
        return result
