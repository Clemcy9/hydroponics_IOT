import network
import time
import ujson
import os
import urequests
from sensors_actuator import OledDisplay, SensorModule

REGISTER_FILE = "register.json"
DB_FILE = "db.json"
MODE = "local" #or cloud

SETTINGS ={
    "local":{
        "WIFI_SSID":"Samsung Galaxy S8+", # "aboy"
        "WIFI_PASSWORD" :"inchristalone", #"aries1234" 
        "SERVER_BASE_URL" :"http://192.168.43.240:5000" # "http://192.168.5.4:5000"

    }
}

# Defaults to cloud mode
WIFI_SSID = "aboy"
WIFI_PASSWORD = "aries1234"
SERVER_BASE_URL = "https://iot-server-9u9o.onrender.com"

# Override with local settings if MODE = "local"
if MODE == "cloud":
    WIFI_SSID = SETTINGS["local"]["WIFI_SSID"]
    WIFI_PASSWORD = SETTINGS["local"]["WIFI_PASSWORD"]
    SERVER_BASE_URL = SETTINGS["local"]["SERVER_BASE_URL"]


DATA_CACHING_INTERVAL_SECONDS = 10
SEND_INTERVAL_SECONDS = 5  # can be 60 for 1 min
MAX_RETRIES = 5  # stop loop after 5 consecutive failures

# algorithm
# 1. check if connected to wifi
# 2. check if network access to server using hello packets
# 3. check if iot node has been registered using register,json. this is FIRST BOOT mode
# 4. create a data.json file, get sensor readings at regular intervals (READINGS_INTERVAL), append to data.json
# 5. read the content of data.json and send at specified intervals (UPLOAD_INTERVAL)
# 6. on account of failure to upload data, update the payload by incrementing the retries field in each readings data
# 7. on REGISTRATION mode and (not)connected to wifi  but no internet connection, switch to "DATA BANK" mode- only store readings don't upload

# different modes
# 1. REGISTRATION mode - when (!register.json) && (!data.json) && (is_internet_access) possibly during initial boot
# 2. RESET (clear off data) mode - when (!register.json)&&(data.json) possibly during initial boot
# 3. RELAY (normal) mode - (register.json) && (data.json) && (is_internet_access)
# 4. DATA_BANK mode - (register.json) && (data.json) && (!is_internet_access)
# 6. DATA_LOGGING (display sensor readings) mode - (!register.json) && (!data.json) && (!is_internet_access)
# 5. OTA_UPDATE mode - 


def mode_selector(*args, **kwargs):
    try:
        # load_file(REGISTER_FILE)
        connect_wifi(WIFI_SSID, WIFI_PASSWORD)
        check_internet()
        if(not load_file(REGISTER_FILE) and not load_file(DB_FILE) ):
            # REGISTRATION MODE
            print("Registration mode")
            time.sleep(2)
            register_iot()
            
        if(not load_file(REGISTER_FILE) and load_file(DB_FILE) ):
            # RESET MODE
            print("Reset mode")
            time.sleep(2)
        
        if(load_file(REGISTER_FILE)):
            # RELAY (normal) MODE
            print("Reset mode")
            time.sleep(2)
            send_sensor_data_periodically()

    except IOError as e:
        pass
        # switch to 
    except NoInternetException as e:
        if(not load_file(REGISTER_FILE) and not load_file(DB_FILE) ):
            # DATA_BANK MODE
            print("DATA_BANK mode")
            time.sleep(2)
            append_file(DB_FILE, sensor_data.read_all_sensors())
    except NotConnectedWifi as e:
        # DATA_LOGGING MODE
        print("DATA_LOGGING mode")
        time.sleep(2)
        sensor_data.read_all_sensors()
#     finally:
#         pass


# commented because hardware not available
oled_display = OledDisplay()
sensor_data = SensorModule()
readings = sensor_data.read_all_sensors()
# readings = {
#             "ambient_temp": 1,
#             "humidity": 2,
#             "water_temp": 3,
#             "water_level",45
#             "tds": 4,
#             "ph":33,
#             # "tds_voltage": 5,
#         }

# custom exceptions
class NoInternetException(Exception):
    def __init__(self, *args: object) -> None:
        self.message  = "no internet connection"
        super().__init__(*args)

class NotConnectedWifi(Exception):
    def __init__(self, *args: object) -> None:
        self.message  = "not connected to wifi"
        super().__init__(*args)

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to network...")
        wlan.connect(ssid, password)
        retries = 0
        while not wlan.isconnected() and retries < 20:
            print("Waiting for connection...")
            oled_display.show_text(["HYDROPONICS", "wifi failure", "create new hotspot", f"N={WIFI_SSID}",f"P={WIFI_PASSWORD}"])
            time.sleep(1)
            retries += 1

    if wlan.isconnected():
        print("Connected to WiFi:", wlan.ifconfig())
        return True
    else:
        print("Failed to connect")
        raise NotConnectedWifi
        # return False

def check_internet():
    res = urequests.get(f"{SERVER_BASE_URL}/hello")
    if res.status_code ==200:
        return 1
    else:
        raise NoInternetException
        # return 0

