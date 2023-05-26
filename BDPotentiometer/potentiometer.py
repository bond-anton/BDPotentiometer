""" Basic potentiometer device implementation """

from .__helpers import coerce, check_positive, check_not_negative


class Potentiometer:
    """
    Represents a general potentiometer with 3 terminals A, B, and W.

    A     ┌──────────┐     B
     o────┤          ├─────o
          └─────▲────┘
          1 <── │ ──> 0
                o W
    Total resistance is `r_ab`, winder resistance is `r_w`
    """

    def __init__(self, r_ab: float, r_w: float = 0, locked: bool = False) -> None:
        self.__locked: bool = bool(locked)
        self.__r_ab: float = check_positive(r_ab)
        self.__r_w: float = check_not_negative(r_w)

    @property
    def r_ab(self) -> float:
        """
        Total resistance of the potentiometer between A and B terminals.

        :return: Total resistance as float.
        """
        return self.__r_ab

    @r_ab.setter
    def r_ab(self, resistance: float) -> None:
        if not self.locked:
            self.__r_ab = check_positive(resistance)

    @property
    def r_w(self) -> float:
        """
        Winder terminal resistance.

        :return: winder resistance as float.
        """
        return self.__r_w

    @r_w.setter
    def r_w(self, r_w: float) -> None:
        if not self.locked:
            self.__r_w = float(check_not_negative(r_w))

    @property
    def locked(self) -> bool:
        """
        Check if parameters of the potentiometer are locked.

        :return: True if locked and False otherwise
        """
        return self.__locked

    def r_wa(self, winder_position: float) -> float:
        """
        Calculates resistance between terminals A and W given the winder position
        as a fraction of its movement in the range from 0 (terminal B) to 1 (terminal A).

        :param winder_position: Winder position in the range [0: 1]
        :return: Resistance between terminals A and W (float).
        """
        winder_position = coerce(winder_position, 0, 1)
        return self.r_w + (1 - winder_position) * self.r_ab

    def r_wb(self, winder_position: float) -> float:
        """
        Calculates resistance between terminals B and W given the winder position
        as a fraction of its movement in the range from 0 (terminal B) to 1 (terminal A).

        :param winder_position: Winder position in the range [0: 1]
        :return: Resistance between terminals B and W (float).
        """
        winder_position = coerce(winder_position, 0, 1)
        return self.r_w + winder_position * self.r_ab

    def r_wa_to_position(self, r_wa: float) -> float:
        """
        Calculate winder position as a fraction of its movement in the range from 0 (terminal B)
        to 1 (terminal A) given the resistance between terminals A and W.

        :param r_wa: Resistance between terminals A and W (float)
        :return: Winder position in the range [0: 1] (float).
        """
        r_wa = coerce(r_wa, self.r_w, self.r_w + self.r_ab)
        return 1 - (r_wa - self.r_w) / self.r_ab

    def r_wb_to_position(self, r_wb: float) -> float:
        """
        Calculate winder position as a fraction of its movement in the range from 0 (terminal B)
        to 1 (terminal A) given the resistance between terminals B and W.

        :param r_wb: Resistance between terminals B and W (float)
        :return: Winder position in the range [0: 1] (float).
        """
        r_wb = coerce(r_wb, self.r_w, self.r_w + self.r_ab)
        return (r_wb - self.r_w) / self.r_ab
