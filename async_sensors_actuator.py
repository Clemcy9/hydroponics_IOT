"""
Non-blocking, asynchronous sensor module
Optimized for Raspberry Pi Pico (MicroPython + uasyncio)
Includes console logging of all sensor data.
"""

import uasyncio as asyncio
from machine import Pin, ADC, SoftI2C
from ssd1306 import SSD1306_I2C
import onewire, ds18x20, dht, utime


# ==============================
# OLED DISPLAY
# ==============================
class OledDisplay:
    def __init__(self, sda=0, scl=1):
        i2c = SoftI2C(sda=Pin(sda), scl=Pin(scl))
        self.oled = SSD1306_I2C(128, 64, i2c)

    def show(self, lines):
        self.oled.fill(0)
        y = 0
        for line in lines:
            self.oled.text(line, 0, y)
            y += 12
        self.oled.show()


# ==============================
# SENSOR MODULE (ASYNC)
# ==============================
class SensorModule:
    def __init__(self):
        # --- Pins ---
        self.dht_pin = Pin(17, Pin.IN)
        self.dht = dht.DHT11(self.dht_pin)

        self.ds_pin = Pin(15)
        self.ds = ds18x20.DS18X20(onewire.OneWire(self.ds_pin))
        self.ds_roms = self.ds.scan()

        self.tds_adc = ADC(Pin(26))
        self.ph_adc = ADC(Pin(27))
        self.ldr_adc = ADC(Pin(28))

        self.trigger = Pin(8, Pin.OUT)
        self.echo = Pin(9, Pin.IN)

        # Variables updated asynchronously
        self.data = {
            "ambient_temp": None,
            "humidity": None,
            "water_temp": None,
            "tds": None,
            "water_level": None,
            "ph": None,
            "ldr": None,
        }

        # calibration
        self.VREF = 3.3
        self.KVALUE = 0.5
        self.ph_v4 = 1.92
        self.ph_v7 = 2.50
        self.slope = (7 - 4) / (self.ph_v7 - self.ph_v4)

        # display
        self.display = OledDisplay()

    # -----------------------------
    # ASYNC SENSOR TASKS
    # -----------------------------

    async def task_dht(self):
        while True:
            try:
                self.dht.measure()
                self.data["ambient_temp"] = self.dht.temperature()
                self.data["humidity"] = self.dht.humidity()
            except:
                pass
            await asyncio.sleep(2)

    async def task_ds18(self):
        while True:
            try:
                self.ds.convert_temp()
                await asyncio.sleep_ms(750)
                t = self.ds.read_temp(self.ds_roms[0])
                self.data["water_temp"] = t
            except:
                pass
            await asyncio.sleep(1)

    async def task_ldr(self):
        while True:
            raw = self.ldr_adc.read_u16()
            self.data["ldr"] = round(raw / 65535 * 100, 1)
            await asyncio.sleep(0.3)

    async def task_ph(self):
        while True:
            raw = self.ph_adc.read_u16()
            voltage = (raw / 65535) * self.VREF
            ph = 7 + (voltage - self.ph_v7) * self.slope
            self.data["ph"] = round(ph, 1)
            await asyncio.sleep(0.4)

    async def task_tds(self):
        while True:
            raw = self.tds_adc.read_u16()
            voltage = (raw / 65535) * self.VREF

            if self.data["water_temp"] is not None:
                comp = 1 + 0.02 * (self.data["water_temp"] - 25)
            else:
                comp = 1

            comp_voltage = voltage / comp

            tds = (
                133.42 * comp_voltage**3
                - 255.86 * comp_voltage**2
                + 857.39 * comp_voltage
            ) * self.KVALUE

            self.data["tds"] = round(tds, 1)
            await asyncio.sleep(0.5)

    async def task_ultrasonic(self):
        while True:
            try:
                self.trigger.low()
                utime.sleep_us(3)
                self.trigger.high()
                utime.sleep_us(10)
                self.trigger.low()

                timeout = utime.ticks_us() + 30000
                while self.echo.value() == 0:
                    if utime.ticks_us() > timeout:
                        raise Exception("Timeout1")

                start = utime.ticks_us()
                timeout = utime.ticks_us() + 30000
                while self.echo.value() == 1:
                    if utime.ticks_us() > timeout:
                        raise Exception("Timeout2")

                end = utime.ticks_us()
                duration = end - start
                distance = (duration * 0.0343) / 2

                self.data["water_level"] = round(distance, 1)

            except:
                self.data["water_level"] = None

            await asyncio.sleep(0.2)

    async def task_display(self):
        while True:
            d = self.data
            lines = [
                f"AT:{d['ambient_temp']} H:{d['humidity']}",
                f"WT:{d['water_temp']}  L:{d['ldr']}%",
                f"TDS:{d['tds']}ppm",
                f"WL:{d['water_level']}cm",
                f"pH:{d['ph']}"
            ]
            self.display.show(lines)
            await asyncio.sleep(1)

    # -----------------------------
    # NEW: CONSOLE LOGGING TASK
    # -----------------------------
    async def task_console_logger(self):
        while True:
            print("\n=== SENSOR READINGS ===")
            for k, v in self.data.items():
                print(f"{k}: {v}")
            print("=======================\n")
            await asyncio.sleep(0.5)   # print every 1 second

    # -----------------------------
    # START ALL TASKS
    # -----------------------------
    async def run(self):
        await asyncio.gather(
            self.task_dht(),
            self.task_ds18(),
            self.task_ldr(),
            self.task_ph(),
            self.task_tds(),
            self.task_ultrasonic(),
            self.task_display(),
            self.task_console_logger(),   # <-- NEW
        )


# ==============================
# MAIN
# ==============================
async def main():
    sm = SensorModule()
    await sm.run()

asyncio.run(main())
