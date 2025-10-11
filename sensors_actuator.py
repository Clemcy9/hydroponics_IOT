"""
sensor_actuator.py
Modular interface for sensors and actuators on Raspberry Pi Pico (MicroPython)
Supports:
 - DHT11 (temperature/humidity)
 - DS18B20 (water temperature)
 - TDS sensor (water quality)
 - Ultrasonic sensor (water level)
 - SSD1306 OLED display
"""

from machine import Pin, ADC, SoftI2C
from ssd1306 import SSD1306_I2C
import onewire, ds18x20, dht, utime, time


# ==============================
# OLED DISPLAY CLASS
# ==============================
class OledDisplay:
    def __init__(self, sda=0, scl=1):
        i2c = SoftI2C(sda=Pin(sda), scl=Pin(scl))
        self.oled = SSD1306_I2C(128, 64, i2c)

    def clear(self):
        self.oled.fill(0)

    def show_text(self, lines):
        """Display lines of text (list of strings)"""
        self.clear()
        y = 0
        for line in lines:
            self.oled.text(line, 0, y)
            y += 12
        self.oled.show()


# ==============================
# SENSOR MODULE
# ==============================
class SensorModule:
    def __init__(self):
        # --- Sensor pins ---
        self.tds_adc = ADC(Pin(26))         # TDS analog input
        self.ds_pin = Pin(14)                # DS18B20
        self.dht_pin = Pin(16, Pin.IN)       # DHT11
        self.trigger = Pin(3, Pin.OUT)       # Ultrasonic trigger
        self.echo = Pin(2, Pin.IN)           # Ultrasonic echo

        # --- Calibration values ---
        self.VREF = 3.3
        self.K_VALUE = 0.5
        self.water_temp = 25.0  # Default, updated by DS18B20

        # --- Sensor setup ---
        self.dht_sensor = dht.DHT11(self.dht_pin)
        self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(self.ds_pin))
        self.roms = self.ds_sensor.scan()
        print("✅ Found DS18B20 devices:", self.roms)

        # --- OLED ---
        self.display = OledDisplay()

    # ------------------------------
    # Individual sensor readings
    # ------------------------------

    def read_dht(self):
        try:
            self.dht_sensor.measure()
            temp = self.dht_sensor.temperature()
            hum = self.dht_sensor.humidity()
            return temp, hum
        except Exception as e:
            print("❌ DHT11 error:", e)
            return None, None

    def read_ds18b20(self):
        try:
            self.ds_sensor.convert_temp()
            time.sleep_ms(750)
            for rom in self.roms:
                temp = self.ds_sensor.read_temp(rom)
                if temp is not None:
                    self.water_temp = temp
                    return temp
        except Exception as e:
            print("❌ DS18B20 error:", e)
        return None

    def read_tds(self):
        try:
            raw = self.tds_adc.read_u16()
            voltage = (raw / 65535) * self.VREF

            comp_coeff = 1.0 + 0.02 * (self.water_temp - 25.0)
            comp_voltage = voltage / comp_coeff

            tds = (
                133.42 * comp_voltage**3
                - 255.86 * comp_voltage**2
                + 857.39 * comp_voltage
            ) * self.K_VALUE

            return round(tds, 2), round(voltage, 2)
        except Exception as e:
            print("❌ TDS read error:", e)
            return None, None

    def read_ultrasonic(self):
        try:
            self.trigger.low()
            utime.sleep_us(2)
            self.trigger.high()
            utime.sleep_us(5)
            self.trigger.low()

            while self.echo.value() == 0:
                signaloff = utime.ticks_us()
            while self.echo.value() == 1:
                signalon = utime.ticks_us()

            timepassed = signalon - signaloff
            distance = (timepassed * 0.0343) / 2
            return round(distance, 2)
        except Exception as e:
            print("❌ Ultrasonic read error:", e)
            return None

    # ------------------------------
    # Unified data collector
    # ------------------------------
    def read_all_sensors(self):
        ambient_temp, humidity = self.read_dht()
        water_temp = self.read_ds18b20()
        tds, voltage = self.read_tds()
        distance = self.read_ultrasonic()

        readings = {
            "DHT_ambient_temp_sensor": ambient_temp,
            "DHT_humiity_sensor": humidity,
            "water_temp": water_temp,
            "tds": tds,
            "tds_voltage": voltage,
            "ULTRASONIC_tankWaterLevel_sensor": distance
        }

        self.display_data(readings)
        return readings

    # ------------------------------
    # Display readings on OLED
    # ------------------------------
    def display_data(self, readings):
        lines = [
            "HYDROPONICS",
            f"AT:{readings['ambient_temp']}C  H:{readings['humidity']}%",
            f"WT:{readings['water_temp']}C  TDS:{readings['tds']}ppm",
            f"WL:{readings['water_level']}cm",
        ]
        self.display.show_text(lines)


# ==============================
# DEMO LOOP (for testing)
# ==============================
# if __name__ == "__main__":
#     sensor_module = SensorModule()

#     while True:
#         data = sensor_module.read_all_sensors()
#         print("Sensor Readings:", data)
#         time.sleep(2)
