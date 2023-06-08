Introduction
============

**BDPotentiometer** is a python module for easy control of multichannel
digital potentiometer or rheostat.

Potentiometer
-------------
Potentiometer is a simple electrical component with three terminals.
The two terminals `A` and `B` are connected to opposite sides of the resistor,
and the third terminal `W` is connected to sliding contact (the wiper).
This design turns potentiometer into variable voltage divider,
which consist of two resistors `A-W` nd `W-B` connected in series.
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

Rheostat
--------
The use of only two terminals, one of which is the wiper `W`, turns potentiometer
into rheostat or variable resistor `B-W` or `A-W`. This is a simplest application of the potentiometer.

Digital Potentiometer
---------------------
The digital potentiometer is a special type of potentiometer
with electronically controlled wiper position. They usually consist of a network of resistors
connected in series. The movement of the wiper is emulated by electronic switches,
which connect certain resistor of the network to the output terminal of the digital potentiometer.
The resolution of discrete wiper movement is determined by the value
of the single resistor of the network.

.. figure:: images/digital_pot.svg
    :width: 600
    :align: center

    Fig. 2. Equivalent circuit of digital potentiometer with resistor ladder design.

As you can see in Fig. 2. each tap of resistor ladder has its own wiper resistance `R_w`
(usually some tens of Ohms). Small variations of `R_w` are possible between taps,
which can lead to a non-linear change in resistance when changing the value of the slider position.
The lower the total resistance of the potentiometer, the more noticeable this effect.

If :math:`x` is again a wiper position (integer this time) measured from `B` (:math:`x=0`)
to `A` (:math:`x=n`), then

.. math::

    R_{BW} = \frac{R_{AB}}{n} \cdot x + R_{w} = R_{s} \cdot x + R_{w},

.. math::

    R_{AW} = \frac{R_{AB}}{n} \cdot (n - x) + R_{w} = R_{s} \cdot (n - x) + R_{w}.


Programming Digital Potentiometer
---------------------------------

Digital potentiometer is usually being programmed using its serial communication interface.
This could be:

* Up/Down input pins for incrementing/decrementing pot's value;
* SPI interface;
* I2C interface.

Some digital potentiometers have non-volatile memory for wiper position storage.
Such pots restore wiper position after power cycle. Other potentiometers reset wiper position on
power cycle to default value (usually middle of the scale).
