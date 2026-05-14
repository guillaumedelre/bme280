# 🛠️ Development

## Install dev dependencies

```bash
pip install -r requirements-dev.txt
```

## Run the test suite

```bash
pytest tests/ -v
```

Expected output:

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
tests/test_bme280.py::test_nvm_copy_timeout_raises_oserror PASSED
tests/test_bme280.py::test_sensor_returns_required_keys PASSED
tests/test_bme280.py::test_sensor_data_has_three_measurements PASSED
tests/test_bme280.py::test_humidity_clamped_within_range PASSED
tests/test_bme280.py::test_pressure_zero_when_p1_calibration_is_zero PASSED

20 passed in 0.22s
```

> All tests run without physical hardware — `smbus2` is fully mocked via `unittest.mock`.

## Run tests in Docker

No hardware required. The `test` target in the Dockerfile installs dev dependencies and runs pytest.

```bash
docker compose run --rm test
# or directly:
docker build --target test -t bme280-test . && docker run --rm bme280-test
```

## Lint and type-check

```bash
# Style (PEP 8, max line length 120)
flake8 bme280.py sensor_api.py tests/

# Static type checking
mypy bme280.py sensor_api.py
```

Both tools are configured via `setup.cfg` / `pytest.ini` and run automatically in the GitHub Actions CI pipeline on every push to `develop`.

## CI pipeline

Three jobs run in parallel on each push:

| Job | Tool | What it checks |
|-----|------|----------------|
| `lint` | flake8 + mypy | Style and type correctness |
| `test` | Docker + pytest | All 20 unit tests (no hardware) |
| `security` | pip-audit | Known CVEs in dependencies |

See `.github/workflows/ci.yml` for the full configuration.

## Test architecture

### Driver tests (`tests/test_bme280.py`)

The I²C bus (`smbus2.SMBus`) is patched at the class level so no hardware is required:

```python
@patch("bme280.smbus2.SMBus")
def test_sensor_returns_required_keys(mock_smbus_cls: MagicMock) -> None:
    mock_smbus_cls.return_value.__enter__.return_value = make_mock_bus()
    result = sensor()
    assert "data" in result
```

The `make_mock_bus()` helper configures realistic `side_effect` sequences that mirror actual I²C traffic: chip ID read, NVM copy status, calibration registers, raw measurement bytes.

### API tests (`tests/test_api.py`)

The Flask test client is used with `sensor` and `mqtt_publish.multiple` patched:

```python
@patch("sensor_api.sensor")
def test_bme280_returns_sensor_data(mock_sensor: MagicMock, client: FlaskClient) -> None:
    mock_sensor.return_value = {...}
    response = client.get("/bme280")
    assert response.status_code == 200
```
