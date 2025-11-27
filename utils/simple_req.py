import network
import time
import urequest  # This now imports your module!

SSID = "aboy"
PASSWORD = "aries1234"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Connecting to WiFi...")
while not wlan.isconnected():
    time.sleep(1)

print("Connected:", wlan.ifconfig())

# Test GET
url = "http://httpbin.org/get"
response = urequest.get(url)
print("Status:", response.status_code)
print("Text:", response.text)
response.close()
