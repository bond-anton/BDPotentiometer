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
    moves the wiper to the position that produces the requested voltage when one
    exists, and otherwise saturates at the terminal with the closest output.
    The resistance of the load can be set using the property `r_load`.
    The potential at the other end of the load resistor is set using the `v_load`
    property.

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
        return self._v_w_at(self.wiper_position)

    def _v_w_at(self, position: float) -> float:
        """
        Voltage at terminal W for an arbitrary wiper position.

        `v_w` evaluates this for the current position; the setter also needs the
        two terminal voltages to decide where an unreachable target saturates.

        :param position: Wiper position in the range from 0 (B) to 1 (A).
        :return: Voltage at terminal W as float.
        """
        if self.r_load + self.r_w == 0:
            return self.v_load
        r_left = self.r_a + self.r_ab * (1 - position)
        r_right = self.r_b + self.r_ab * position
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
        saturates at the terminal whose actual output is closest to the target
        and a warning is logged; if both terminals are equally close, the
        position is kept and a warning is logged instead. The requested voltage
        is never rejected, so the property does not raise for an unreachable
        target.

        A target exactly equal to `v_load` draws no load current and is solved
        as an unloaded divider. Any other target, including one arbitrarily
        close to `v_load`, is solved with the loaded divider equation.

        When the load resistance `r_load` is zero the load shorts the wiper, the
        output no longer depends on the wiper position, and the wiper is centred
        at 0.5 as the only neutral choice.

        :param voltage: Voltage at the terminal W (float).
        :raises TypeError: If `voltage` is not a real number.
        :raises ValueError: If `voltage` is infinite or `NaN`.
        """
        voltage = float(check_number(voltage))
        self.logger.debug("Setting V(W) to %2.2g V", voltage)
        if self.r_load == 0:
            self.logger.debug("R(Load) is zero, wiper has no effect, centring it")
            self.wiper_position = 0.5
        else:
            self._v_out_gen_solution(voltage)

    def _v_out_eq_v_load(self) -> None:
        """
        Pick the wiper position for which the open-circuit divider gives
        `v_load`.

        `v_load` is reachable when the open-circuit divider voltage at some
        position equals it, which for a linear divider means that `v_load` lies
        between the open-circuit voltages at the two terminals. Otherwise the
        wiper saturates at the terminal whose loaded output is closest to
        `v_load` and a warning is logged. When `v_a == v_b == v_load` every
        position produces the target and the wiper is centred. When
        `v_a == v_b != v_load` no position produces the target at all; the
        wiper is left untouched and a warning is logged.
        """
        self.logger.debug("Load current is zero, V_load = V_w = %s", self.v_load)
        span = self.v_a - self.v_b
        if span == 0:
            if self.v_load == self.v_a:
                self.logger.debug("V_a = V_b = V_load = %s", self.v_load)
                self.logger.debug(
                    "V_w independent of wiper position, setting wiper to the middle."
                )
                self.wiper_position = 0.5
            else:
                self.logger.warning(
                    "V_a = V_b = %s is unreachable for V_load = %s at any wiper "
                    "position, holding position %s",
                    self.v_a,
                    self.v_load,
                    self.wiper_position,
                )
            return
        # Open-circuit divider: (V_a - V_load) / r_left = (V_load - V_b) / r_right.
        # Solving for the B-W resistance avoids the k + 1 denominator, which
        # cancels to zero when the rails differ by a single ulp.
        r_bw = (
            (self.v_load - self.v_b) * (self.r_a + self.r_ab)
            - (self.v_a - self.v_load) * self.r_b
        ) / span
        self.logger.debug("R_bw = %s", r_bw)
        position = r_bw / self.r_ab
        if -1e-12 <= position <= 1.0 + 1e-12:
            self.logger.debug("Setting wiper to %s", position)
            self.wiper_position = clamp(position, 0.0, 1.0)
        else:
            self._saturate(self.v_load)

    def _saturate(self, voltage: float) -> None:
        """
        Move the wiper to the terminal whose output is closest to `voltage`.

        Called when no wiper position reproduces the target. A warning reports
        both terminal voltages; identical terminal voltages leave the position
        untouched because neither terminal is preferable.

        A target outside the output range is assigned by comparing it with the
        terminal voltages, not by subtracting it from both: the differences are
        nearly equal when the target is far outside a narrow range, and the
        comparison would lose the side that the target lies on.
        """
        v_at_b = self._v_w_at(0.0)
        v_at_a = self._v_w_at(1.0)
        if v_at_b == v_at_a:
            self.logger.warning(
                "No wiper position gives V(W) = %s V, both terminals produce "
                "%s V, holding position %s",
                voltage,
                v_at_b,
                self.wiper_position,
            )
            return
        low, high = (v_at_b, v_at_a) if v_at_b < v_at_a else (v_at_a, v_at_b)
        if voltage >= high:
            position = 1.0 if v_at_a > v_at_b else 0.0
        elif voltage <= low:
            position = 1.0 if v_at_a < v_at_b else 0.0
        elif abs(v_at_b - voltage) < abs(v_at_a - voltage):
            position = 0.0
        elif abs(v_at_a - voltage) < abs(v_at_b - voltage):
            position = 1.0
        else:
            self.logger.warning(
                "No wiper position gives V(W) = %s V, both terminals are equally "
                "far, holding position %s",
                voltage,
                self.wiper_position,
            )
            return
        self.logger.warning(
            "No wiper position gives V(W) = %s V, saturating at %s (V(W) = %s V)",
            voltage,
            "A" if position == 1.0 else "B",
            v_at_a if position == 1.0 else v_at_b,
        )
        self.wiper_position = position

    def _v_out_gen_solution(self, voltage: float) -> None:
        """
        Solve the divider equation for the wiper position giving `voltage`.

        The solution is the root of a quadratic in the wiper position, which can
        have two valid positions or none. Two roots are disambiguated by keeping
        the one closest to the current position; a root just outside [0, 1] is
        clamped to the terminal. When no root is usable the wiper saturates at
        the terminal whose output is closest to the target, and an ambiguous
        target leaves the position untouched; both cases log a warning.

        The quadratic is built from resistances normalized by `r_ab`. Normalizing
        keeps every coefficient on the scale of the resistances themselves; the
        unscaled form subtracts terms of order `r_w * r_top`, which cancels the
        root when `r_w` dominates `r_load`.
        """
        v_a = self.v_a
        v_b = self.v_b
        v_load = self.v_load
        if voltage == v_load:
            # Zero load current: the equation degenerates to the open-circuit
            # divider, which is linear in the position.
            self._v_out_eq_v_load()
            return
        # The load branch is the series r_w + r_load to v_load. In normalized
        # units r_b = r_b / r_ab, s = r_left(0) / r_ab, beta = (r_w + r_load) / r_ab.
        r_b = self.r_b / self.r_ab
        s = 1.0 + self.r_a / self.r_ab
        beta = (self.r_w + self.r_load) / self.r_ab
        delta = voltage - v_load
        alpha = 1.0 + self.r_w / self.r_load
        # A2 * x^2 + A1 * x + A0 = 0.
        a2 = delta * alpha
        a1 = -a2 * (s - r_b) + beta * (v_a - v_b)
        a0 = beta * (v_a * r_b + v_b * s - v_load * (s + r_b)) - a2 * (
            beta * (s + r_b) + s * r_b
        )
        self.logger.debug("V_out coefficients: %s, %s, %s", a2, a1, a0)
        d = a1 * a1 - 4 * a2 * a0
        if d < 0:
            roots = []
        else:
            # The textbook formula cancels catastrophically when a1 dominates,
            # so build the well-conditioned root and derive the second one from
            # the product a0 / a2.
            q = -(a1 + m.copysign(1.0, a1) * m.sqrt(d)) / 2
            roots = [0.0] if q == 0 else [q / a2, a0 / q]
        candidates = [
            clamp(root, 0.0, 1.0) for root in roots if -1e-12 <= root <= 1.0 + 1e-12
        ]
        if candidates:
            self.wiper_position = min(
                candidates, key=lambda root: abs(self.wiper_position - root)
            )
            return
        self._saturate(voltage)
