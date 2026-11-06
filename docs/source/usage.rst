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

Values and validation
---------------------

``value`` is an integer wiper code, clamped to ``0..max_code``. Because
``max_code`` equals ``max_value`` on the shipped parts, 7-bit parts accept
``0..128`` and 8-bit parts ``0..256``. Fractional values are rejected rather
than rounded, and booleans, ``NaN``, and infinities are rejected as numbers.
``invert`` must be a real bool.

``value_relative`` is ``value / max_value``. On the shipped parts it spans
``0..1``; a subclass whose code range is narrower than its divisor tops out at
``max_code / max_value``. The setter accepts ``0..1`` and rounds to the
nearest code.

``set_channel_label`` strips surrounding whitespace and rejects an empty
label. Passing ``port``, ``device``, or any pin keyword together with
``transport=`` or ``spi=`` raises ``TypeError``.

``label`` and ``log_level`` configure the device logger. A logger is
configured once: a later device without ``log_level`` keeps the level already
set, and ``propagate`` stays enabled, so records may also reach the root
handlers.

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
