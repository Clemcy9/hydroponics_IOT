#download: onewire and ds18b20 libraries
#install "micropython-ssd1306" library

from machine import Pin, SoftI2C
from ssd1306 import SSD1306_I2C
import machine, onewire, ds18x20, time
from machine import ADC, Pin
from picozero import LED
import dht
import time
import utime

# Connect TDS sensor to GP26 (ADC0) and temp_sensor to GPIO14
tds_adc = ADC(Pin(26))    #tds sensor
ds_pin = Pin(14)  #ds18b20 temp_sensor
dht_pin = Pin(16, Pin.IN) #dht11 pin

# TDS Calibration values
VREF = 3.3       # Pico ADC reference voltage
K_VALUE = 0.5    # Probe calibration constant
TEMP = 0        # Get temp values from sensor in realtime


# Create a DHT object
sensor = dht.DHT11(dht_pin)

# Create a ds18b20 object
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
print('Found DS devices: ', roms)

#OLED
i2c = SoftI2C(sda=Pin(0), scl=Pin(1))
oled = SSD1306_I2C(128, 64, i2c)

#Ultrasonic sensor
trigger = Pin(3, Pin.OUT)
echo = Pin(2, Pin.IN)

def read_tds():
    # Read 16-bit value (0–65535) from ADC
    raw = tds_adc.read_u16()
    voltage = (raw / 65535) * VREF  # Convert to volts

    # Temperature compensation
    comp_coeff = 1.0 + 0.02 * (TEMP - 25.0)
    comp_voltage = voltage / comp_coeff

    # Convert voltage to TDS (ppm)
    tds = (133.42 * comp_voltage**3
          - 255.86 * comp_voltage**2
          + 857.39 * comp_voltage) * K_VALUE

    return tds, voltage


while True:
    #TDS reading
    tds, volt = read_tds()
    
    #Ultrasonic sensor reading
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(5)
    trigger.low()
    while echo.value() == 0:
        signaloff = utime.ticks_us()
    while echo.value() == 1:
        signalon = utime.ticks_us()
    timepassed = signalon - signaloff
    distance = (timepassed * 0.0343) / 2
    distance = round(distance, 2) 
    print("Distance: ", distance, "cm")
    
    sensor.measure()
    temperature = sensor.temperature()
    humidity = sensor.humidity()
    
    #DS18B20 Temp sensor reading
    ds_sensor.convert_temp()
    time.sleep_ms(750)
    for rom in roms:
        water_temp = ds_sensor.read_temp(rom)
        TEMP = int(ds_sensor.read_temp(rom))

    print(f"Ambience Temp.: {temperature:.2f}°C, Ambience Hum.: {humidity:.2f}%, Water Temp.: {water_temp:.2f}°C, Water Qty.: {tds:.2f}ppm")

    
    oled.fill(0)

    oled.text("HYDROPONICS", 24,0)
    
    oled.text("A.T/H: ", 0,12)
    oled.text(str(temperature),50,12)
    oled.text("*C",70,12)
    oled.text("/", 85,12)
    oled.text(str(humidity),95,12)
    oled.text("%",120,12)
    
    oled.text("W.Tmp: ", 0,24)
    oled.text(str(int(ds_sensor.read_temp(rom))),50,24)
    oled.text("*C",70,24)
    
    oled.text("W.Qlt: ", 0,36)
    oled.text(str(int(ds_sensor.read_temp(rom))),50,36)
    oled.text("ppm",70,36)
    
    oled.text("pH: ", 0,48)
    #oled.text(str(int(ds_sensor.read_temp(rom))),60,48)
    oled.text("W.L: ", 50,48)
    oled.text(str(int(distance)),80,48)
    oled.text("cm",110,48)
    
    time.sleep(1)
    oled.show()

