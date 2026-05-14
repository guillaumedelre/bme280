# 📡 API Reference

Base URL: `http://<raspberry-pi-host>:5000`

---

## `GET /health`

Service liveness check.

**Response `200`:**
```json
{
  "status": "ok"
}
```

---

## `GET /`

Root endpoint.

**Response `200`:**
```json
{}
```

---

## `GET /bme280`

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

## `GET /bme280/publish`

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

## Error handling summary

| HTTP Status | Meaning | Trigger |
|-------------|---------|---------|
| `200` | Success | Normal operation |
| `503` | Sensor unavailable | I²C bus error, sensor disconnected |
| `502` | Bad gateway | MQTT broker unreachable or refused connection |
