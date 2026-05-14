# 🌡️ BME280 Environmental Sensor

[![CI](https://github.com/guillaumedelre/bme280/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/guillaumedelre/bme280/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> Python 3 driver for the Bosch BME280 environmental sensor — reads temperature, pressure and humidity over I²C on a Raspberry Pi, and exposes them via a REST API with MQTT publishing for Home Assistant integration.

---

## 📋 Table of Contents

- [Hardware](#-hardware)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Usage](#-usage)
  - [CLI](#cli)
  - [HTTP API](#http-api)
  - [Docker](#docker)
- [API Reference](#-api-reference)
- [Home Assistant Integration](#-home-assistant-integration)
- [Development](#-development)
- [Project Structure](#-project-structure)

---

## 🔌 Hardware

| Component | Details |
|-----------|---------|
| **Sensor** | Bosch BME280 — Waveshare Environmental Sensor (SKU 15231) |
| **Board** | Raspberry Pi Rev 2+ (I²C bus 1) |
| **Interface** | I²C — default address `0x77`, alternate `0x76` (SDO pin) |
| **Protocol** | SMBus via `/dev/i2c-1` |

### Wiring (Raspberry Pi GPIO)

```
BME280          Raspberry Pi
──────          ────────────
VCC    ──────►  Pin 1  (3.3V)
GND    ──────►  Pin 6  (GND)
SDA    ──────►  Pin 3  (GPIO2 / SDA1)
SCL    ──────►  Pin 5  (GPIO3 / SCL1)
```

> 💡 Make sure I²C is enabled: `sudo raspi-config` → Interface Options → I2C → Enable

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Raspberry Pi                       │
│                                                     │
│  ┌──────────────┐     ┌──────────────────────────┐  │
│  │  bme280.py   │     │      sensor_api.py       │  │
│  │              │     │         (Flask)           │  │
│  │  I²C driver  │◄────│  GET /bme280             │  │
│  │  Calibration │     │  GET /bme280/publish     │  │
│  │  algorithms  │     │  GET /health             │  │
│  └──────┬───────┘     └───────────┬──────────────┘  │
│         │                         │                  │
│         ▼                         ▼                  │
│  ┌──────────────┐     ┌──────────────────────────┐  │
│  │  BME280 chip │     │      MQTT Broker         │  │
│  │  (I²C 0x77)  │     │   (Home Assistant)       │  │
│  └──────────────┘     └──────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites

```bash
# Enable I²C on Raspberry Pi
sudo raspi-config   # Interface Options → I2C → Enable
sudo reboot
```

### Clone & install

```bash
git clone https://github.com/guillaumedelre/bme280.git
cd bme280

pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
# Edit .env with your MQTT broker details
nano .env
```

---

## ⚙️ Configuration

All settings are driven by environment variables. Copy `.env.example` to `.env` and fill in your values.

| Variable | Default | Description |
|----------|---------|-------------|
| `BME280_I2C_BUS` | `1` | I²C bus number (`1` for Pi Rev 2+, `0` for Rev 1) |
| `BME280_I2C_ADDRESS` | `0x77` | Sensor I²C address (`0x77` or `0x76` depending on SDO pin) |
| `BME280_IIR_FILTER` | `0` | IIR filter coefficient: `0`=off, `1`=2×, `2`=4×, `3`=8×, `4`=16× (recommended: `2` for indoor use) |
| `MQTT_BROKER_HOST` | `localhost` | IP or hostname of your MQTT broker |
| `MQTT_USERNAME` | _(empty)_ | MQTT username (leave empty for anonymous) |
| `MQTT_PASSWORD` | _(empty)_ | MQTT password |
| `MQTT_CLIENT_ID` | `rpi-bme280` | MQTT client identifier |
| `FLASK_PORT` | `5000` | HTTP port for the API |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode (`true` / `false`) |

**Example `.env`:**

```ini
BME280_I2C_BUS=1
BME280_I2C_ADDRESS=0x77
BME280_IIR_FILTER=0

MQTT_BROKER_HOST=192.168.1.10
MQTT_USERNAME=homeassistant
MQTT_PASSWORD=your_password_here
MQTT_CLIENT_ID=rpi-bme280

FLASK_PORT=5000
FLASK_DEBUG=false
```

---

## 🚀 Usage

### CLI

Read sensor data directly from the terminal (requires hardware):

```bash
python bme280.py
```

```
Chip ID  : 96
Version  : 0
Temperature : 21.55 °C
Pressure    : 1005.16 hPa
Humidity    : 44.57 %RH
```

Use an alternate I²C address:

```bash
BME280_I2C_ADDRESS=0x76 python bme280.py
```

### HTTP API

Start the API server:

```bash
python sensor_api.py
# Listening on http://0.0.0.0:5000
```

```bash
# Health check
curl http://rpi.local:5000/health

# Read sensor data
curl http://rpi.local:5000/bme280 | python -m json.tool

# Publish to MQTT
curl http://rpi.local:5000/bme280/publish
```

#### Automate with cron

Publish sensor data every minute via cron:

```bash
crontab -e
```

```cron
* * * * * curl -s http://localhost:5000/bme280/publish >> /var/log/bme280.log 2>&1
```

### Docker

#### Run the API in Docker (Raspberry Pi)

```bash
# Build the app image
docker build --target app -t bme280-app .

# Run with I²C device passthrough and env file
docker run -d \
  --name bme280 \
  --device /dev/i2c-1:/dev/i2c-1 \
  --env-file .env \
  -p 5000:5000 \
  bme280-app
```

Or with docker compose:

```bash
# Edit docker-compose.yml and uncomment the devices section
docker compose up app
```

#### Run tests in Docker (no hardware required)

```bash
docker compose run --rm test
# or
docker build --target test -t bme280-test . && docker run --rm bme280-test
```

---

## 📡 API Reference

### `GET /health`

Service health check.

**Response `200`:**
```json
{
  "status": "ok"
}
```

---

### `GET /`

Root endpoint.

**Response `200`:**
```json
{}
```

---

### `GET /bme280`

Returns current sensor readings with full device metadata.

**Response `200`:**
```json
{
  "name": "bme280",
  "brand": "Waveshare",
  "part_number": "BME280 Environmental Sensor",
  "sku": 15231,
  "upc": 614961952638,
  "chip": {
    "id": 96,
    "version": 0
  },
  "capabilities": {
    "temperature": {
      "unit_of_measurement": "°C",
      "min": -40,
      "max": 85,
      "resolution": 0.01,
      "accuracy": 1
    },
    "humidity": {
      "unit_of_measurement": "%RH",
      "min": 0,
      "max": 100,
      "resolution": 0.008,
      "accuracy": 3
    },
    "pressure": {
      "unit_of_measurement": "hPa",
      "min": 300,
      "max": 1100,
      "resolution": 0.008,
      "accuracy": 0.0018
    }
  },
  "data": {
    "temperature": 21.55,
    "humidity": 44.57,
    "pressure": 1005.16
  }
}
```

**Response `503`** — sensor unavailable (I²C error):
```json
{
  "error": "Sensor unavailable",
  "detail": "[Errno 2] No such file or directory: '/dev/i2c-1'"
}
```

---

### `GET /bme280/publish`

Reads sensor data and publishes each measurement to the configured MQTT broker.

**MQTT topics published:**

| Topic | Payload | Example |
|-------|---------|---------|
| `sensor/bme280_temperature` | float string | `21.55` |
| `sensor/bme280_humidity` | float string | `44.57` |
| `sensor/bme280_pressure` | float string | `1005.16` |

**Response `200`:**
```json
{
  "published": true,
  "topics": [
    "sensor/bme280_temperature",
    "sensor/bme280_humidity",
    "sensor/bme280_pressure"
  ]
}
```

**Response `503`** — sensor unavailable:
```json
{
  "error": "Sensor unavailable",
  "detail": "..."
}
```

**Response `502`** — MQTT broker unreachable:
```json
{
  "error": "MQTT publish failed",
  "detail": "Connection refused"
}
```

---

## 🏠 Home Assistant Integration

### Manual MQTT sensors

Add to your `configuration.yaml`:

```yaml
mqtt:
  sensor:
    - name: "BME280 Temperature"
      state_topic: "sensor/bme280_temperature"
      unit_of_measurement: "°C"
      device_class: temperature
      state_class: measurement

    - name: "BME280 Humidity"
      state_topic: "sensor/bme280_humidity"
      unit_of_measurement: "%"
      device_class: humidity
      state_class: measurement

    - name: "BME280 Pressure"
      state_topic: "sensor/bme280_pressure"
      unit_of_measurement: "hPa"
      device_class: atmospheric_pressure
      state_class: measurement
```

### Automation example

Trigger an alert when humidity exceeds 70%:

```yaml
automation:
  - alias: "High humidity alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.bme280_humidity
        above: 70
    action:
      - service: notify.mobile_app
        data:
          message: "⚠️ Humidity is {{ states('sensor.bme280_humidity') }}%"
```

---

## 🛠️ Development

### Install dev dependencies

```bash
pip install -r requirements-dev.txt
```

### Run the test suite

```bash
pytest tests/ -v
```

```
tests/test_api.py::test_health_returns_ok PASSED
tests/test_api.py::test_index_returns_empty_json PASSED
tests/test_api.py::test_bme280_returns_sensor_data PASSED
tests/test_api.py::test_bme280_returns_503_when_sensor_unavailable PASSED
tests/test_api.py::test_publish_returns_200_with_topics PASSED
tests/test_api.py::test_publish_returns_503_when_sensor_unavailable PASSED
tests/test_api.py::test_publish_returns_502_when_mqtt_fails PASSED
tests/test_bme280.py::test_get_short_positive PASSED
tests/test_bme280.py::test_get_short_negative PASSED
tests/test_bme280.py::test_get_ushort PASSED
tests/test_bme280.py::test_get_char_positive PASSED
tests/test_bme280.py::test_get_char_negative PASSED
tests/test_bme280.py::test_get_uchar PASSED
tests/test_bme280.py::test_read_id_returns_chip_id_and_version PASSED
tests/test_bme280.py::test_read_id_custom_chip_id PASSED
tests/test_bme280.py::test_sensor_returns_required_keys PASSED
tests/test_bme280.py::test_sensor_data_has_three_measurements PASSED
tests/test_bme280.py::test_humidity_clamped_within_range PASSED
tests/test_bme280.py::test_pressure_zero_when_p1_calibration_is_zero PASSED

19 passed in 0.22s
```

> 💡 All tests run without physical hardware — `smbus2` is fully mocked via `unittest.mock`.

### Run tests in Docker

```bash
docker compose run --rm test
```

---

## 📁 Project Structure

```
bme280/
├── 📄 bme280.py              # I²C driver — Bosch calibration algorithms
├── 📄 sensor_api.py          # Flask HTTP API + MQTT publisher
│
├── 🧪 tests/
│   ├── test_bme280.py        # Driver unit tests (hardware mocked)
│   └── test_api.py           # API route tests (Flask test client)
│
├── 🐳 Dockerfile             # Multi-stage: test / app
├── 🐳 docker-compose.yml     # test + app services
│
├── ⚙️  .env.example           # Configuration template
├── 📋 requirements.txt       # Runtime dependencies
├── 📋 requirements-dev.txt   # Dev/test dependencies
├── 🔧 pytest.ini             # Pytest configuration
└── 🔒 .gitignore
```

### Key dependencies

| Package | Version | Role |
|---------|---------|------|
| `smbus2` | ≥ 0.4.3 | I²C communication |
| `flask` | ≥ 3.0.0 | HTTP API framework |
| `paho-mqtt` | ≥ 1.6.1 | MQTT client |
| `python-dotenv` | ≥ 1.0.0 | `.env` file loading |

---

## 📊 Sensor Specifications

| Measurement | Range | Resolution | Accuracy |
|-------------|-------|------------|----------|
| 🌡️ Temperature | -40 °C → +85 °C | 0.01 °C | ± 1 °C |
| 💧 Humidity | 0 → 100 %RH | 0.008 %RH | ± 3 %RH |
| 🔵 Pressure | 300 → 1100 hPa | 0.008 hPa | ± 0.0018 hPa |

---

*Bosch BME280 datasheet: [BST-BME280-DS002][bme280-datasheet]*

[bme280-datasheet]: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf
