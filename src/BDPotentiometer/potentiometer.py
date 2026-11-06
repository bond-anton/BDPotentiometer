"""Basic potentiometer device implementation"""

import math as m

from .__helpers import check_not_negative, check_number, check_positive, clamp
from .__logger import get_logger


class Potentiometer:
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
    The property `wiper_position` holds that position. The resistances between terminals
    WA and WB are available as the `r_wa` and `r_wb` properties; assigning to either of them
    moves the wiper to the position that produces the requested resistance.

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
    To obtain the voltage at the terminal W read the `v_w` property; assigning to it
    moves the wiper to the position that produces the requested voltage.
    The resistance of the load can be set using the property `r_load`.
    The potential at the another end of the load resistor is set using the `v_load` property.

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


    To get the position of the wiper given a required V_W assign the voltage to `v_w`.

    """

    def __init__(
        self, r_ab: float = 1.0e5, wiper_position: float = 0.5, **kwargs
    ) -> None:
        """
        Initialize the potentiometer model.

        :param r_ab: Total resistance between terminals A and B in Ohm (float).
            Must be positive, otherwise `ValueError` is raised.
        :param wiper_position: Initial wiper position in the range [0, 1], where
            0 is terminal B and 1 is terminal A. Clamped to that range (float).
        :param kwargs: Optional model parameters: `r_w`, `r_a`, `r_b` (resistances
            in Ohm, default 0), `v_a`, `v_b`, `v_load` (voltages in V, default 0),
            `r_load` (load resistance in Ohm, default 1e10), `label` (logger name,
            default "Potentiometer"), and `log_level` (logger level).
        :raises TypeError: If a numeric parameter is not a real number (bool
            included).
        :raises ValueError: If `r_ab` is not positive, if `r_w`, `r_a`, `r_b`, or
            `r_load` is negative, or if a voltage is infinite or `NaN`.
        """
        self._r_ab: float = float(check_positive(r_ab))
        self._r_w: float = float(check_not_negative(kwargs.get("r_w", 0.0)))
        self._r_a: float = float(check_not_negative(kwargs.get("r_a", 0.0)))
        self._r_b: float = float(check_not_negative(kwargs.get("r_b", 0.0)))
        self._v_a: float = float(check_number(kwargs.get("v_a", 0.0)))
        self._v_b: float = float(check_number(kwargs.get("v_b", 0.0)))
        self._v_load: float = float(check_number(kwargs.get("v_load", 0.0)))
        self._r_load: float = float(check_not_negative(kwargs.get("r_load", 1.0e10)))
        self._wiper_position: float = float(clamp(wiper_position, 0, 1))
        self.logger = get_logger(
            kwargs.get("label", "Potentiometer"), kwargs.get("log_level")
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
        """Set the total resistance between terminals A and B in Ohm."""
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
        """Set the wiper terminal resistance in Ohm."""
        self._r_w = float(check_not_negative(resistance))
        self.logger.debug("R(W) set to %2.2g Ohm", self._r_w)

    @property
    def r_a(self) -> float:
        """Resistance of terminal A"""
        return self._r_a

    @r_a.setter
    def r_a(self, resistance: float) -> None:
        """Set the resistance of terminal A in Ohm."""
        self._r_a = float(check_not_negative(resistance))
        self.logger.debug("R(A) set to %2.2g Ohm", self._r_a)

    @property
    def r_b(self) -> float:
        """Resistance of terminal B"""
        return self._r_b

    @r_b.setter
    def r_b(self, resistance: float) -> None:
        """Set the resistance of terminal B in Ohm."""
        self._r_b = float(check_not_negative(resistance))
        self.logger.debug("R(B) set to %2.2g Ohm", self._r_b)

    @property
    def r_load(self) -> float:
        """Resistive load R_load value"""
        return self._r_load

    @r_load.setter
    def r_load(self, r_load: float) -> None:
        """Set the load resistance in Ohm."""
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
        """Set the voltage at terminal A in V."""
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
        """Set the voltage at terminal B in V."""
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
        """Set the voltage at the far end of the load in V."""
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
        """Set the wiper position, clamped to the range from 0 (B) to 1 (A)."""
        self._wiper_position = float(clamp(position, 0, 1))
        self.logger.debug("Wiper position set to %2.2f", self._wiper_position)

    @property
    def r_wa(self) -> float:
        """
        The resistance between terminals A and W for the current wiper position.

        :return: A-W resistance as float.
        """
        return self.r_w + self.r_a + (1 - self.wiper_position) * self.r_ab

    @r_wa.setter
    def r_wa(self, resistance: float) -> None:
        """
        Move the wiper to the position that gives the requested A-W resistance.

        The requested resistance is clamped to the interval
        [`r_w` + `r_a`, `r_w` + `r_a` + `r_ab`] before the position is computed.

        :param resistance: Resistance between terminals A and W (float)
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

        :return: B-W resistance as float.
        """
        return self.r_w + self.r_b + self.wiper_position * self.r_ab

    @r_wb.setter
    def r_wb(self, resistance: float) -> None:
        """
        Move the wiper to the position that gives the requested B-W resistance.

        The requested resistance is clamped to the interval
        [`r_w` + `r_b`, `r_w` + `r_b` + `r_ab`] before the position is computed.

        :param resistance: Resistance between terminals B and W (float)
        """
        resistance = clamp(
            resistance, self.r_w + self.r_b, self.r_w + self.r_b + self.r_ab
        )
        self.logger.debug("Setting R(WB) to %2.2g Ohm", resistance)
        self.wiper_position = (resistance - self.r_w - self.r_b) / self.r_ab

    @property
    def v_w(self) -> float:
        """
        The voltage at the terminal W for the current wiper position.

        The wiper terminal resistance `r_w` is part of the divider, so the wiper
        voltage contains the `v_load * r_w` term. When `r_w` is zero the result
        reduces to the divider voltage at the bottom of the wiper.

        :return: Voltage at terminal W as float.
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

        return (v_bot * self.r_load + self.v_load * self.r_w) / (self.r_load + self.r_w)

    @v_w.setter
    def v_w(self, voltage: float) -> None:
        """
        Move the wiper to the position that gives the requested W voltage.

        When no wiper position can produce the requested voltage, the wiper
        saturates at the terminal the target points at; if even that is
        ambiguous the position is kept and a warning is logged. The requested
        voltage is clamped by the divider, so the property does not raise for
        an unreachable target.

        A target within `rel_tol=1e-9` and `abs_tol=1e-12` of `v_load` is
        solved as an unloaded divider, because the load current vanishes and
        the general solution divides by it.

        When the load resistance `r_load` is zero the load shorts the wiper, the
        output no longer depends on the wiper position, and the wiper is centred
        at 0.5 as the only neutral choice.

        :param voltage: Voltage at the terminal W (float).
        :raises TypeError: If `voltage` is not a real number.
        :raises ValueError: If `voltage` is infinite or `NaN`.
        """
        voltage = float(check_number(voltage))
        self.logger.debug("Setting V(W) to %2.2g V", voltage)
        if self.r_load != 0:
            if m.isclose(voltage, self.v_load, rel_tol=1e-9, abs_tol=1e-12):
                self._v_out_eq_v_load()
            else:
                self._v_out_gen_solution(voltage)
        else:
            self.logger.debug("R(Load) is zero, wiper has no effect, centring it")
            self.wiper_position = 0.5

    def _v_out_eq_v_load(self):
        """
        Pick the wiper position that keeps V(W) equal to `v_load`.

        With no load current the wiper voltage follows the unloaded divider, so
        `v_load` is reachable only inside the rail span; a target outside it is
        clamped to the nearest terminal. When `v_a == v_b == v_load` every
        position produces the target and the wiper is centred. When
        `v_a == v_b != v_load` no position produces the target at all; the
        wiper is left untouched and a warning is logged.
        """
        self.logger.debug("Load current is zero, V_load = V_w = %s", self.v_load)
        if self.v_b == self.v_a == self.v_load:
            self.logger.debug("V_a = V_b = V_load = %s", self.v_load)
            self.logger.debug(
                "V_w independent of wiper position, setting wiper to the middle."
            )
            self.wiper_position = 0.5
        elif self.v_b == self.v_a:
            self.logger.warning(
                "V_a = V_b = %s is unreachable for V_load = %s at any wiper "
                "position, holding position %s",
                self.v_a,
                self.v_load,
                self.wiper_position,
            )
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
        """
        Solve the divider equation for the wiper position giving `voltage`.

        The solution is the root of a quadratic in the wiper position, which can
        have two valid positions or none. Two roots are disambiguated by keeping
        the one closest to the current position; a root just outside [0, 1] is
        clamped to the terminal. When no root is usable the wiper saturates at
        the terminal the target points at, and a target that cannot be reached
        at all leaves the position untouched with a warning.
        """
        i_l: float = (self.v_load - voltage) / self.r_load
        v_bot: float = voltage - i_l * self.r_w
        self.logger.debug("V_bot = %s, V_b = %s, V_a = %s", v_bot, self.v_b, self.v_a)
        r_tl: float = self.r_ab + self.r_a
        r_top: float = self.r_ab + self.r_a + self.r_b
        v_top: float = self.v_b - self.v_a
        b: float = self.r_b - r_tl + v_top / i_l
        c: float = (
            v_bot * r_top / i_l
            - self.r_b * r_tl
            - (self.v_a * self.r_b + self.v_b * r_tl) / i_l
        )
        # The monic quadratic is x^2 + (b / r_ab) * x + c / r_ab^2 = 0. The
        # textbook formula cancels catastrophically when b dominates, so build
        # the well-conditioned root and derive the second one from the product.
        d = b * b - 4 * c
        candidates = []
        if d >= 0:
            q = -(b + m.copysign(1.0, b) * m.sqrt(d)) / (2 * self.r_ab)
            if q == 0:
                roots = [0.0] if c == 0 else []
            else:
                roots = [q, c / (self.r_ab * self.r_ab * q)]
            candidates = [
                clamp(root, 0.0, 1.0) for root in roots if -1e-12 <= root <= 1.0 + 1e-12
            ]
        if candidates:
            self.wiper_position = min(
                candidates, key=lambda root: abs(self.wiper_position - root)
            )
            return
        if v_bot <= self.v_b < self.v_a or v_bot >= self.v_b > self.v_a:
            self.logger.debug("Coerce to V_b, setting wiper to 0")
            self.wiper_position = 0
        elif v_bot <= self.v_a < self.v_b or v_bot >= self.v_a > self.v_b:
            self.logger.debug("Coerce to V_a, setting wiper to 1")
            self.wiper_position = 1
        else:
            self.logger.warning(
                "No wiper position gives V(W) = %s V, wiper holds position", voltage
            )
