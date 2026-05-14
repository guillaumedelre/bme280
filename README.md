# 🌡️ BME280 Environmental Sensor

[![CI](https://github.com/guillaumedelre/bme280/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/guillaumedelre/bme280/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> Python 3 driver for the Bosch BME280 environmental sensor — reads temperature, pressure and humidity over I²C on a Raspberry Pi, and exposes them via a REST API with MQTT publishing for Home Assistant integration.

---

## Quick start

```bash
git clone https://github.com/guillaumedelre/bme280.git
cd bme280

pip install -r requirements.txt
cp .env.example .env   # fill in your MQTT broker details

python sensor_api.py   # API available at http://0.0.0.0:5000
```

```bash
curl http://rpi.local:5000/bme280
curl http://rpi.local:5000/bme280/publish
```

---

## Documentation

| Topic | File |
|-------|------|
| Hardware wiring and I²C setup | [docs/hardware.md](docs/hardware.md) |
| System architecture and data flow | [docs/architecture.md](docs/architecture.md) |
| Installation and prerequisites | [docs/installation.md](docs/installation.md) |
| Environment variable reference | [docs/configuration.md](docs/configuration.md) |
| CLI, HTTP API, cron, Docker usage | [docs/usage.md](docs/usage.md) |
| REST API endpoint reference | [docs/api-reference.md](docs/api-reference.md) |
| Home Assistant + MQTT integration | [docs/home-assistant.md](docs/home-assistant.md) |
| Test suite, lint, CI pipeline | [docs/development.md](docs/development.md) |
| Project structure and dependencies | [docs/project-structure.md](docs/project-structure.md) |

---

*Bosch BME280 datasheet: [BST-BME280-DS002][bme280-datasheet]*

[bme280-datasheet]: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf
