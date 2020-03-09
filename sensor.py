# -*- coding: utf-8 -*-
# !/usr/bin/python

from driver import Driver


class Sensor(Driver):


    def dump(self):
        (chip_id, chip_version) = self.read_bme280_id()
        print "Chip ID     :", chip_id
        print "Version     :", chip_version

        temperature, pressure, humidity = self.read_bme280_all()

        print "Temperature :", temperature, "C"
        print "Pressure    :", pressure, "hPa"
        print "Humidity    :", humidity, "%RH"

    def state(self):
        (chip_id, chip_version) = self.read_bme280_id()
        temperature, pressure, humidity = self.read_bme280_all()
        sensor = {
            'name': 'bme280',
            'brand': 'Waveshare',
            'part_number': 'BME280 Environmental Sensor',
            'sku': 15231,
            'upc': 614961952638,
            'chip': {
                'id': chip_id,
                'version': chip_version,
            },
            'capabilities': {
                'temperature': {
                    'unit_of_measurement': '°C',
                    'min': -40,
                    'max': 85,
                    'resolution': 0.01,
                    'accuracy': 1,
                },
                'humidity': {
                    'unit_of_measurement': '%RH',
                    'min': 0,
                    'max': 100,
                    'resolution': 0.008,
                    'accuracy': 3,
                },
                'pressure': {
                    'unit_of_measurement': 'hPa',
                    'min': 300,
                    'max': 1100,
                    'resolution': 0.008,
                    'accuracy': 0.0018,
                },
            },
            'data': {
                'temperature': temperature,
                'humidity': humidity,
                'pressure': pressure,
            },
        }

        return sensor

    def temperature(self):
        return Sensor().state()['data']['temperature']

    def humidity(self):
        return Sensor().state()['data']['humidity']

    def pressure(self):
        return Sensor().state()['data']['pressure']