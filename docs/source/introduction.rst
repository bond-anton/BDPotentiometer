Introduction
============

**BDPotentiometer** is a python module for easy control of multichannel
digital potentiometer or rheostat. The module can also be used to model analog or digital
potentiometer devices using **Potentiometer** and **DigitalWiper** classes correspondingly.

Potentiometer
-------------
Potentiometer is a simple electrical component with three terminals.
The two terminals `A` and `B` are connected to opposite sides of the resistor,
and the third terminal `W` is connected to sliding contact (the wiper).
This design turns potentiometer into variable voltage divider,
which consist of two resistors `A-W` and `W-B` connected in series.
If a reference input voltage is applied across `A-B` terminals,
one may control the output voltage at wiper terminal by changing its position.

Following symbols are used to depict a potentiometer.
IEC standard symbol is on the left and US ANSI symbol is on the right.

.. figure:: images/pot_symbols.svg
    :width: 300
    :align: center

    Fig. 1. Potentiometer symbols.

For the remainder of the documentation, we will stick to the IEC symbol.

.. note::
    In BDPotentiometer wiper position is measured from terminal `B`
    to terminal `A`.

If :math:`x` is a wiper position measured from `B` (:math:`x=0`)
to `A` (:math:`x=1`), then

.. math::

    R_{BW} = R_{AB} \cdot x,

.. math::

    R_{AW} = R_{AB} \cdot (1 - x).

If we applied voltage :math:`V_{in}` to terminal `A` and put terminal `B` to ground, output
voltage :math:`V_{out}` at wiper terminal would be

.. math::

    V_{out} = V_{in} \frac{R_{BW}}{R_{AB}} = V_{in} \cdot x.

These equations describe an ideal divider. The
:class:`~BDPotentiometer.potentiometer.Potentiometer` class also models the
terminal series resistances :math:`R_A` and :math:`R_B` and the wiper
resistance :math:`R_W`, so

.. math::

    R_{BW} = R_B + R_W + R_{AB} \cdot x,

.. math::

    R_{AW} = R_A + R_W + R_{AB} \cdot (1 - x).

The class also accepts terminal voltages :math:`V_A` and :math:`V_B` and a
load resistance :math:`R_{load}` connected between the wiper and
:math:`V_{load}`. :math:`V_W` is then the loaded-divider solution; the ideal
:math:`V_{in} \cdot x` above is the case :math:`R_A = R_B = R_W = 0`,
:math:`V_B = 0`, and no load.

Rheostat
--------
The use of only two terminals, one of which is the wiper `W`, turns potentiometer
into rheostat or variable resistor `B-W` or `A-W`. This is the simplest application of the potentiometer.

Digital Potentiometer
---------------------
The digital potentiometer is a special type of potentiometer
with electronically controlled wiper position. It usually consists of a network of resistors
connected in series. The movement of the wiper is emulated by electronic switches,
which connect certain resistor of the network to the output terminal of the digital potentiometer.
The resolution of discrete wiper movement is determined by the value
of the single resistor of the network.

.. figure:: images/digital_pot.svg
    :width: 600
    :align: center

    Fig. 2. Equivalent circuit of digital potentiometer with resistor ladder design.

As you can see in Fig. 2. each tap of resistor ladder has its own wiper resistance :math:`R_w`
(usually some tens of Ohms). Small variations of :math:`R_w` are possible between taps,
which can lead to a non-linear change in resistance when changing the value of the slider position.
The lower the total resistance of the potentiometer, the more noticeable this effect.

If :math:`x` is again the wiper code (an integer this time) measured from `B`
(:math:`x=0`) towards `A`, and :math:`N` is the full-scale divisor, then

.. math::

    R_{BW} = \frac{R_{AB}}{N} \cdot x + R_{w} = R_{s} \cdot x + R_{w},

.. math::

    R_{AW} = \frac{R_{AB}}{N} \cdot (N - x) + R_{w} = R_{s} \cdot (N - x) + R_{w}.

``max_value`` is this divisor: 128 for 7-bit parts and 256 for 8-bit parts.
The highest accepted code is ``max_code = min(max_value, 255)``, so 8-bit
parts clamp at 255 while still dividing by 256. The resulting :math:`x / N` is
the relative wiper position in the range 0 to 1.


Programming Digital Potentiometer
---------------------------------

Digital potentiometer can be controlled using its dedicated input/output pins.
This could be:

* Up/Down input pins for incrementing/decrementing pot's value;
* SPI interface;
* I2C interface.

Some digital potentiometers have non-volatile memory for wiper position storage.
Such pots restore wiper position after power cycle. Other potentiometers reset wiper position on
power cycle to default value (middle tap usually).
