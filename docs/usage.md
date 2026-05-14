# 🚀 Usage

## CLI

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

## HTTP API

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

See [API Reference](api-reference.md) for the full endpoint documentation.

## Automate with cron

Publish sensor data every minute:

```bash
crontab -e
```

```cron
* * * * * curl -s http://localhost:5000/bme280/publish >> /var/log/bme280.log 2>&1
```

## Docker

### Run the API (Raspberry Pi)

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

Or with docker compose (uncomment `devices` in `docker-compose.yml` first):

```bash
docker compose up app
```

### Run tests (no hardware required)

```bash
docker compose run --rm test
# or
docker build --target test -t bme280-test . && docker run --rm bme280-test
```
