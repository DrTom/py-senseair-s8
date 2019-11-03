import uasyncio as asyncio
import urandom as random
import utime as time
import math as math
import logging as logging

class SenseAirS8():

    REQUEST_CO2_CMD = b'\xFE\x44\x00\x08\x02\x9F\x25'

    def __init__(self, uart):
        self.uart = uart
        self.logger = logging.getLogger('SenseAirS8')
        self.readout = {}
        self.resp = b''
        self.logger.info(" initialized ")

    def format_ba(self,ba):
        return "".join(' {:02X}'.format(x) for x in ba).strip()

    def read_co2(self):
        read_start = time.ticks_us()
        self.resp = self.uart.read(7)
        read_end= time.ticks_us()
        self.logger.debug(
                "UART received [{:s}] in : {:d} us".format(
                    self.format_ba(self.resp), read_end-read_start))
        high = self.resp[3]
        low = self.resp[4]
        co2 = (high*256) + low
        self.readout= {
                "value": co2,
                "timestamp": time.time()}
        self.logger.debug(" readout {:s}".format(str(self.readout)))


    def set_read_error(self):
        self.readout = {
                "error": "no suiteable response via uart"
                }

    def read_synchronized(self):
        request_start = time.ticks_us()
        self.uart.write(self.REQUEST_CO2_CMD)
        request_end = time.ticks_us()
        self.logger.debug(
                "uart request duration: {:d} us".format(
                    request_end-request_start))
        time.sleep(0.1)
        if self.uart.any() >= 7:
            self.read_co2()
        else:
            self.set_read_error()
        return self.readout


class SenseAirS8as(SenseAirS8):
    def __init__(self, uart, intervall_secs=5):
        SenseAirS8.__init__(self,uart)
        self.intervall_secs = intervall_secs
        self.loop = asyncio.get_event_loop()
        self.loop_id = None
        self.logger.info(" initialized, intervall_secs {:d} ".format(intervall_secs))
        self.re_start_async_loop()

    async def read_async_loop(self, loop_id):
        try:
            if self.loop_id == loop_id:
                self.uart.write(self.REQUEST_CO2_CMD)
                await asyncio.sleep_ms(100)
            if self.loop_id == loop_id:
                self.read_co2()
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
