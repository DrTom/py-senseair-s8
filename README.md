SenseAirS8 CO2-Sensor Asynchronous Device Library for Python
============================================================

This library supports reading of CO2 values from a SenseAir S8 via UART.
Supported Python implementations are MicroPython or regular Python (cPython).
This library supports **asynchronous**, and synchronous access, the latter is
mostly only useful for testing or demonstration.

The coded has been successfully tested with
* MicroPython 1.11 on a ESP32 Wrover DevBoard
* Python 3.7 on MacOS with a USB-UART adapter

Caveats with respect to the Sensor Family
-----------------------------------------

SenseAir S8 comprises a family of CO2 sensors. They look very much
alike but there are different pinouts and protocols. This library supports the
SenseAir S8 004-0-0053.

Dependencies
------------

* MicroPython (1.11 tested) or Python (3.7 tested)
* logging, see [micropython-logging] for MicroPython
* asyncio, or [uasyncio] for MicroPython

Usage
-----

The following is a synchronous example for MicroPython.

~~~python
from SenseAirS8 import *

# MicroPython on microcontrollers adjust pins:
TX_PIN=12
RX_PIN=13

from machine import UART
uart = UART(1, 9600, tx=TX_PIN, rx=RX_PIN, timeout=100)

s8sync = SenseAirS8(uart)
print("sync readout {}".format(s8sync.read_synchronized()))
~~~

For advanced usage see the provided code in [main.py](./main.py) and
of the source code in [SenseAirS8/](./SenseAirS8/).


Limitations and Restrictions
----------------------------

* The implementation of the Modbus protocol does not perform CRC at this time.
*
* Only the CO2 read command is implemented.
*
* There seem to be variations of the S8 Modbus protocol around. This library
  supports the CO2 read command starting with `xFE x44`. There exists a S8
  Modubs documentation which describes a CO2 read command starting with `xFE
  x04`. This protocol is not supported at this time.



[micropython-logging]: https://pypi.org/project/micropython-logging/
[uasyncio]: https://pypi.org/project/micropython-uasyncio/
