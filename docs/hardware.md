# 🔌 Hardware

## Components

| Component | Details |
|-----------|---------|
| **Sensor** | Bosch BME280 — Waveshare Environmental Sensor (SKU 15231) |
| **Board** | Raspberry Pi Rev 2+ (I²C bus 1) |
| **Interface** | I²C — default address `0x77`, alternate `0x76` (SDO pin) |
| **Protocol** | SMBus via `/dev/i2c-1` |

## Wiring (Raspberry Pi GPIO)

```
BME280          Raspberry Pi
──────          ────────────
VCC    ──────►  Pin 1  (3.3V)
GND    ──────►  Pin 6  (GND)
SDA    ──────►  Pin 3  (GPIO2 / SDA1)
SCL    ──────►  Pin 5  (GPIO3 / SCL1)
```

> 💡 Make sure I²C is enabled: `sudo raspi-config` → Interface Options → I2C → Enable

## I²C Address

The BME280 supports two I²C addresses depending on the SDO pin wiring:

| SDO pin | Address |
|---------|---------|
| GND | `0x76` |
| VCC | `0x77` (default) |

Override via environment variable: `BME280_I2C_ADDRESS=0x76` (see [Configuration](configuration.md)).

## Sensor Specifications

| Measurement | Range | Resolution | Accuracy |
|-------------|-------|------------|----------|
| 🌡️ Temperature | -40 °C → +85 °C | 0.01 °C | ± 1 °C |
| 💧 Humidity | 0 → 100 %RH | 0.008 %RH | ± 3 %RH |
| 🔵 Pressure | 300 → 1100 hPa | 0.008 hPa | ± 0.0018 hPa |

## Enabling I²C on Raspberry Pi

```bash
sudo raspi-config   # Interface Options → I2C → Enable
sudo reboot

# Verify the sensor is detected
i2cdetect -y 1
# Expected: address 0x77 (or 0x76) appears in the grid
```

---

*Bosch BME280 datasheet: [BST-BME280-DS002][bme280-datasheet]*

[bme280-datasheet]: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf
