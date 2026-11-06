Welcome to BDPotentiometer's documentation!
===========================================

**BDPotentiometer** is a Python library for easy control of digital
potentiometers. It supports the MCP4xxx family over SPI through a pluggable
transport layer, so the SPI backend can be replaced without changing device
code.

Check out the :doc:`usage` section for further information.

.. note::

   Three SPI backends ship today: gpiozero hardware SPI (default), plain
   ``spidev``, and an in-memory fake for tests. ``I2cTransport`` is a protocol
   placeholder for future chips; no I2C backend is implemented.

Contents
--------

.. toctree::

   introduction
   usage
   transport
   api
