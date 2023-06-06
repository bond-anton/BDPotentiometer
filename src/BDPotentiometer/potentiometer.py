""" Basic potentiometer device implementation """

import math as m

from .__helpers import coerce, check_number, check_positive, check_not_negative


class Potentiometer:
    """
    Represents a general potentiometer with 3 terminals A, B, and W.

    A     ┌─────────────┐     B
     o────┤Potentiometer├─────o
          └──────▲──────┘
           1 <── │ ──> 0
                 o W
    Total resistance is `r_ab`, wiper resistance is `r_w`
    If device is `locked` parameters `r_ab` and `r_w` are read-only.

    Wiper moves from B to A changing position from 0 to 1.
    Resistance between terminals WA and WB can be calculated using `r_wa` and `r_wb` functions.
    Reverse functions `r_wa_to_position` and `r_wb_to_position` for calculation of wiper position
    given r_wa or r_wb are also available.

    Parameter `rheostat` turns potentiometer to rheostat with terminal A floating not connected,
    and two terminals B and W available

    A     ┌─────────────┐     B
     x────┤   Rheostat  ├─────o
          └──────▲──────┘
           1 <── │ ──> 0
                 o W

    Potentiometer can be connected like shown bin the sketch below
                 ┌────────┐ A     ┌──────────┐     B
      (V_in) o───┤ R_lim  ├──o────┤   POT    ├─────o────┐
                 └────────┘       └─────▲────┘          │
                                  1 <── │ ──> 0         │
                                        o W (V_out)    ─┴─ GND
                                        │
                                      ┌───┐
                                      │ L │
                             R_load   │ o │
                                      │ a │
                                      │ d │
                                      └───┘
                                        │
                                       ─┴─ GND

    Rheostat possible connection circuit is shown below.

      A     ┌──────────┐     B   ┌────────┐
       x────┤ Rheostat ├─────o───┤ R_lim  ├──o (V_in)
            └─────▲────┘         └────────┘
            1 <── │ ──> 0
                  o W (V_out)
                  │
                ┌───┐
                │ L │
         R_load │ o │
                │ a │
                │ d │
                └───┘
                  │
                 ─┴─ GND

    R_lim is current limiting resistor, and R_load is resistive load.
    Parameters `r_lim` and `r_load` can be set using properties with same name.
    Default value for R_lim and R_load is zero.
    Input voltage (V_in) is set using property `voltage_in`.
    Output voltage (V_out) can be calculated using method `voltage_out`.

    Wiper position given required V_out can be calculated
    using function `voltage_out_to_wiper_position`.

    """

    # pylint: disable=too-many-instance-attributes

    def __init__(
        self, r_ab: float, r_w: float = 0, rheostat: bool = False, locked: bool = False
    ) -> None:
        self.__locked: bool = bool(locked)
        self.__r_ab: float = check_positive(r_ab)
        self.__r_w: float = check_not_negative(r_w)
        self.__rheostat: bool = bool(rheostat)

        self.__r_lim: float = 0
        self.__r_load: float = 0
        self.__voltage_in: float = 0

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
        Wiper terminal resistance.

        :return: Wiper resistance as float.
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

    @property
    def rheostat(self) -> bool:
        """
        Check if device is configured as a rheostat (terminal A is floating and not available
        for connection).

        :return: True if device is a rheostat, otherwise False.
        """
        return self.__rheostat

    @property
    def r_lim(self) -> float:
        """R_lim current limiting resistor"""
        return self.__r_lim

    @r_lim.setter
    def r_lim(self, r_lim: float) -> None:
        self.__r_lim = check_not_negative(r_lim)

    @property
    def r_load(self) -> float:
        """Resistive load R_load value"""
        return self.__r_load

    @r_load.setter
    def r_load(self, r_load: float) -> None:
        self.__r_load = check_not_negative(r_load)

    @property
    def voltage_in(self) -> float:
        """
        Input voltage of the device.

        :return: voltage_in (float).
        """
        return self.__voltage_in

    @voltage_in.setter
    def voltage_in(self, voltage: float) -> None:
        self.__voltage_in = check_number(voltage)

    def r_wa(self, wiper_position: float) -> float:
        """
        Calculates resistance between terminals A and W given the wiper position
        as a fraction of its movement in the range from 0 (terminal B) to 1 (terminal A).

        :param wiper_position: Wiper position in the range [0: 1]
        :return: Resistance between terminals A and W (float).
        """
        wiper_position = coerce(wiper_position, 0, 1)
        return self.r_w + (1 - wiper_position) * self.r_ab

    def r_wb(self, wiper_position: float) -> float:
        """
        Calculates resistance between terminals B and W given the wiper position
        as a fraction of its movement in the range from 0 (terminal B) to 1 (terminal A).

        :param wiper_position: Wiper position in the range [0: 1]
        :return: Resistance between terminals B and W (float).
        """
        wiper_position = coerce(wiper_position, 0, 1)
        return self.r_w + wiper_position * self.r_ab

    def r_wa_to_position(self, r_wa: float) -> float:
        """
        Calculate wiper position as a fraction of its movement in the range from 0 (terminal B)
        to 1 (terminal A) given the resistance between terminals A and W.

        :param r_wa: Resistance between terminals A and W (float)
        :return: Wiper position in the range [0: 1] (float).
        """
        r_wa = coerce(r_wa, self.r_w, self.r_w + self.r_ab)
        return 1 - (r_wa - self.r_w) / self.r_ab

    def r_wb_to_position(self, r_wb: float) -> float:
        """
        Calculate wiper position as a fraction of its movement in the range from 0 (terminal B)
        to 1 (terminal A) given the resistance between terminals B and W.

        :param r_wb: Resistance between terminals B and W (float)
        :return: Wiper position in the range [0: 1] (float).
        """
        r_wb = coerce(r_wb, self.r_w, self.r_w + self.r_ab)
        return (r_wb - self.r_w) / self.r_ab

    def voltage_out(self, wiper_position: float) -> float:
        """
        Calculates output voltage for given wiper position.

        :param wiper_position: Wiper position as float number between 0 and 1.
        :return: Voltage (float).
        """
        if self.rheostat:
            r_total = self.r_load + self.r_lim + self.r_wb(wiper_position)
            return self.voltage_in * self.r_load / r_total
        r_wb = self.r_ab * wiper_position
        r_wa = self.r_ab * (1 - wiper_position)
        r_bot = r_wb * (self.r_w + self.r_load) / (r_wb + self.r_w + self.r_load)
        v_bot = self.voltage_in * r_bot / (r_bot + self.r_lim + r_wa)
        return v_bot / (self.r_load + self.r_w) * self.r_load

    def voltage_out_to_wiper_position(self, voltage_out: float) -> float:
        """
        Calculates wiper position given output voltage.

        :param voltage_out: Output voltage (float).
        :return: Wiper position as float number between 0 and 1.
        """
        if voltage_out == 0 or self.r_load == 0 or self.voltage_in == 0:
            return 0
        if (self.voltage_in / voltage_out) / abs(self.voltage_in / voltage_out) < 0:
            return 0

        if self.rheostat:
            r_total = self.voltage_in * self.r_load / voltage_out
            r_wb = r_total - self.r_load - self.r_lim
            return self.r_wb_to_position(r_wb)

        v_bot = voltage_out * (self.r_w + self.r_load) / self.r_load
        r_lim = self.r_ab + self.r_lim
        r_l = self.r_w + self.r_load
        quad_b = self.voltage_in / v_bot * r_l - r_lim
        quad_ac = -r_lim * r_l
        quad_d = quad_b**2 - 4 * quad_ac
        r_wb = (-quad_b + m.sqrt(quad_d)) / 2
        return r_wb / self.r_ab
