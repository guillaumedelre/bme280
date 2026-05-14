import os
import bme280
from flask import Flask, jsonify
from dotenv import load_dotenv
from paho.mqtt import publish as mqtt_publish

load_dotenv()

app = Flask(__name__)
app.json.sort_keys = False

MQTT_BROKER_HOST = os.environ.get('MQTT_BROKER_HOST', 'localhost')
MQTT_USERNAME = os.environ.get('MQTT_USERNAME', '')
MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', '')
MQTT_CLIENT_ID = os.environ.get('MQTT_CLIENT_ID', 'rpi-bme280')

TEMPERATURE_TOPIC = 'sensor/bme280_temperature'
HUMIDITY_TOPIC = 'sensor/bme280_humidity'
PRESSURE_TOPIC = 'sensor/bme280_pressure'


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


@app.route('/')
def index():
    return jsonify({})


@app.route('/bme280')
def bme280_action():
    try:
        return jsonify(bme280.sensor())
    except OSError as e:
        return jsonify({'error': 'Sensor unavailable', 'detail': str(e)}), 503


@app.route('/bme280/publish')
def bme280_publish_action():
    try:
        data = bme280.sensor()
    except OSError as e:
        return jsonify({'error': 'Sensor unavailable', 'detail': str(e)}), 503

    auth = {'username': MQTT_USERNAME, 'password': MQTT_PASSWORD} if MQTT_USERNAME else None

    try:
        mqtt_publish.multiple(
            [
                {'topic': TEMPERATURE_TOPIC, 'payload': str(data['data']['temperature'])},
                {'topic': HUMIDITY_TOPIC, 'payload': str(data['data']['humidity'])},
                {'topic': PRESSURE_TOPIC, 'payload': str(data['data']['pressure'])},
            ],
            hostname=MQTT_BROKER_HOST,
            auth=auth,
            client_id=MQTT_CLIENT_ID,
        )
    except Exception as e:
        return jsonify({'error': 'MQTT publish failed', 'detail': str(e)}), 502

    return jsonify({
        'published': True,
        'topics': [TEMPERATURE_TOPIC, HUMIDITY_TOPIC, PRESSURE_TOPIC],
    })


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
