import time
import paho.mqtt.client as mqtt
from sensor import Sensor
from flask import Flask, jsonify

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

username = 'homeassistant'
password = 'chi6pa9tiom3chahhohB7sienicae2aimimeefei4queol7eesuthohcai6maiph'
client_id = 'rpi3b-bme280' + str(int(time.time()))
broker_host = '192.168.86.35'
temperature_topic = 'sensor/bme280_temperature'
humidity_topic = 'sensor/bme280_humidity'
pressure_topic = 'sensor/bme280_pressure'

@app.route('/')
def index():
    return jsonify({})

@app.route('/bme280')
def bme280_action():
    return jsonify(Sensor().state())

@app.route('/bme280/publish')
def bme280_publish_action():
    sensor = Sensor()

    hass_mqtt = mqtt.Client(client_id)
    hass_mqtt.username_pw_set(username, password)
    hass_mqtt.connect(broker_host)

    hass_mqtt.publish(temperature_topic, sensor.temperature())
    hass_mqtt.publish(humidity_topic, sensor.humidity())
    hass_mqtt.publish(pressure_topic, sensor.pressure())

    return jsonify({})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
