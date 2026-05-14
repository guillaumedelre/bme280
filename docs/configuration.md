# ⚙️ Configuration

All settings are driven by environment variables. Copy `.env.example` to `.env` and fill in your values.

```bash
cp .env.example .env
```

> 🔒 `.env` is listed in `.gitignore` — it will never be committed.

## Reference

### Sensor (I²C)

| Variable | Default | Description |
|----------|---------|-------------|
| `BME280_I2C_BUS` | `1` | I²C bus number (`1` for Pi Rev 2+, `0` for Rev 1) |
| `BME280_I2C_ADDRESS` | `0x77` | Sensor I²C address (`0x77` or `0x76` depending on SDO pin wiring) |
| `BME280_IIR_FILTER` | `0` | IIR filter coefficient: `0`=off, `1`=2×, `2`=4×, `3`=8×, `4`=16× |

> 💡 For indoor use (stable environment), `BME280_IIR_FILTER=2` (4× coefficient) smooths out pressure spikes from door slams or air currents.

### MQTT

| Variable | Default | Description |
|----------|---------|-------------|
| `MQTT_BROKER_HOST` | `localhost` | IP or hostname of your MQTT broker |
| `MQTT_USERNAME` | _(empty)_ | MQTT username (leave empty for anonymous connections) |
| `MQTT_PASSWORD` | _(empty)_ | MQTT password |
| `MQTT_CLIENT_ID` | `rpi-bme280` | MQTT client identifier — must be unique per broker |

### Flask API

| Variable | Default | Description |
|----------|---------|-------------|
| `FLASK_PORT` | `5000` | HTTP port for the API server |
| `FLASK_DEBUG` | `false` | Enable Flask debug mode (`true` / `false`) — keep `false` in production |

## Example `.env`

```ini
# Sensor
BME280_I2C_BUS=1
BME280_I2C_ADDRESS=0x77
BME280_IIR_FILTER=0

# MQTT
MQTT_BROKER_HOST=192.168.1.10
MQTT_USERNAME=rpi-bme280
MQTT_PASSWORD=your_password_here
MQTT_CLIENT_ID=rpi-bme280

# Flask
FLASK_PORT=5000
FLASK_DEBUG=false
```
