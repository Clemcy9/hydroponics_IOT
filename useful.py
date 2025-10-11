import os, ujson

def load_response(filename):
    if filename in os.listdir():
        try:
            with open(filename, "r") as f:
                return ujson.load(f)
        except Exception as e:
            print("❌ Error reading file:", e)
    return None

data  = load_response("config.json")

# print(f"sensor data:{data['sensors']}")

readings = {
            "temp sensor": 1,
            "humidity sensor": 2,
            "water_temp": 3,
            "tds": 4,
            "tds_voltage": 5,
            "water_level": 6
        }

# payload = [{x['_id']:y[str(x['name'])]} for x in data['sensors'] y in readings]

# payload = {
#     sensor['_id']: readings[sensor['name']]
#     for sensor in data['sensors']
#     if sensor['name'] in readings
# }

payload = {
        "iot_id": 'config["iot"]["_id"]',
        "sensors": [{sensor['_id']: readings[sensor['name']]} for sensor in data['sensors'] if sensor['name'] in readings]
    }


print(f'payload:{payload}')