Usage
=====

Installation
------------

To install the core library only use pip

.. code-block:: console

   $ pip install BDPotentiometer

A bare install ships no hardware backend: the model classes and
:class:`~BDPotentiometer.transport.FakeSpiTransport` work, while building a
device for real hardware raises ``ImportError`` naming the extra to install.

The default hardware backend is spidev, installed by the ``spi`` extra:

.. code-block:: console

   $ pip install 'BDPotentiometer[spi]'

The optional gpiozero backend is installed by the ``gpiozero`` extra:

.. code-block:: console

   $ pip install 'BDPotentiometer[gpiozero]'

Example (MCP4231)
-----------------

MCP4231 is a 7-bit digital potentiometer with two independent channels and SPI
control.

Import the MCP4231 class first.

.. code-block:: python

   from BDPotentiometer.mcp4xxx import MCP4231

Then create a new potentiometer given the total resistance ``r_ab``. The value
must be one of the entries in
:data:`BDPotentiometer.mcp4xxx.resistance_list`. With no ``transport=`` and no
pin keywords, the device builds a
:class:`~BDPotentiometer.transport.SpiDevTransport`: ``port`` selects the
spidev bus and ``device`` selects the chip-select line, so this needs the
``spi`` extra.

.. code-block:: python

   my_pot = MCP4231(r_ab=10e3, device=0)
   my_pot.set_value(0, 27)

Passing any of ``clock_pin``, ``mosi_pin``, ``miso_pin``, or ``select_pin``
selects the gpiozero backend instead, which needs the ``gpiozero`` extra:

.. code-block:: python

   my_pot = MCP4231(r_ab=10e3, clock_pin=11, select_pin=8)

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
returns scripted frames instead of touching hardware and needs no extra:

.. code-block:: python

   from BDPotentiometer.mcp4xxx import MCP4231
   from BDPotentiometer.transport import FakeSpiTransport

   transport = FakeSpiTransport(default=[0, 0])
   my_pot = MCP4231(r_ab=10e3, transport=transport)
   my_pot.set_value(0, 27)
   print(transport.calls[-1])

See :doc:`transport` for backend selection, ownership, and permissions.
