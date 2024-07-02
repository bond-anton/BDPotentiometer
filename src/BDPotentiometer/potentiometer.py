""" Basic potentiometer device implementation """

import math as m
from .__helpers import clamp, check_number, check_positive, check_not_negative
from .__logger import get_logger


class Potentiometer:

    # pylint: disable=too-many-instance-attributes

    """
    Represents a generic potentiometer with 3 terminals A, B, and W.

    A     ┌─────────────┐     B
     o────┤Potentiometer├─────o
          └──────▲──────┘
           1 <── │ ──> 0
                 o W
    The total resistance of the potentiometer is `r_ab`, the resistance of the wiper is `r_w`,
    the resistance of the A and B terminals is `r_a` and `r_b`, respectively.

    The wiper can move between B and A, changing its position from 0 (terminal B) to 1 (terminal A).
    To calculate the resistance between terminals WA and WB use `r_wa` and `r_wb` methods.
    The inverse functions `r_wa_to_position` and `r_wb_to_position` are also available
    to calculate the wiper position given a known r_wa or r_wb.

    The figure below shows the equivalent wiring diagram for a potentiometer.
             A   ┌─────────┐  ┌─────────┐  ┌─────────┐   B
      (V_A)  o───┤   R_A   ├──┤   POT   ├──┤   R_B   ├───o  (V_B)
                 └─────────┘  └────▲────┘  └─────────┘
                             1 <── │ ──> 0
                                ┌─────┐
                                │     │
                                │ R_W │
                                │     │
                                └─────┘
                                   │
                                   o W (V_W)
                                   │
                                 ┌───┐
                                 │ L │
                        R_load   │ o │
                                 │ a │
                                 │ d │
                                 └───┘
                                   │
                                   o L (V_L)

    The voltage at the A and B terminals of the potentiometer can be controlled
    using the parameters `v_a` and `v_b`.
    To obtain the voltage at the terminal W use method `v_w`.
    The resistance of the load can be set using the property `r_load`.
    The potential at the another end of the load resistor is set using the `v_l` property.

    If we set the resistance `r_a` to a very high value, the potentiometer will turn
    into a rheostat with a floating A terminal.

      A     ┌──────────┐        ┌────────┐  B
       x────┤ Rheostat ├────────┤  R_B   ├──o (V_B)
            └─────▲────┘        └────────┘
            1 <── │ ──> 0
                  o W (V_W)
                  │
                ┌───┐
                │ L │
         R_load │ o │
                │ a │
                │ d │
                └───┘
                  │
                 ─┴─ GND (V_L = 0)

    From the other hand, if the `r_b` and `v_b` are set to zero we can get a simple voltage source.
             A   ┌───────┐       ┌─────────┐     B
      (V_in) o───┤  R_A  ├───────┤   POT   ├─────o────┐
                 └───────┘       └────▲────┘          │
                                1 <── │ ──> 0         │
                                      o W (V_out)    ─┴─ GND (V_B = 0)
                                      │
                                    ┌───┐
                                    │ L │
                           R_load   │ o │
                                    │ a │
                                    │ d │
                                    └───┘
                                      │
                                     ─┴─ GND (V_L = 0)


    To get the position of the wiper given a required V_W use `v_w_to_wiper_position` method.

    """

    def __init__(
        self, r_ab: float = 1.0e5, wiper_position: float = 0.5, **kwargs
    ) -> None:
        self._r_ab: float = check_positive(r_ab)
        self._r_w: float = check_not_negative(kwargs.get("r_w", 0.0))
        self._r_a: float = check_not_negative(kwargs.get("r_a", 0.0))
        self._r_b: float = check_not_negative(kwargs.get("r_b", 0.0))
        self._v_a: float = check_number(kwargs.get("v_a", 0.0))
        self._v_b: float = check_number(kwargs.get("v_b", 0.0))
        self._v_load: float = check_number(kwargs.get("v_load", 0.0))
        self._r_load: float = check_not_negative(kwargs.get("r_load", 1.0e10))
        self._wiper_position: float = float(clamp(wiper_position, 0, 1))
        self.logger = get_logger(
            kwargs.get("label", "Potentiometer"), kwargs.get("log_level", None)
        )

    @property
    def r_ab(self) -> float:
        """
        Total resistance of the potentiometer between A and B terminals.

        :return: Total resistance as float.
        """
        return self._r_ab

    @r_ab.setter
    def r_ab(self, resistance: float) -> None:
        self._r_ab = float(check_positive(resistance))
        self.logger.debug("R(AB) set to %2.2g Ohm", self._r_ab)

    @property
    def r_w(self) -> float:
        """
        Wiper terminal resistance.

        :return: Wiper resistance as float.
        """
        return self._r_w

    @r_w.setter
    def r_w(self, resistance: float) -> None:
        self._r_w = float(check_not_negative(resistance))
        self.logger.debug("R(W) set to %2.2g Ohm", self._r_w)

    @property
    def r_a(self) -> float:
        """Resistance of terminal A"""
        return self._r_a

    @r_a.setter
    def r_a(self, resistance: float) -> None:
        self._r_a = float(check_not_negative(resistance))
        self.logger.debug("R(A) set to %2.2g Ohm", self._r_a)

    @property
    def r_b(self) -> float:
        """Resistance of terminal B"""
        return self._r_b

    @r_b.setter
    def r_b(self, resistance: float) -> None:
        self._r_b = float(check_not_negative(resistance))
        self.logger.debug("R(B) set to %2.2g Ohm", self._r_b)

    @property
    def r_load(self) -> float:
        """Resistive load R_load value"""
        return self._r_load

    @r_load.setter
    def r_load(self, r_load: float) -> None:
        self._r_load = float(check_not_negative(r_load))
        self.logger.debug("R(Load) set to %2.2g Ohm", self._r_load)

    @property
    def v_a(self) -> float:
        """
        Voltage at terminal A.

        :return: v_a (float).
        """
        return self._v_a

    @v_a.setter
    def v_a(self, voltage: float) -> None:
        self._v_a = float(check_number(voltage))
        self.logger.debug("V(A) set to %2.2g V", self._v_a)

    @property
    def v_b(self) -> float:
        """
        Voltage at terminal B.

        :return: v_b (float).
        """
        return self._v_b

    @v_b.setter
    def v_b(self, voltage: float) -> None:
        self._v_b = float(check_number(voltage))
        self.logger.debug("V(B) set to %2.2g V", self._v_b)

    @property
    def v_load(self) -> float:
        """
        Voltage at load resistance.

        :return: v_load (float).
        """
        return self._v_load

    @v_load.setter
    def v_load(self, voltage: float) -> None:
        self._v_load = float(check_number(voltage))
        self.logger.debug("V(Load) set to %2.2g V", self._v_load)

    @property
    def wiper_position(self) -> float:
        """
        Wiper position in the range from 0 (B) to 1 (A)
        :return: wiper_position (float)
        """
        return self._wiper_position

    @wiper_position.setter
    def wiper_position(self, position: float) -> None:
        self._wiper_position = float(clamp(position, 0, 1))
        self.logger.debug("Wiper position set to %2.2f", self._wiper_position)

    @property
    def r_wa(self) -> float:
        """
        The resistance between terminals A and W for the current wiper position.
        """
        return self.r_w + self.r_a + (1 - self.wiper_position) * self.r_ab

    @r_wa.setter
    def r_wa(self, resistance: float) -> None:
        """
        Calculate wiper position as a fraction of its movement in the range from 0 (terminal B)
        to 1 (terminal A) given the resistance between terminals A and W.

        :param resistance: Resistance between terminals A and W (float)
        :return: Wiper position in the range [0: 1] (float).
        """
        resistance = clamp(
            resistance, self.r_w + self.r_a, self.r_w + self.r_a + self.r_ab
        )
        self.logger.debug("Setting R(WA) to %2.2g Ohm", resistance)
        self.wiper_position = 1 - (resistance - self.r_w - self.r_a) / self.r_ab

    @property
    def r_wb(self) -> float:
        """
        The resistance between terminals B and W for the current wiper position.
        """
        return self.r_w + self.r_b + self.wiper_position * self.r_ab

    @r_wb.setter
    def r_wb(self, resistance: float) -> None:
        """
        Calculate wiper position as a fraction of its movement in the range from 0 (terminal B)
        to 1 (terminal A) given the resistance between terminals B and W.

        :param resistance: Resistance between terminals B and W (float)
        :return: Wiper position in the range [0: 1] (float).
        """
        resistance = clamp(resistance, self.r_w, self.r_w + self.r_ab)
        self.logger.debug("Setting R(WB) to %2.2g Ohm", resistance)
        self.wiper_position = (resistance - self.r_w - self.r_b) / self.r_ab

    @property
    def v_w(self) -> float:
        """
        The voltage at the terminal W for the current wiper position.
        """
        if self.r_load + self.r_w == 0:
            return self.v_load
        r_left = self.r_a + self.r_ab * (1 - self.wiper_position)
        r_right = self.r_b + self.r_ab * self.wiper_position
        r_bot = self.r_w + self.r_load
        v_bot = (
            self.v_a * r_bot * r_right
            + self.v_b * r_bot * r_left
            + self.v_load * r_left * r_right
        ) / (r_bot * r_right + r_bot * r_left + r_left * r_right)

        return v_bot / (self.r_load + self.r_w) * self.r_load

    @v_w.setter
    def v_w(self, voltage: float) -> None:
        """
        Calculates wiper position given the voltage at the terminal W.

        :param voltage: Voltage at the terminal W (float).
        """
        if not isinstance(voltage, (float, int)):
            raise TypeError(f"Float value expected, got {voltage} ({type(voltage)}).")
        self.logger.debug("Setting V(W) to %2.2g V", voltage)
        if self.r_load != 0:
            if voltage == self.v_load:
                self._v_out_eq_v_load()
            else:
                self._v_out_gen_solution(voltage)
        else:
            self.logger.debug("R(L) is zero, setting wiper to the middle")
            self.wiper_position = 0.5

    def _v_out_eq_v_load(self):
        self.logger.debug("Load current is zero, V_load = V_w = %s", self.v_load)
        if self.v_b == self.v_a == self.v_load:
            self.logger.debug("V_a = V_b = V_load = %s", self.v_load)
            self.logger.debug(
                "V_w independent of wiper position, setting wiper to the middle."
            )
            self.wiper_position = 0.5
        elif self.v_b == self.v_a:
            self.logger.debug("V_a = V_b = %s", self.v_a)
            r_bw = (self.r_a + self.r_ab - self.r_b) / 2
            self.logger.debug("R_bw = %s", r_bw)
            r_bw = clamp(r_bw, 0.0, self.r_ab)
            self.logger.debug("Setting wiper to %s", r_bw / self.r_ab)
            self.wiper_position = r_bw / self.r_ab
        elif self.v_b == self.v_load:
            self.logger.debug("V_a != V_b = V_load = %s", self.v_load)
            self.logger.debug("Setting wiper to 0")
            self.wiper_position = 0
        elif self.v_a == self.v_load:
            self.logger.debug("V_b != V_a = V_load = %s", self.v_load)
            self.logger.debug("Setting wiper to 1")
            self.wiper_position = 1
        else:
            k = (self.v_a - self.v_load) / (self.v_load - self.v_b)
            r_bw = (self.r_a + self.r_ab - k * self.r_b) / (k + 1)
            self.logger.debug("R_bw = %s", r_bw)
            r_bw = clamp(r_bw, 0.0, self.r_ab)
            self.logger.debug("Setting wiper to %s", r_bw / self.r_ab)
            self.wiper_position = r_bw / self.r_ab

    def _v_out_gen_solution(self, voltage: float) -> None:
        i_l: float = (self.v_load - voltage) / self.r_load
        v_bot: float = voltage - i_l * self.r_w
        self.logger.debug("V_bot = %s, V_b = %s, V_a = %s", v_bot, self.v_b, self.v_a)
        if v_bot <= self.v_b < self.v_a or v_bot >= self.v_b > self.v_a:
            self.logger.debug("Coerce to V_b, setting wiper to 0")
            self.wiper_position = 0
        elif v_bot <= self.v_a < self.v_b or v_bot >= self.v_a > self.v_b:
            self.logger.debug("Coerce to V_a, setting wiper to 1")
            self.wiper_position = 1
        else:
            r_top: float = self.r_ab + self.r_a + self.r_b
            r_tl: float = self.r_ab + self.r_a
            v_top: float = self.v_b - self.v_a
            b: float = self.r_b - r_tl + v_top / i_l
            c: float = (
                v_bot * r_top / i_l
                - self.r_b * r_tl
                - (self.v_a * self.r_b + self.v_b * r_tl) / i_l
            )
            d = b * b - 4 * c
            if d >= 0:
                sol = []
                x1 = (-b + m.sqrt(d)) / (2 * self.r_ab)
                x2 = (-b - m.sqrt(d)) / (2 * self.r_ab)
                if 0 <= x1 <= 1:
                    sol.append(x1)
                if 0 <= x2 <= 1:
                    sol.append(x2)
                if len(sol) == 2:
                    if abs(self.wiper_position - sol[0]) < abs(
                        self.wiper_position - sol[1]
                    ):
                        self.wiper_position = sol[0]
                    else:
                        self.wiper_position = sol[1]
                elif len(sol) == 1:
                    self.wiper_position = sol[0]
            else:
                self.logger.debug("No solution wiper holds position")
