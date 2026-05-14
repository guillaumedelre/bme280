# 🏠 Home Assistant Integration

## How it works

```
BME280 sensor
    │  I²C
    ▼
bme280.py (driver)
    │  temperature / pressure / humidity
    ▼
sensor_api.py (Flask)
    │  GET /bme280/publish
    ▼
MQTT broker (Mosquitto)           ◄── Home Assistant polls topics
    │
    ├── sensor/bme280_temperature  →  21.55
    ├── sensor/bme280_humidity     →  44.57
    └── sensor/bme280_pressure     →  1005.16
                                        │
                                        ▼
                               Home Assistant dashboard
```

Every call to `/bme280/publish` (manually or via cron) pushes the three values to the broker. Home Assistant reads them in real time and updates the entity states.

---

## Prerequisites

### 1. Install Mosquitto in Home Assistant

In HA: **Settings → Add-ons → Mosquitto broker** → Install → Start.

> 💡 Enable "Start on boot" to survive reboots.

### 2. Create a dedicated MQTT user

**Settings → People → Users** → Add user (e.g. `rpi-bme280`). This user will be used by the Raspberry Pi to publish.

### 3. Enable the MQTT integration

**Settings → Devices & Services → Add integration → MQTT** → point to `localhost:1883` with the user created above.

### 4. Set credentials in `.env`

```ini
MQTT_BROKER_HOST=192.168.1.10   # HA host IP
MQTT_USERNAME=rpi-bme280
MQTT_PASSWORD=your_password
```

> 🔒 Never commit `.env` — it is listed in `.gitignore`.

---

## Option A — MQTT auto-discovery (recommended)

Home Assistant supports [MQTT discovery][ha-mqtt-discovery]: publish a JSON config payload once and the entity appears automatically in the UI — no `configuration.yaml` edit needed.

Run this once from the Pi (replace `<broker>` and credentials):

```bash
mosquitto_pub -h <broker> -u rpi-bme280 -P <password> \
  -t "homeassistant/sensor/bme280_temperature/config" \
  -m '{"name":"BME280 Temperature","state_topic":"sensor/bme280_temperature","unit_of_measurement":"°C","device_class":"temperature","state_class":"measurement","unique_id":"bme280_temperature"}'

mosquitto_pub -h <broker> -u rpi-bme280 -P <password> \
  -t "homeassistant/sensor/bme280_humidity/config" \
  -m '{"name":"BME280 Humidity","state_topic":"sensor/bme280_humidity","unit_of_measurement":"%","device_class":"humidity","state_class":"measurement","unique_id":"bme280_humidity"}'

mosquitto_pub -h <broker> -u rpi-bme280 -P <password> \
  -t "homeassistant/sensor/bme280_pressure/config" \
  -m '{"name":"BME280 Pressure","state_topic":"sensor/bme280_pressure","unit_of_measurement":"hPa","device_class":"atmospheric_pressure","state_class":"measurement","unique_id":"bme280_pressure"}'
```

The three entities appear under **Settings → Devices & Services → MQTT** within seconds.

---

## Option B — Manual MQTT sensors

If you prefer explicit config, add to your `configuration.yaml`:

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

Then: **Developer Tools → YAML → Check configuration → Restart**.

---

## Automation example

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

## Troubleshooting

| Symptom | Check |
|---------|-------|
| Entity stuck at `unavailable` | Verify cron is running: `crontab -l` |
| `502` on `/bme280/publish` | Broker unreachable — check `MQTT_BROKER_HOST` and broker is up |
| No entity in HA after discovery | Check discovery is enabled in MQTT integration settings |
| Wrong values | Confirm `BME280_I2C_ADDRESS` matches your wiring (`0x76` vs `0x77`) |

[ha-mqtt-discovery]: https://www.home-assistant.io/integrations/mqtt/#mqtt-discovery
