cloud server url: https://iot-server-9u9o.onrender.com/

✅ Project description
✅ System architecture
✅ User types and roles
✅ IoT node configuration
✅ Installation & setup
✅ API flow
✅ Sensor/Actuator information
✅ Troubleshooting
✅ Future improvements

🌱 Hydroponics IoT Monitoring & Automation System

MicroPython + Raspberry Pi Pico W + REST API Backend

This project provides a complete IoT solution for monitoring and automating a hydroponics system.
It features:

Real-time monitoring of temperature, humidity, water temperature, water quality (TDS), pH, and water level

Automated registration of IoT nodes

Periodic sensor data upload to a backend server

Optional actuator control (pump, fan)

OLED display for local system status

Offline mode with local config caching

📘 Table of Contents

Project Overview

System Architecture

User Types

Hardware Requirements

Installation & Setup

Configuring the IoT Node

How the System Works

Sensors & Actuators

API Endpoints

Troubleshooting

Future Improvements

📍 Project Overview

This project enables a Raspberry Pi Pico W (or Zero W) to function as an IoT node in a hydroponics setup.
It performs the following tasks:

✔ Automatically registers itself with the server
✔ Retrieves assigned sensor & actuator IDs
✔ Periodically reads all sensors
✔ Sends readings to /readings API endpoint
✔ Displays readings on OLED
✔ Supports reconnect and retry logic

A config.json file is saved after registration — this file connects the node to its server identity.

🏗 System Architecture
┌──────────────────────────────────────────┐
│ Backend Server (Flask/FastAPI) │
│ - IoT Registration (/iot/register) │
│ - Save readings (/readings) │
│ - Database for sensors & actuators │
└──────────────────────────────────────────┘
▲
│ HTTP POST (JSON)
▼
┌───────────────────────────────────┐
│ IoT Node (Pico W / ESP32) │
│ - Reads sensors │
│ - Sends data │
│ - Displays info on OLED │
│ - Uses config.json after signup │
└───────────────────────────────────┘
▲
│ I²C / Analog / GPIO
▼
┌──────────────────────┐
│ Sensors │
└──────────────────────┘

👤 User Types
🟩 1. Owner (System Administrator)

Manages the backend dashboard and controls:

Registered IoT nodes

Sensor assignments

Actuator states (pump, fan)

View historical data

Configure thresholds & alerts

🟦 2. IoT Node

Runs the MicroPython script.
Responsibilities:

Connect to WiFi

Register itself and fetch IDs

Read all sensors

Post sensor data periodically

Retry if connection fails

Display data on OLED

🧰 Hardware Requirements
Component Purpose
Raspberry Pi Pico W Main IoT controller
SSD1306 OLED (I2C) On-device UI feedback
DHT11 Ambient temp & humidity
DS18B20 Water temperature
TDS Sensor Water quality
Ultrasonic HC-SR04 Water level
pH Sensor (analog) pH reading
Relay modules Pump / fan control
Jumper wires Connections
🛠 Installation & Setup
1️⃣ Install MicroPython Firmware

Flash MicroPython onto the Pico W using Thonny or picotool.

2️⃣ Project Files to Upload

Upload these files to the Pico:

main.py
sensors_actuator.py
ssd1306.py
config.json (auto-created after registration)

3️⃣ Configure WiFi + Server Settings

Inside main.py update:

WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"
SERVER_BASE_URL = "http://<your-server-ip>:5000"

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

Save response to config.json

Switch to normal mode

Normal Mode

If config.json exists, the Pico:

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

🪲 Troubleshooting
Issue Cause Fix
Cannot connect WiFi Wrong SSID/password Update WIFI_SSID
Registration fails Server not reachable Check SERVER_BASE_URL
No sensor data Sensors wired incorrectly Confirm GPIO pins
OLED blank Wrong SDA/SCL pins Update OledDisplay pins
DS18B20 not found Missing pull-up resistor Add 4.7kΩ
🚀 Future Improvements

MQTT version (instead of HTTP polling)

Over-the-air firmware updates

Actuator automation rules (pump auto-on/off)

Encrypted communication

Add camera monitoring
