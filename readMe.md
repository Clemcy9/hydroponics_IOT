# 🚀 Hydroponics IoT Monitoring System

A smart hydroponics system that senses and logs essential environmental parameters to ensure optimal plant growth conditions.  
The system measures:

- 🌞 Light Intensity
- 💧 Air Humidity
- 🌡️ Air Temperature
- 🌡️ Water Temperature
- 🧪 Total Dissolved Solids (TDS)
- ⚗️ pH Level of Water

The device supports **three intelligent operation modes**:
**Data Relay Mode**, **Data Bank Mode**, and **Debugging Mode**, automatically switching based on network availability.

---

## 📦 Tech Stack

### 🌐 Cloud

- Node.js + Express.js
- MongoDB
- Google Sheets (optional logging)

### 🔧 Hardware

- Raspberry Pi Pico W
- MicroPython / Python
- Sensors:
  - DHT11/DHT22 (air temp & humidity)
  - DS18B20 (water temperature)
  - TDS sensor
  - pH sensor
  - Light/LDR sensor
- WiFi connectivity

---

## 🧠 System Behavior

| Mode                | Trigger Condition                           | Behavior                                          |
| ------------------- | ------------------------------------------- | ------------------------------------------------- |
| **Data Relay Mode** | WiFi hotspot available **with internet**    | Sends data to cloud every 10 mins; logs on-screen |
| **Data Bank Mode**  | WiFi hotspot available **without internet** | Saves data offline until internet returns         |
| **Debugging Mode**  | No WiFi detected                            | Shows continuous logs on-screen only              |

📌 **Sensor reading interval:** every 1 minute  
📌 **Cloud upload interval:** every 10 minutes

---

## 🚀 How to Run the System

### 1. **Data Relay Mode (Cloud Connected)**

Use this when real-time logging is required.

1. Create a hotspot with:
   - **Name:** `Samsung Galaxy s8+`
   - **Password:** `inchristalone`
2. Ensure hotspot has **internet access**
3. Power on the device
4. The screen will display:  
   **"RELAY mode"**
5. Shortly after, data logs appear on the display

---

### 2. **Data Bank Mode (Offline Logging)**

Activated when WiFi exists **without internet**.

1. Turn on the hardware with WiFi present but **no internet**
2. Screen shows:  
   **"DATA BANK mode"**
3. Data is saved offline
4. When internet returns, stored data auto-syncs to cloud

---

### 3. **Debugging Mode (No WiFi)**

Use this for calibration and hardware testing.

1. Turn on the hardware **without WiFi**
2. Screen displays:  
   **"DEBUGGING mode"**
3. Sensor readings display continuously

---

## 📁 Project Structure (Example)

project/
│── cloud-api/
│ ├── server.js
│ ├── routes/
│ ├── controllers/
│ ├── models/
│ └── utils/
│
│── pico-firmware/
│ ├── boot.py
│ ├── main.py
│ ├── sensors_actuactor.py
│ ├── lib/

---

## 📊 Data Flow Overview

1. Sensors capture environmental readings every **1 minute**
2. Pico W analyzes and prepares the readings
3. Depending on mode:
   - Sends data to cloud every **10 minutes**
   - Stores data offline
   - Displays debugging data
4. Cloud API stores data in:
   - MongoDB
   - Google Sheets (optional mirror)

---

## 🤝 Contributing

Contributions, hardware improvements, and optimizations are welcome!  
Feel free to open an issue or submit a pull request.

---

## 📄 License

MIT License.

4️⃣ Required Python Libraries on Pico

These must be uploaded:

urequests.py

ujson.py

ssd1306.py

onewire.py

ds18x20.py

🔧 Configuring the IoT Node
Registration Mode (First Boot)

The Pico automatically enters registration mode if no config.json is found.

It will:

Connect to WiFi

POST to /iot/register

Receive:

Node ID

Sensor \_ids

Actuator \_ids

Save response to reg.json

Switch to normal mode

Normal Mode

If reg.json exists, the Pico:

Reads all sensors using SensorModule

Sends payload every SEND_INTERVAL_SECONDS

Retries up to MAX_RETRIES

Displays live data on OLED

📡 How the System Works

1. Registration Request
   {
   "name": "iot-picoZeroW",
   "status": "active",
   "sensors": [
   { "name": "DHT_ambient_temp_sensor" },
   { "name": "DHT_humiity_sensor" },
   { "name": "ULTRASONIC_tankWaterLevel_sensor" },
   { "name": "TDS_waterQuaity_sensor" }
   ],
   "actuators": [
   { "name": "water pump" },
   { "name": "fan relay" }
   ]
   }

2. Saved Config Structure
   {
   "\_id": "...",
   "sensors": [
   { "name": "DHT_ambient_temp_sensor", "_id": "..." },
   { "name": "tds", "_id": "..." }
   ],
   "actuators": [...]
   }

3. Periodic Sensor Payload
   {
   "sensors": [
   { "sensor": "<id>", "value": "25.3" },
   { "sensor": "<id>", "value": "68" }
   ],
   "actuators": []
   }

🧪 Sensors & Actuators
Sensor Method Output
DHT11 read_dht() temp, humidity
DS18B20 read_ds18b20() water temp
TDS read_tds() ppm, voltage
pH Sensor read_ph() pH, voltage
Ultrasonic HC-SR04 read_ultrasonic() distance (water level)
OLED OledDisplay.show_text() device status
🌐 API Endpoints
POST /iot/register

Registers the IoT node and returns sensor/actuator IDs.

POST /readings

Accepts periodic sensor payloads.
