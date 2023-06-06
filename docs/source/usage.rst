Usage
=====

Installation
------------

To install BDPotentiometer use pip

.. code-block:: console

   $ pip install BDPotentiometer


Example (MCP4231)
-----------------
MCP4231 is a 7-bit digital potentiometer with two independent channels with SPI control.

Import MCP4231 class first.

>>> from BDPotentiometer.mcp4xxx import MCP4231

Then create a new potentiometer given the total resistance ``r_ab``.
Parameter ``device`` specifies SPI device (chip enable) pin the pot is connected to.

>>> my_pot = MCP4231(r_ab=10e3, device=0)

That is it. Now you can freely operate your pot.

>>> my_pot.channels[0].value = 27
27

