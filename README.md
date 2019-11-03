
~~~python
import logging
from machine import UART
from SenseAirS8 import *

logging.getLogger('SenseAirS8').setLevel(logging.DEBUG)

uart = UART(1, 9600, tx=12, rx=13, timeout=100)
s8 = SenseAirS8(uart)
s8.read_synchronized()

~~~



~~~python
import logging
from machine import UART
from SenseAirS8 import *

logging.getLogger('SenseAirS8').setLevel(logging.DEBUG)

uart = UART(1, 9600, tx=12, rx=13, timeout=100)
s8as = SenseAirS8as(uart)

import uasyncio as asyncio
loop = asyncio.get_event_loop()
loop.run_forever()
~~~
