from sense_air_s8 import *
import logging
import sys
import time
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio as asyncio


################################################################################
### configure serial/uart device ###############################################
################################################################################

# MicroPython on microcontrollers adjust pins:
TX_PIN=12
RX_PIN=13

# LINUX, MAC_OS, etc: adjust this depending on you serial driver and device driver:
USB_SERIAL='/dev/cu.SLAB_USBtoUART'

################################################################################
### set serial/uart ############################################################
################################################################################

# might need adjustment on MicroPython derivatives
if sys.implementation.name == 'micropython':
    from machine import UART
    uart = UART(1, 9600, tx=TX_PIN, rx=RX_PIN, timeout=100)
else:
    from serial import Serial
    uart = Serial(USB_SERIAL,9600,timeout=1)


################################################################################
### logging ####################################################################
################################################################################

logger = logging.getLogger('')

if sys.implementation.name == 'cpython':
    logger.addHandler(logging.StreamHandler())


################################################################################
### synchronous mode with debugging enabled ####################################
################################################################################

s8sync = SenseAirS8(uart)
s8sync.logger.setLevel(logging.DEBUG)
print("sync readout {}".format(s8sync.read_synchronized()))


################################################################################
### asynchronous mode ##########################################################
################################################################################

async def co2_update_handler(update):
    logger.debug("co2_update_handler {}".format(update))
    raw = update["value"]
    rounded = round(raw/50.0)*50
    print("{} CO2: {} raw: {}".format(round(time.time()),rounded,raw))

s8async = SenseAirS8as(uart)
s8sync.logger.setLevel(logging.DEBUG)
s8async.add_update_handler("print_handler", co2_update_handler)


################################################################################

loop = asyncio.get_event_loop()
loop.run_forever()
