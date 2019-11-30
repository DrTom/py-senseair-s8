try:
    import uasyncio as asyncio
except ImportError:
    import asyncio as asyncio
import random as random
import time as time
import math as math
import logging as logging
import sense_air_s8.modbus_crc as modbus_crc

import sys
if sys.implementation.name == 'cpython':
    def ticks_us():
       return int(time.time_ns()/1000)
else:
    from time import ticks_us

class SenseAirS8():

    REQUEST_CO2_CMD = b'\xFE\x44\x00\x08\x02\x9F\x25'

    def __init__(self, uart):
        self.uart = uart
        self.logger = logging.getLogger('SenseAirS8')
        self.readout = {}
        self.logger.info(" initialized ")

    def format_ba(self,ba):
        return "".join(' {:02X}'.format(x) for x in ba).strip()

    def uart_bytes_available(self):
        if sys.implementation.name == 'cpython':
            return self.uart.in_waiting
        else:
            return self.uart.any()

    def read_co2(self):
        try:
            read_start = ticks_us()
            bytes_avail = self.uart_bytes_available()
            if bytes_avail != 7:
                raise Exception("expect 7 bytes from uart, but {} available".format(bytes_avail))
            self.raw_readout = self.uart.read(7)
            read_end= ticks_us()
            self.logger.debug(
                    "UART received [{:s}] in : {:d} us".format(
                        self.format_ba(self.raw_readout), read_end-read_start))
            if not modbus_crc.check(self.raw_readout):
                raise ValueError("CRC Error {}".format(self.raw_readout))
            high = self.raw_readout[3]
            low = self.raw_readout[4]
            co2 = (high*256) + low
            self.readout= {
                "value": co2,
                "timestamp": time.time()}
            self.logger.debug(" readout {}".format(self.readout))
        except Exception as ex:
            err_msg = '{}'.format(ex)
            self.logger.error(err_msg)
            self.readout = {"error": err_msg}

    def read_synchronized(self):
        request_start = ticks_us()
        self.uart.write(self.REQUEST_CO2_CMD)
        request_end = ticks_us()
        self.logger.debug(
                "uart request duration: {:d} us".format(
                    request_end-request_start))
        time.sleep(0.1)
        self.read_co2()
        return self.readout


class SenseAirS8as(SenseAirS8):
    def __init__(self, uart, intervall_secs=5):
        SenseAirS8.__init__(self,uart)
        self.intervall_secs = intervall_secs
        self.loop = asyncio.get_event_loop()
        self.loop_id = None
        self.update_handlers = {}
        self.logger.info(" initialized, intervall_secs {:d} ".format(intervall_secs))
        self.re_start_async_loop()

    def add_update_handler(self, key, handler):
        self.update_handlers[key]=handler

    async def read_async_loop(self, loop_id):
        try:
            if self.loop_id == loop_id:
                self.uart.write(self.REQUEST_CO2_CMD)
                await asyncio.sleep(0.1)
            if self.loop_id == loop_id:
                self.read_co2()
            for k in self.update_handlers:
                handler = self.update_handlers[k]
                self.logger.debug("invoking handler for key {}".format(k))
                await handler(self.readout)
        except Exception as e:
            self.readout= { "error": str(e)}
            self.logger.error(str(e))
        s = 0
        while s < self.intervall_secs and loop_id == self.loop_id:
            s += 1
            await asyncio.sleep(1)
        if self.loop_id == loop_id:
            self.loop.create_task(self.read_async_loop(loop_id))

    def re_start_async_loop(self):
        loop_id = random.getrandbits(32)
        self.loop_id = loop_id
        self.loop.create_task(self.read_async_loop(loop_id))
        self.logger.info(" (re)started async loop loop_id: {:d}".format(loop_id))
