import network
import time
import ujson
import os
import urequests
from sensors_actuator import OledDisplay, SensorModule

CONFIG_FILE = "config.json"
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


SEND_INTERVAL_SECONDS = 5  # can be 60 for 1 min
MAX_RETRIES = 5  # stop loop after 5 consecutive failures

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
        return False

def save_file(filename, data):
    try:
        with open(filename, "w") as f:
            ujson.dump(data, f)
        print(f"✅ Saved response to {filename}")
    except Exception as e:
        print("❌ Error saving file:", e)

def load_file(filename):
    if filename in os.listdir():
        try:
            with open(filename, "r") as f:
                return ujson.load(f)
        except Exception as e:
            print("❌ Error reading file:", e)
    return None

def register_iot():
    oled_display.show_text(["HYDROPONICS", "REGISTRATION MODE"])
    if not connect_wifi(WIFI_SSID, WIFI_PASSWORD):
        oled_display.show_text(["HYDROPONICS", "wifi failure", "create new hotspot", f"N={WIFI_SSID}",f"P={WIFI_PASSWORD}"])
        return

    url = f"{SERVER_BASE_URL}/iot/register"
    headers = {"Content-Type": "application/json"}
    payload = {
        "name": "iot-picoZeroW",
        "status": "active",
        "sensors": [
            {"name": "ambient_temp"},
            {"name": "humidity"},
            {"name": "water_level"},
            {"name": "TDS_waterQuaity_sensor"}
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
            save_file(CONFIG_FILE, response_data)
            print("🎉 Registration successful, config saved.")
            oled_display.show_text(["HYDROPONICS", "REGISTRATION SUCCESSFUL"])
        else:
            print("⚠️ Unexpected response:", res.text)
            oled_display.show_text(["HYDROPONICS", "REGISTRATION FAILED"])
            res.close()

    except Exception as e:
        print("❌ Error during registration:", e)
        previous_saved = load_file(CONFIG_FILE)
        if previous_saved:
            print("⚙️ Using previously saved config.")
        else:
            print("No existing configuration found.")

def send_sensor_data():
    config = load_file(CONFIG_FILE)
    if not config:
        print("⚠️ No config found, please register first.")
        return

    if not connect_wifi(WIFI_SSID, WIFI_PASSWORD):
        oled_display.show_text(["HYDROPONICS", "wifi failure", "create new hotspot", f"N={WIFI_SSID}",f"P={WIFI_PASSWORD}"])
        raise Exception('can not connet network')
        # return

    url = f"{SERVER_BASE_URL}/readings"
    headers = {"Content-Type": "application/json"}

    # Construct payload using IDs from config
    payload = {"sensors": [], "actuators": []}

    # --- sensors ---
    for sensor in config.get("sensors", []):
        name = sensor["name"]
        if name in readings:
            payload["sensors"].append({
                "sensor": sensor["_id"],
                "value": str(readings[name]),
            })

    # --- actuators (optional) ---
    # actuator_states = {"Pump": 1, "Fan": 0}
    # for actuator in config.get("actuators", []):
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
        print("❌ Error sending data:", e)
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
            print(f"❌ Error sending data (attempt {retry_count}/{MAX_RETRIES}): {e}")
            if retry_count >= MAX_RETRIES:
                print("⚠️ Max retries reached, stopping periodic sending.")
                oled_display.show_text(["HYDROPONICS", "wifi failure", "max retries ", "restart d system"])
        
                break
        print(f"Waiting for {SEND_INTERVAL_SECONDS} seconds before next send...\n")
        time.sleep(SEND_INTERVAL_SECONDS)

def boot():
    if "config.json" in os.listdir():
        print("Config found → Running in NORMAL MODE")
        send_sensor_data_periodically()
    else:
        print("No config found → Running in REGISTRATION MODE")
        register_iot()
        send_sensor_data_periodically()  # start sending after registration

boot()

