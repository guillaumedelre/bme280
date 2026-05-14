# 📁 Project Structure

```
bme280/
├── bme280.py               # I²C driver — Bosch calibration algorithms
├── sensor_api.py           # Flask HTTP API + MQTT publisher
│
├── tests/
│   ├── test_bme280.py      # Driver unit tests (hardware mocked)
│   └── test_api.py         # API route tests (Flask test client)
│
├── docs/
│   ├── hardware.md         # Components, wiring, I²C address
│   ├── architecture.md     # System diagram, component descriptions
│   ├── installation.md     # Prerequisites, clone, configure
│   ├── configuration.md    # Full environment variable reference
│   ├── usage.md            # CLI, HTTP API, cron, Docker
│   ├── api-reference.md    # Endpoint documentation with examples
│   ├── home-assistant.md   # MQTT auto-discovery, HA integration
│   ├── development.md      # Test suite, lint, CI pipeline
│   └── project-structure.md
│
├── .github/
│   └── workflows/
│       └── ci.yml          # CI: lint, test, security (pip-audit)
│
├── Dockerfile              # Multi-stage: test target + app target
├── docker-compose.yml      # Services: test, app
│
├── .env.example            # Configuration template
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Dev/test dependencies
├── pytest.ini              # Pytest configuration
└── .gitignore
```

## Key dependencies

| Package | Version | Role |
|---------|---------|------|
| `smbus2` | >= 0.4.3 | I²C communication via `/dev/i2c-*` |
| `flask` | >= 3.0.0 | HTTP API framework |
| `paho-mqtt` | >= 1.6.1 | MQTT client (fire-and-forget publish) |
| `python-dotenv` | >= 1.0.0 | `.env` file loading at startup |

Dev/test only:

| Package | Version | Role |
|---------|---------|------|
| `pytest` | >= 8.0.0 | Test runner |
| `pytest-flask` | >= 1.3.0 | Flask test client fixture |
| `flake8` | >= 7.0.0 | Style linter (PEP 8, max line 120) |
| `mypy` | >= 1.0.0 | Static type checker |

## Sensor Specifications

| Measurement | Range | Resolution | Accuracy |
|-------------|-------|------------|----------|
| Temperature | -40 °C to +85 °C | 0.01 °C | +/- 1 °C |
| Humidity | 0 to 100 %RH | 0.008 %RH | +/- 3 %RH |
| Pressure | 300 to 1100 hPa | 0.008 hPa | +/- 0.0018 hPa |

[BME280 datasheet][bme280-datasheet]

[bme280-datasheet]: https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf
