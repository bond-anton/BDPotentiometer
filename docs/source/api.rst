API reference
=============

Potentiometer model
-------------------

.. autoclass:: BDPotentiometer.potentiometer.Potentiometer
   :members:
   :show-inheritance:
   :class-doc-from: init

Digital wiper
-------------

.. autoclass:: BDPotentiometer.digital_wiper.DigitalWiper
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.digital_wiper.SpiDigitalWiper
   :members:
   :show-inheritance:

Digital potentiometer device
----------------------------

.. autoclass:: BDPotentiometer.digital_potentiometer.DigitalPotentiometerDevice
   :members:
   :show-inheritance:
   :class-doc-from: init

MCP4xxx devices
---------------

.. autoclass:: BDPotentiometer.mcp4xxx.mcp4xxx.MCP4xxx
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.mcp4xx1.MCP4xx1
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.mcp4xx2.MCP4xx2
   :members:
   :show-inheritance:

``resistance_list`` contains the supported ``r_ab`` values in ohms.

.. autodata:: BDPotentiometer.mcp4xxx.resistance_list

Wire format
~~~~~~~~~~~

A wiper write is one 16-bit word: bits 15:12 carry the register address,
bits 11:10 the command, bit 9 is unused, bit 8 is the ninth data bit ``D8``,
and bits 7:0 are ``D7:D0``. A write command uses command ``00`` and a read
command ``11``.

Every read response frames the data the same way: bits 15:9 are
``1111111`` and bit 8 carries ``D8``, so the ninth data bit travels next to
``D7:D0``. The ninth data bit is what lets a full-scale code of 256 be
represented, so the data field spans ``0..0x100``.

Two registers carry fixed bits in both directions. ``STATUS`` (``0x5``) has
bits 8:5 ``D8:D5`` reserved and forced ``1``, and bit 1 is ``SHDN``; a real
read from an MCP4251 returns ``[0xFF, 0xE0]``. ``TCON`` (``0x4``) has bit 8
``D8`` reserved and forced ``1``, bits 7:0 are
``R1HW, R1A, R1W, R1B, R0HW, R0A, R0W, R0B``, and its power-on value is
``0x1FF``; a real read returns ``[0xFF, 0xFF]``. A ``TCON`` write therefore
carries ``D8 = 1`` as well.

Concrete chips
--------------

MCP4XX1 potentiometers
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4131
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4141
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4151
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4161
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4231
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4241
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4251
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4261
   :members:
   :show-inheritance:

MCP4XX2 rheostats
~~~~~~~~~~~~~~~~~

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4132
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4142
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4152
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4162
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4232
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4242
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4252
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.mcp4xxx.MCP4262
   :members:
   :show-inheritance:

Transport backends
------------------

The transport layer is not part of this package. It ships in the separate
``scietex.hal.spi`` distribution, which provides the ``SpiTransport`` protocol,
the ``SpiDevTransport``, ``GpiozeroSpiTransport``, and ``FakeSpiTransport``
backends, the ``TransportError`` and ``TransportClosed`` exceptions, and the
selection helpers used by the device constructors:

.. code-block:: python

   from scietex.hal.spi import SpiDevTransport

See :doc:`transport` for backend selection, ownership, and permissions.

.. seealso::

   `scietex.hal.spi <https://github.com/bond-anton/scietex.hal.spi>`_ -- API
   reference for the transport layer.

Package exports
---------------

``from BDPotentiometer import *`` follows ``__all__``, which lists only the
model classes: ``DigitalPotentiometerDevice``, ``DigitalWiper``,
``Potentiometer``, and ``SpiDigitalWiper``. Import transports and transport
exceptions from ``scietex.hal.spi``.
