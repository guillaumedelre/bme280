# 🏗️ Architecture

## System Overview

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

## Components

### `bme280.py` — I²C Driver

Low-level sensor driver. Handles:

- Soft reset and NVM copy wait on each read (Bosch SensorAPI spec)
- Calibration data extraction from EEPROM registers (`0x88`, `0xA1`, `0xE1`)
- Raw data reading from `0xF7` (8 bytes: pressure, temperature, humidity)
- Bosch compensation algorithms (double-precision floating point)
- IIR filter configuration via register `0xF5`
- Measurement completion polling via status register `0xF3`

### `sensor_api.py` — HTTP API

Flask application exposing three routes:

| Route | Role |
|-------|------|
| `GET /health` | Service liveness check |
| `GET /bme280` | Returns full sensor reading as JSON |
| `GET /bme280/publish` | Reads sensor and publishes to MQTT broker |

All configuration (MQTT credentials, I²C address, Flask port) is loaded from environment variables via `python-dotenv`.

## Data Flow

```
BME280 chip  ──I²C──►  bme280.py  ──►  sensor_api.py  ──HTTP──►  client (curl / cron)
                                              │
                                         MQTT publish
                                              │
                                              ▼
                                       MQTT Broker
                                              │
                                              ▼
                                      Home Assistant
```
