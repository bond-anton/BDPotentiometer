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

Exceptions
~~~~~~~~~~

.. autoclass:: BDPotentiometer.transport.base.TransportError
   :members:
   :show-inheritance:

.. autoclass:: BDPotentiometer.transport.base.TransportClosed
   :members:
   :show-inheritance:
