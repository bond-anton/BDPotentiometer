Usage
=====

Installation
------------

To install BDPotentiometer use pip

.. code-block:: console

   $ pip install BDPotentiometer

The optional ``spi`` extra installs ``spidev``, needed by
:class:`~BDPotentiometer.transport.SpiDevTransport`:

.. code-block:: console

   $ pip install 'BDPotentiometer[spi]'

Example (MCP4231)
-----------------

MCP4231 is a 7-bit digital potentiometer with two independent channels and SPI
control.

Import the MCP4231 class first.

.. code-block:: python

   from BDPotentiometer.mcp4xxx import MCP4231

Then create a new potentiometer given the total resistance ``r_ab``. The value
must be one of the entries in
:data:`BDPotentiometer.mcp4xxx.resistance_list`. ``device`` selects the SPI
chip-enable line the pot is connected to; the bus and pins depend on the
wiring.

.. code-block:: python

   my_pot = MCP4231(r_ab=10e3, device=0)
   my_pot.set_value(0, 27)

With no transport arguments the device builds a
:class:`~BDPotentiometer.transport.GpiozeroSpiTransport`.

Selecting a transport
---------------------

Pass a transport instance with ``transport=``.
:class:`~BDPotentiometer.transport.SpiDevTransport` opens the Linux spidev
device directly and needs the ``spi`` extra. ``bus`` and ``device`` identify
``/dev/spidev<bus>.<device>``, so their values depend on the wiring:

.. code-block:: python

   from BDPotentiometer.mcp4xxx import MCP4231
   from BDPotentiometer.transport import SpiDevTransport

   transport = SpiDevTransport(bus=0, device=0)
   my_pot = MCP4231(r_ab=10e3, transport=transport)
   my_pot.set_value(0, 27)

For tests and dry runs, :class:`~BDPotentiometer.transport.FakeSpiTransport`
returns scripted frames instead of touching hardware:

.. code-block:: python

   from BDPotentiometer.mcp4xxx import MCP4231
   from BDPotentiometer.transport import FakeSpiTransport

   transport = FakeSpiTransport(default=[0, 0])
   my_pot = MCP4231(r_ab=10e3, transport=transport)
   my_pot.set_value(0, 27)
   print(transport.calls[-1])

See :doc:`transport` for backend selection, ownership, and permissions.
