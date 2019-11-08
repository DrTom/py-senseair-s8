from SenseAirS8 import *
import logging
import sys
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

s8_logger = logging.getLogger('SenseAirS8')
# s8_logger.setLevel(logging.DEBUG)

if sys.implementation.name == 'cpython':
    s8_logger.addHandler(logging.StreamHandler())


################################################################################
### synchronous mode with debugging enabled ####################################
################################################################################

s8sync = SenseAirS8(uart)
print("sync readout {}".format(s8sync.read_synchronized()))


################################################################################
### asynchronous mode ##########################################################
################################################################################

s8async = SenseAirS8as(uart)

async def print_readout_loop():
    await asyncio.sleep(5)
    while True:
        print("async readout {}".format(s8async.readout))
        await asyncio.sleep(60)

loop = asyncio.get_event_loop()
loop.create_task(print_readout_loop())
loop.run_forever()
