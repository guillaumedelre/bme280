from unittest.mock import MagicMock, patch

import pytest


def make_mock_bus(chip_id: int = 96, chip_version: int = 0) -> MagicMock:
    bus = MagicMock()
    bus.read_byte_data.return_value = 0  # 0xF3 status: NVM copy done, not measuring
    bus.read_i2c_block_data.side_effect = [
        [chip_id, chip_version],   # read_id
        [0] * 24,                  # cal1 - T and P calibration
        [0],                       # cal2 - H1
        [0] * 7,                   # cal3 - H2-H6
        [0] * 8,                   # raw sensor data
    ]
    return bus


@pytest.fixture
def patched_smbus():
    mock_bus = make_mock_bus()
    with patch('bme280.smbus2.SMBus') as MockSMBus:
        instance = MockSMBus.return_value
        instance.__enter__ = MagicMock(return_value=mock_bus)
        instance.__exit__ = MagicMock(return_value=False)
        yield mock_bus


# --- Helper functions (pure, no hardware) ---

def test_get_short_positive():
    from bme280 import _get_short
    assert _get_short([0x78, 0x6C], 0) == 27768  # 0x6C78


def test_get_short_negative():
    from bme280 import _get_short
    assert _get_short([0x00, 0xFF], 0) == -256  # 0xFF00 as signed


def test_get_ushort():
    from bme280 import _get_ushort
    assert _get_ushort([0x48, 0x67], 0) == 26440  # 0x6748


def test_get_char_positive():
    from bme280 import _get_char
    assert _get_char([50], 0) == 50


def test_get_char_negative():
    from bme280 import _get_char
    assert _get_char([200], 0) == -56  # 200 - 256


def test_get_uchar():
    from bme280 import _get_uchar
    assert _get_uchar([0xAB], 0) == 0xAB


# --- read_id ---

def test_read_id_returns_chip_id_and_version(patched_smbus):
    import bme280
    chip_id, chip_version = bme280.read_id()
    assert chip_id == 96
    assert chip_version == 0


def test_read_id_custom_chip_id():
    bus = make_mock_bus(chip_id=96, chip_version=0)
    with patch('bme280.smbus2.SMBus') as MockSMBus:
        instance = MockSMBus.return_value
        instance.__enter__ = MagicMock(return_value=bus)
        instance.__exit__ = MagicMock(return_value=False)
        import bme280
        chip_id, _ = bme280.read_id()
        assert chip_id == 96


# --- sensor() structure ---

def test_sensor_returns_required_keys(patched_smbus):
    import bme280
    result = bme280.sensor()
    assert result['name'] == 'bme280'
    assert 'data' in result
    assert 'capabilities' in result
    assert 'chip' in result


def test_sensor_data_has_three_measurements(patched_smbus):
    import bme280
    data = bme280.sensor()['data']
    assert 'temperature' in data
    assert 'humidity' in data
    assert 'pressure' in data


def test_humidity_clamped_within_range(patched_smbus):
    import bme280
    result = bme280.sensor()
    assert 0.0 <= result['data']['humidity'] <= 100.0


def test_pressure_zero_when_p1_calibration_is_zero(patched_smbus):
    # P1=0 triggers the zero-division guard in the compensation formula
    import bme280
    result = bme280.sensor()
    assert result['data']['pressure'] == 0.0


def test_nvm_copy_timeout_raises_oserror():
    bus = MagicMock()
    bus.read_byte_data.return_value = 0x01  # NVM copy never completes
    with patch('bme280.smbus2.SMBus') as MockSMBus:
        instance = MockSMBus.return_value
        instance.__enter__ = MagicMock(return_value=bus)
        instance.__exit__ = MagicMock(return_value=False)
        import bme280
        with pytest.raises(OSError, match="NVM copy"):
            bme280.read_all()
