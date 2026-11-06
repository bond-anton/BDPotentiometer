Transport backends
==================

Devices and wipers do not talk to SPI directly. They send frames through a
transport, which can be replaced with ``transport=``.

Interface
---------

A transport provides:

* ``transfer(tx) -> list[int]`` -- send one frame of words in ``0..255`` and
  return the received words in the same order;
* ``close()`` -- release the bus handle; repeated calls have no effect;
* ``closed`` -- ``True`` once the handle has been closed.

The shipped backends satisfy the
:class:`~BDPotentiometer.transport.SpiTransport` protocol. Any object with
callable ``transfer`` and ``close`` methods is accepted.

Backends
--------

:class:`~BDPotentiometer.transport.GpiozeroSpiTransport`
   Default. Wraps a gpiozero hardware SPI object. Passing ``port=``,
   ``device=``, ``clock_pin=``, ``mosi_pin=``, ``miso_pin=``, or
   ``select_pin=`` to a device builds this transport.

:class:`~BDPotentiometer.transport.SpiDevTransport`
   Plain Linux ``spidev`` backend for ``/dev/spidev<bus>.<device>``. Requires
   ``pip install 'BDPotentiometer[spi]'``.

:class:`~BDPotentiometer.transport.FakeSpiTransport`
   In-memory backend with scripted responses, for tests without hardware.

Injection
---------

.. code-block:: python

   from BDPotentiometer.mcp4xxx import MCP4231
   from BDPotentiometer.transport import SpiDevTransport

   transport = SpiDevTransport(bus=0, device=0)
   pot = MCP4231(r_ab=10e3, transport=transport)
   pot.set_value(0, 27)
   pot.close()

Ownership
---------

A device's ``close()`` delegates to its transport.

* ``GpiozeroSpiTransport`` closes only a handle it built. When it wraps a
  caller-supplied ``spi=`` object, ``close()`` marks the transport closed but
  leaves the shared bus open for its other users.
* ``SpiDevTransport`` always owns and closes its spidev handle.
* ``FakeSpiTransport`` only flips its ``closed`` flag.

Create one transport per device. All channels of a device share it.

Linux permissions
-----------------

``SpiDevTransport`` needs the kernel SPI device node and permission to open it.
If the node exists but opening fails, add a udev rule. This project's
development setup uses the ``gpio`` group; adjust the group to match your
system::

   SUBSYSTEM=="spidev", GROUP="gpio", MODE="0660"

Install the rule under ``/etc/udev/rules.d/``, reload the rules, and reconnect
the device. Kernel SPI must also be enabled, for example with
``dtparam=spi=on`` in ``/boot/firmware/config.txt`` on current Raspberry Pi OS.
