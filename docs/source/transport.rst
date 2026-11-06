Transport backends
==================

Devices and wipers do not talk to SPI directly. They send frames through a
transport, which can be replaced with ``transport=``. The transport layer is
not part of this package: it lives in the separate
`scietex.hal.spi <https://github.com/bond-anton/scietex.hal.spi>`_ distribution,
so other SPI hardware libraries can share the same backends.

Interface
---------

A transport provides:

* ``transfer(tx) -> list[int]`` -- send one frame of words in ``0..255`` and
  return the received words in the same order;
* ``close()`` -- release the bus handle; repeated calls have no effect. When
  the underlying close fails, the transport stays open and ``close()`` can be
  retried;
* ``closed`` -- ``True`` once ``close()`` has run. For a transport that wraps a
  caller-supplied handle, this reports that the transport itself is closed, not
  that the shared bus was closed.

The shipped backends satisfy the ``SpiTransport`` protocol. Any object with
callable ``transfer`` and ``close`` methods is accepted.

Installation
------------

The transport package is not installed with the core library. Install the
extra for the backend you need:

.. code-block:: console

   $ pip install 'scietex.hal.spi[spi]'
   $ pip install 'scietex.hal.spi[gpiozero]'

A bare install ships no hardware backend, and constructing a device for real
hardware raises ``ImportError`` naming the extra to install.

Backends
--------

``SpiDevTransport``
   Default. Opens ``/dev/spidev<bus>.<device>`` through ``spidev``. With no
   transport and no pin keywords, ``port=`` and ``device=`` select this
   transport, ``port`` mapping to the spidev bus and ``device`` to the
   chip-select line. Requires ``scietex.hal.spi[spi]``.

``GpiozeroSpiTransport``
   Optional. Wraps a gpiozero hardware SPI object. Passing ``clock_pin=``,
   ``mosi_pin=``, ``miso_pin=``, or ``select_pin=`` to a device builds this
   transport. Requires ``scietex.hal.spi[gpiozero]``.

``FakeSpiTransport``
   In-memory backend with scripted responses, for tests without hardware. It
   needs no extra.

Backend keywords select the default transport only. Passing ``port=``,
``device=``, or any pin keyword together with ``transport=`` or ``spi=``
raises ``TypeError``: supply either an explicit transport or the backend
keywords, never both.

Backend keyword mapping
-----------------------

``build_default_transport`` turns the device keyword arguments into a
transport:

===================  ==================================================
Keyword              Effect
===================  ==================================================
``port``             spidev bus number; with no pin keyword, selects
                     ``SpiDevTransport``
``device``           spidev chip-select line
``clock_pin``        selects ``GpiozeroSpiTransport``
``mosi_pin``         selects ``GpiozeroSpiTransport``
``miso_pin``         selects ``GpiozeroSpiTransport``
``select_pin``       selects ``GpiozeroSpiTransport``
===================  ==================================================

Pin keywords win over the spidev keywords, so any pin keyword builds the
gpiozero backend.

Injection
---------

.. code-block:: python

   from BDPotentiometer.mcp4xxx import MCP4231
   from scietex.hal.spi import SpiDevTransport

   transport = SpiDevTransport(bus=0, device=0)
   pot = MCP4231(r_ab=10e3, transport=transport)
   pot.set_value(0, 27)
   pot.close()

Ownership
---------

Whoever constructs the transport closes it. A device closes only a transport
it built itself; a transport passed with ``transport=`` or ``spi=`` stays open
after the device's ``close()``, because the caller still owns it.

* ``GpiozeroSpiTransport`` closes only a handle it built. When it wraps a
  caller-supplied ``spi=`` object, ``close()`` marks the transport closed
  (``closed`` becomes ``True``) but leaves the shared bus open for its other
  users.
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
the device. The user running the process must be a member of the group in the
rule; on this project's Fedora setup that group is ``gpio``, because no ``spi``
group exists. Kernel SPI must also be enabled, for example with
``dtparam=spi=on`` in ``/boot/firmware/config.txt`` on current Raspberry Pi OS.

.. seealso::

   `scietex.hal.spi <https://github.com/bond-anton/scietex.hal.spi>`_ -- the
   transport package and its API reference.
