from unittest.mock import patch

import pytest


MOCK_SENSOR = {
    'name': 'bme280',
    'brand': 'Waveshare',
    'part_number': 'BME280 Environmental Sensor',
    'sku': 15231,
    'upc': 614961952638,
    'chip': {'id': 96, 'version': 0},
    'capabilities': {
        'temperature': {'unit_of_measurement': '°C', 'min': -40, 'max': 85, 'resolution': 0.01, 'accuracy': 1},
        'humidity': {'unit_of_measurement': '%RH', 'min': 0, 'max': 100, 'resolution': 0.008, 'accuracy': 3},
        'pressure': {'unit_of_measurement': 'hPa', 'min': 300, 'max': 1100, 'resolution': 0.008, 'accuracy': 0.0018},
    },
    'data': {'temperature': 21.55, 'humidity': 44.57, 'pressure': 1005.16},
}


@pytest.fixture
def client():
    import sensor_api
    sensor_api.app.config['TESTING'] = True
    return sensor_api.app.test_client()


# --- Health / index ---

def test_health_returns_ok(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.json['status'] == 'ok'


def test_index_returns_empty_json(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.json == {}


# --- /bme280 ---

def test_bme280_returns_sensor_data(client):
    with patch('sensor_api.bme280.sensor', return_value=MOCK_SENSOR):
        resp = client.get('/bme280')
    assert resp.status_code == 200
    assert resp.json['name'] == 'bme280'
    assert resp.json['data']['temperature'] == 21.55


def test_bme280_returns_503_when_sensor_unavailable(client):
    with patch('sensor_api.bme280.sensor', side_effect=OSError('No such file: /dev/i2c-1')):
        resp = client.get('/bme280')
    assert resp.status_code == 503
    assert resp.json['error'] == 'Sensor unavailable'


# --- /bme280/publish ---

def test_publish_returns_200_with_topics(client):
    with patch('sensor_api.bme280.sensor', return_value=MOCK_SENSOR):
        with patch('sensor_api.mqtt_publish.multiple'):
            resp = client.get('/bme280/publish')
    assert resp.status_code == 200
    assert resp.json['published'] is True
    assert len(resp.json['topics']) == 3


def test_publish_returns_503_when_sensor_unavailable(client):
    with patch('sensor_api.bme280.sensor', side_effect=OSError('I2C error')):
        resp = client.get('/bme280/publish')
    assert resp.status_code == 503


def test_publish_returns_502_when_mqtt_fails(client):
    with patch('sensor_api.bme280.sensor', return_value=MOCK_SENSOR):
        with patch('sensor_api.mqtt_publish.multiple', side_effect=Exception('Connection refused')):
            resp = client.get('/bme280/publish')
    assert resp.status_code == 502
    assert resp.json['error'] == 'MQTT publish failed'
