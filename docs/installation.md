# 📦 Installation

## Prerequisites

- Raspberry Pi Rev 2+ with Raspbian / Raspberry Pi OS
- BME280 sensor wired via I²C (see [Hardware](hardware.md))
- Python 3.10+
- I²C enabled on the Pi

```bash
# Enable I²C
sudo raspi-config   # Interface Options → I2C → Enable
sudo reboot
```

## Clone & install

```bash
git clone https://github.com/guillaumedelre/bme280.git
cd bme280

pip install -r requirements.txt
```

## Configure

```bash
cp .env.example .env
nano .env   # fill in your MQTT broker details
```

See [Configuration](configuration.md) for the full list of available variables.

## Verify hardware

```bash
# Check the sensor is detected on the I²C bus
i2cdetect -y 1
# Address 0x77 (or 0x76) should appear

# Run a quick CLI read
python bme280.py
```

Expected output:

```
Chip ID  : 96
Version  : 0
Temperature : 21.55 °C
Pressure    : 1005.16 hPa
Humidity    : 44.57 %RH
```

## Start the API

```bash
python sensor_api.py
# Listening on http://0.0.0.0:5000
```