def append_file(filename, data):
    try:
        if not filename in os.listdir():
            with open(filename, "w") as f:
                ujson.dump(data, f)
            print(f"Saved {filename}")
            return 1
        else:
            with open(filename, "r+") as f:
                n_data = ujson.load(f)
                n_data.extend(data)
                f.seek(0)
                ujson.dump(n_data, f)
                f.truncate()
            return 1
    except IOError as e:
        print("Error saving file:", e)
        raise

def overwrite_file(filename, data):
    try:
        with open(filename, "w") as f:
            ujson.dump(data, f)
        print(f"Saved {filename}")
        return 1
    except IOError as e:
        print("Error saving file:", e)
        raise #this will raise the current exception

def load_file(filename):
    if filename in os.listdir():
        try:
            with open(filename, "r") as f:
                return ujson.load(f)
        except IOError as e:
            print("Error reading file:", e)
    return None

def register_iot():
    oled_display.show_text(["HYDROPONICS", "REGISTRATION MODE"])
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    url = f"{SERVER_BASE_URL}/iot/register"
    headers = {"Content-Type": "application/json"}
    payload = {
        "name": "iot-picoZeroW",
        "status": "active",
        "sensors": [
            {"name": "water_level"},
            {"name": "water_temp"},
            {"name": "ambient_temp"},
            {"name": "humidity"},
            {"name": "ldr"},
            {"name": "ph"},
            {"name": "tds"}
        ],
        "actuators": [
            {"name": "water pump"},
            {"name": "fan relay"}
        ]
    }

    try:
        oled_display.show_text(["HYDROPONICS", "wifi connected"])
        print("📡 Sending registration payload...")
        res = urequests.post(url, headers=headers, data=ujson.dumps(payload))
        print("HTTP Status:", res.status_code)

        if res.status_code == 201:
            response_data = res.json()
            res.close()
            overwrite_file(REGISTER_FILE, response_data)
            print("🎉 Registration successful, register saved.")
            oled_display.show_text(["HYDROPONICS", "REGISTRATION SUCCESSFUL"])
            return 1
        else:
            print("⚠️ Unexpected response:", res.text)
            oled_display.show_text(["HYDROPONICS", "REGISTRATION FAILED"])
            res.close()
            return 0

    except Exception as e:
        print("Error during registration:", e)
        return 0

def send_sensor_data():
    register = load_file(REGISTER_FILE)
    if not register:
        print("⚠️ No register found, please register first.")
        return

    if not connect_wifi(WIFI_SSID, WIFI_PASSWORD):
        oled_display.show_text(["HYDROPONICS", "wifi failure", "create new hotspot", f"N={WIFI_SSID}",f"P={WIFI_PASSWORD}"])
        raise Exception('can not connet network')
        # return

    url = f"{SERVER_BASE_URL}/readings"
    headers = {"Content-Type": "application/json"}

    # Construct payload using IDs from register
    payload = {"sensors": [], "actuators": []}

    # --- sensors ---
    for sensor in register.get("sensors", []):
        name = sensor["name"]
        if name in readings:
            payload["sensors"].append({
                "sensor": sensor["_id"],
                "value": str(readings[name]),
            })

    # --- actuators (optional) ---
    # actuator_states = {"Pump": 1, "Fan": 0}
    # for actuator in register.get("actuators", []):
    #     name = actuator["name"]
    #     if name in actuator_states:
    #         payload["actuators"].append({
    #             "actuator": actuator["_id"],
    #             "value": str(actuator_states[name]),
    #         })
    try:
        print("📡 Sending sensor data:", payload)
        res = urequests.post(url, headers=headers, data=ujson.dumps(payload))
        print("HTTP Status:", res.status_code)
        print("Server Response:", res.text)
        res.close()
    except Exception as e:
        print("Error sending data:", e)
        raise e
        # if it failed to send, store that data locally with timestamps and send sending is restored

def send_sensor_data_periodically():
    retry_count = 0
    while True:
        try:
            oled_display.show_text(["HYDROPONICS", "Data MODE", "sending.."])
            send_sensor_data()
            oled_display.show_text(["HYDROPONICS", "Data MODE", "sent..."])
            retry_count =0  # reset retry counter on success
            print(f'retries is: {retry_count}')
        except Exception as e:
            oled_display.show_text(["HYDROPONICS", "wifi failure", f"retries:{retry_count}"])
        
            retry_count += 1
            print(f"Error sending data (attempt {retry_count}/{MAX_RETRIES}): {e}")
            if retry_count >= MAX_RETRIES:
                print("⚠️ Max retries reached, stopping periodic sending.")
                oled_display.show_text(["HYDROPONICS", "wifi failure", "max retries ", "restart d system"])
        
                break
        print(f"Waiting for {SEND_INTERVAL_SECONDS} seconds before next send...\n")
        time.sleep(SEND_INTERVAL_SECONDS)

def boot():
    if "register.json" in os.listdir():
        print("Config found → Running in NORMAL MODE")
        send_sensor_data_periodically()
    else:
        print("No register found → Running in REGISTRATION MODE")
        register_iot()
        send_sensor_data_periodically()  # start sending after registration

boot()

