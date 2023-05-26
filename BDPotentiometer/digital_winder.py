""" Module contains basic digital winder class implementation """

from typing import Union

from .__helpers import check_integer, check_positive, check_not_negative, coerce


class DigitalWinder:
    """
    Generic digital winder class.
    Digital winder change position by discrete movement between 0 and `max_value`.
    Default value is provided by `default_value` property, which can be set to None for
    devices with non-volatile memory.
    Property `parameters_locked` is used to disable change of `max_value` and `default_value`
    parameters after object is created, only winder position change is allowed.
    """

    def __init__(self, max_value: int = 128, default_value: Union[int, None] = 64,
                 channel: int = 0, parameters_locked: bool = False) -> None:
        self.__locked: bool = bool(parameters_locked)
        self.__channel: int = check_not_negative(check_integer(channel))
        self.__max_value: int = check_positive(check_integer(max_value))
        self.__default_value: Union[int, None] = None
        self.__value: int = 0
        if default_value is not None:
            self.__default_value = coerce(check_not_negative(check_integer(default_value)),
                                          0, self.max_value)
            self.__value = self.default_value
        self.__value = self._read_value()

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
            if self.__default_value is not None:
                self.__default_value = coerce(self.__default_value, 0, self.max_value)
            self.value = self.__value

    @property
    def default_value(self) -> Union[int, None]:
        """
        Returns default winder position value or None for devices with non-volatile memory.

        :return: Default winder position value or None.
        """
        return self.__default_value

    @default_value.setter
    def default_value(self, default_value: Union[int, None]) -> None:
        if not self.locked:
            if default_value is None:
                self.__default_value = None
            else:
                self.__default_value = coerce(check_not_negative(check_integer(default_value)),
                                              0, self.max_value)

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

    @property
    def value(self) -> int:
        """
        Current winder position.

        :return: Winder position value (int).
        """
        return self.__value

    @value.setter
    def value(self, value: int) -> None:
        value = coerce(check_integer(value), 0, self.max_value)
        data = self._set_value(value)
        self.__value = data
