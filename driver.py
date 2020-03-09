# -*- coding: utf-8 -*-
# !/usr/bin/python
# --------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#           bme280.py
#  Read data from a digital pressure sensor.
#
#  Official datasheet available from :
#  https://www.bosch-sensortec.com/bst/products/all_products/bme280
#
# Author : Matt Hawkins
# Date   : 21/01/2018
#
# https://www.raspberrypi-spy.co.uk/
#
# --------------------------------------
import smbus
import time
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte


class Driver:

    @staticmethod
    def get_short(data, index):
        # return two bytes from data as a signed 16-bit value
        return c_short((data[index + 1] << 8) + data[index]).value

    @staticmethod
    def get_u_short(data, index):
        # return two bytes from data as an unsigned 16-bit value
        return (data[index + 1] << 8) + data[index]

    @staticmethod
    def get_char(data, index):
        # return one byte from data as a signed char
        result = data[index]
        if result > 127:
            result -= 256
        return result

    @staticmethod
    def get_u_char(data, index):
        # return one byte from data as an unsigned char
        result = data[index] & 0xFF
        return result

    def read_bme280_id(self):
        addr = self.DEVICE
        # Chip ID Register Address
        reg_id = 0xD0
        (chip_id, chip_version) = self.bus.read_i2c_block_data(addr, reg_id, 2)
        return chip_id, chip_version

    def read_bme280_all(self):
        addr = self.DEVICE
        # Register Addresses
        reg_data = 0xF7
        reg_control = 0xF4

        reg_control_hum = 0xF2

        # Oversample setting - page 27
        oversample_temp = 2
        oversample_pres = 2
        mode = 1

        # Oversample setting for humidity register - page 26
        oversample_hum = 2
        self.bus.write_byte_data(addr, reg_control_hum, oversample_hum)

        control = oversample_temp << 5 | oversample_pres << 2 | mode
        self.bus.write_byte_data(addr, reg_control, control)

        # Read blocks of calibration data from EEPROM
        # See Page 22 data sheet
        cal1 = self.bus.read_i2c_block_data(addr, 0x88, 24)
        cal2 = self.bus.read_i2c_block_data(addr, 0xA1, 1)
        cal3 = self.bus.read_i2c_block_data(addr, 0xE1, 7)

        # Convert byte data to word values
        dig_t1 = self.get_u_short(cal1, 0)
        dig_t2 = self.get_short(cal1, 2)
        dig_t3 = self.get_short(cal1, 4)

        dig_p1 = self.get_u_short(cal1, 6)
        dig_p2 = self.get_short(cal1, 8)
        dig_p3 = self.get_short(cal1, 10)
        dig_p4 = self.get_short(cal1, 12)
        dig_p5 = self.get_short(cal1, 14)
        dig_p6 = self.get_short(cal1, 16)
        dig_p7 = self.get_short(cal1, 18)
        dig_p8 = self.get_short(cal1, 20)
        dig_p9 = self.get_short(cal1, 22)

        dig_h1 = self.get_u_char(cal2, 0)
        dig_h2 = self.get_short(cal3, 0)
        dig_h3 = self.get_u_char(cal3, 2)

        dig_h4 = self.get_char(cal3, 3)
        dig_h4 = (dig_h4 << 24) >> 20
        dig_h4 = dig_h4 | (self.get_char(cal3, 4) & 0x0F)

        dig_h5 = self.get_char(cal3, 5)
        dig_h5 = (dig_h5 << 24) >> 20
        dig_h5 = dig_h5 | (self.get_u_char(cal3, 4) >> 4 & 0x0F)

        dig_h6 = self.get_char(cal3, 6)

        # Wait in ms (Datasheet Appendix B: Measurement time and current calculation)
        wait_time = 1.25 + (2.3 * oversample_temp) + ((2.3 * oversample_pres) + 0.575) + (
                    (2.3 * oversample_hum) + 0.575)
        time.sleep(wait_time / 1000)  # Wait the required time

        # Read temperature/pressure/humidity
        data = self.bus.read_i2c_block_data(addr, reg_data, 8)
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        hum_raw = (data[6] << 8) | data[7]

        # Refine temperature
        var1 = ((temp_raw >> 3 - dig_t1 << 1) * dig_t2) >> 11
        var2 = (((((temp_raw >> 4) - dig_t1) * ((temp_raw >> 4) - dig_t1)) >> 12) * dig_t3) >> 14
        t_fine = var1 + var2
        temperature = float(((t_fine * 5) + 128) >> 8)

        # Refine pressure and adjust for temperature
        var1 = t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * dig_p6 / 32768.0
        var2 = var2 + var1 * dig_p5 * 2.0
        var2 = var2 / 4.0 + dig_p4 * 65536.0
        var1 = (dig_p3 * var1 * var1 / 524288.0 + dig_p2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * dig_p1
        if var1 == 0:
            pressure = 0
        else:
            pressure = 1048576.0 - pres_raw
            pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
            var1 = dig_p9 * pressure * pressure / 2147483648.0
            var2 = pressure * dig_p8 / 32768.0
            pressure = pressure + (var1 + var2 + dig_p7) / 16.0

        # Refine humidity
        humidity = t_fine - 76800.0
        humidity = (hum_raw - (dig_h4 * 64.0 + dig_h5 / 16384.0 * humidity)) * (
                    dig_h2 / 65536.0 * (1.0 + dig_h6 / 67108864.0 * humidity * (1.0 + dig_h3 / 67108864.0 * humidity)))
        humidity = humidity * (1.0 - dig_h1 * humidity / 524288.0)
        if humidity > 100:
            humidity = 100
        elif humidity < 0:
            humidity = 0

        return temperature / 100.0, pressure / 100.0, humidity

    def __init__(self):
        self.DEVICE = 0x77  # Default device I2C address

        '''
        Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
        Rev 1 Pi uses bus 0
        '''
        self.bus = smbus.SMBus(1)
