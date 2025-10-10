import network
import time
import ujson
import os
import urequests


#wifi connection
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print("connecting to network..")
        wlan.connect(ssid, password)
        retries = 0
        while not wlan.isconnected() and retries < 15:
            print("waiting for connection...")
            time.sleep(1)
            retries +=1
    
    if wlan.isconnected():
        print("connectd to wifi:", wlan.ifconfig())
        return True
    else:
        print("failed to connect")
        return False
    

#save response to file
def save_response(filename, data):
    with open(filename, "w") as f:
        ujson.dump(data, f)
    print(f"saved response to {filename}")

#load response from filesystem
def load_response(filename):
    if filename in os.listdir():
        with open(filename, "r") as f:
            return ujson.load(f)
    return None

#main function
def register_iot():
    connect_wifi("aboy", "aries1234")
    
    url = "http://192.168.5.4:5000/iot/register"
    headers = {"Content-Type": "application/json"}
    payload = {
        "name": "iot-farm1",
        "status": "active",
        "sensors": [
            {"name": "temp sensor"},
            {"name": "humidity sensor"}
        ],
        "actuators": [
            {"name": "water pump"},
            {"name": "fan relay"}
        ]
    }
    
    try:
        # can also write to display
        print('sending payload..')
        res = urequests.post(url, headers = headers, data=ujson.dumps(payload))
        print("status:", res.status_code, "type of res.status:", type(res.status_code))
        if res.status_code == 201:
            response_data = res.json()
            res.close()
            save_response("iot_registration.json", response_data)
            print(f'saved response to filesystem')
    except Exception as e:
        print("error:", e)
        previous_saved = load_response("iot_registration.json")
        if previous_saved:
            print("using previous data", previous_saved)
        
        
register_iot()        
    
        
    
        
        
        