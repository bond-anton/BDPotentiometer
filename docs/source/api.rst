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
command ``11``; the read response is ``1111 111D8`` followed by ``D7:D0``.
The ninth data bit is what lets a full-scale code of 256 be represented, so
the data field spans ``0..0x100``.

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

.. autoclass:: BDPotentiometer.transport.base.SpiTransport
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.transport.base.I2cTransport
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.transport.gpiozero_spi.GpiozeroSpiTransport
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.transport.spidev_spi.SpiDevTransport
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.transport.fake.FakeSpiTransport
   :members:
   :show-inheritance:

.. autofunction:: BDPotentiometer.transport.base.is_spi_transport

Transport selection
~~~~~~~~~~~~~~~~~~~

.. autofunction:: BDPotentiometer.transport.selection.build_default_transport

.. autodata:: BDPotentiometer.transport.selection.GPIOZERO_PIN_ARGS

.. autodata:: BDPotentiometer.transport.selection.GPIOZERO_SPI_ARGS

gpiozero helpers
~~~~~~~~~~~~~~~~

.. autofunction:: BDPotentiometer.__gpiozero_helpers.fix_gpiozero_dual_cs_spi

An existing ``Device.pin_factory`` is left untouched: the patch returns
without replacing a factory the application already selected.

Exceptions
~~~~~~~~~~

.. autoclass:: BDPotentiometer.transport.base.TransportError
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.transport.base.TransportClosed
   :members:
   :show-inheritance:
