import os
import time
from ctypes import c_short

import smbus2

I2C_BUS = int(os.environ.get('BME280_I2C_BUS', '1'))
DEVICE_ADDRESS = int(os.environ.get('BME280_I2C_ADDRESS', '0x77'), 16)

# IIR filter coefficient: 0=off, 1=2, 2=4, 3=8, 4=16 (see datasheet table 28)
IIR_FILTER = int(os.environ.get('BME280_IIR_FILTER', '0'))


def _get_short(data: list[int], index: int) -> int:
    return c_short((data[index + 1] << 8) + data[index]).value


def _get_ushort(data: list[int], index: int) -> int:
    return (data[index + 1] << 8) + data[index]


def _get_char(data: list[int], index: int) -> int:
    result = data[index]
    if result > 127:
        result -= 256
    return result


def _get_uchar(data: list[int], index: int) -> int:
    return data[index] & 0xFF


def read_id(addr: int = DEVICE_ADDRESS) -> tuple[int, int]:
    with smbus2.SMBus(I2C_BUS) as bus:
        chip_id = bus.read_byte_data(addr, 0xD0)
    return chip_id, 0


def _wait_nvm_copy(bus: smbus2.SMBus, addr: int) -> None:
    """Poll status register until NVM copy is complete after soft reset."""
    for _ in range(5):
        if not (bus.read_byte_data(addr, 0xF3) & 0x01):
            return
        time.sleep(0.002)
    raise OSError("BME280 NVM copy did not complete after soft reset")


def read_all(addr: int = DEVICE_ADDRESS) -> tuple[float, float, float]:
    OVERSAMPLE_TEMP = 2
    OVERSAMPLE_PRES = 2
    OVERSAMPLE_HUM = 2
    MODE = 1

    with smbus2.SMBus(I2C_BUS) as bus:
        # Soft reset to ensure the sensor starts from a known state
        bus.write_byte_data(addr, 0xE0, 0xB6)
        time.sleep(0.002)  # 2ms startup delay (datasheet section 4.2)
        _wait_nvm_copy(bus, addr)

        bus.write_byte_data(addr, 0xF5, IIR_FILTER << 2)  # config: filter bits [4:2]
        bus.write_byte_data(addr, 0xF2, OVERSAMPLE_HUM)
        bus.write_byte_data(addr, 0xF4, OVERSAMPLE_TEMP << 5 | OVERSAMPLE_PRES << 2 | MODE)

        cal1 = bus.read_i2c_block_data(addr, 0x88, 24)
        cal2 = bus.read_i2c_block_data(addr, 0xA1, 1)
        cal3 = bus.read_i2c_block_data(addr, 0xE1, 7)

        # Datasheet Appendix B: minimum wait before first status check
        wait_ms = 1.25 + (2.3 * OVERSAMPLE_TEMP) + ((2.3 * OVERSAMPLE_PRES) + 0.575) + ((2.3 * OVERSAMPLE_HUM) + 0.575)
        time.sleep(wait_ms / 1000)

        # Poll measuring bit (0xF3 bit 3) until measurement is complete
        for _ in range(20):
            if not (bus.read_byte_data(addr, 0xF3) & 0x08):
                break
            time.sleep(0.001)

        data = bus.read_i2c_block_data(addr, 0xF7, 8)

    dig_T1 = _get_ushort(cal1, 0)
    dig_T2 = _get_short(cal1, 2)
    dig_T3 = _get_short(cal1, 4)

    dig_P1 = _get_ushort(cal1, 6)
    dig_P2 = _get_short(cal1, 8)
    dig_P3 = _get_short(cal1, 10)
    dig_P4 = _get_short(cal1, 12)
    dig_P5 = _get_short(cal1, 14)
    dig_P6 = _get_short(cal1, 16)
    dig_P7 = _get_short(cal1, 18)
    dig_P8 = _get_short(cal1, 20)
    dig_P9 = _get_short(cal1, 22)

    dig_H1 = _get_uchar(cal2, 0)
    dig_H2 = _get_short(cal3, 0)
    dig_H3 = _get_uchar(cal3, 2)

    dig_H4 = (_get_char(cal3, 3) << 24) >> 20 | (_get_char(cal3, 4) & 0x0F)
    dig_H5 = (_get_char(cal3, 5) << 24) >> 20 | (_get_uchar(cal3, 4) >> 4 & 0x0F)
    dig_H6 = _get_char(cal3, 6)

    pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
    hum_raw = (data[6] << 8) | data[7]

    # Temperature compensation - Bosch datasheet page 22
    var1 = ((((temp_raw >> 3) - (dig_T1 << 1))) * dig_T2) >> 11
    var2 = (((((temp_raw >> 4) - dig_T1) * ((temp_raw >> 4) - dig_T1)) >> 12) * dig_T3) >> 14
    t_fine = var1 + var2
    temperature = float(((t_fine * 5) + 128) >> 8)

    # Pressure compensation
    var1 = t_fine / 2.0 - 64000.0
    var2 = var1 * var1 * dig_P6 / 32768.0
    var2 = var2 + var1 * dig_P5 * 2.0
    var2 = var2 / 4.0 + dig_P4 * 65536.0
    var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
    var1 = (1.0 + var1 / 32768.0) * dig_P1
    pressure = 0.0
    if var1 != 0:
        pressure = 1048576.0 - pres_raw
        pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
        var1 = dig_P9 * pressure * pressure / 2147483648.0
        var2 = pressure * dig_P8 / 32768.0
        pressure = pressure + (var1 + var2 + dig_P7) / 16.0

    # Humidity compensation
    humidity = t_fine - 76800.0
    humidity = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * humidity)) * (
        dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * humidity * (1.0 + dig_H3 / 67108864.0 * humidity))
    )
    humidity = humidity * (1.0 - dig_H1 * humidity / 524288.0)
    humidity = max(0.0, min(100.0, humidity))

    return temperature / 100.0, pressure / 100.0, humidity


def sensor(addr: int = DEVICE_ADDRESS) -> dict:
    chip_id, chip_version = read_id(addr)
    temperature, pressure, humidity = read_all(addr)
    return {
        'name': 'bme280',
        'brand': 'Waveshare',
        'part_number': 'BME280 Environmental Sensor',
        'sku': 15231,
        'upc': 614961952638,
        'chip': {'id': chip_id, 'version': chip_version},
        'capabilities': {
            'temperature': {'unit_of_measurement': '°C', 'min': -40, 'max': 85, 'resolution': 0.01, 'accuracy': 1},
            'humidity': {'unit_of_measurement': '%RH', 'min': 0, 'max': 100, 'resolution': 0.008, 'accuracy': 3},
            'pressure': {
                'unit_of_measurement': 'hPa', 'min': 300, 'max': 1100, 'resolution': 0.008, 'accuracy': 0.0018,
            },
        },
        'data': {
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure,
        },
    }


if __name__ == '__main__':
    chip_id, chip_version = read_id()
    print(f"Chip ID  : {chip_id}")
    print(f"Version  : {chip_version}")
    temperature, pressure, humidity = read_all()
    print(f"Temperature : {temperature:.2f} °C")
    print(f"Pressure    : {pressure:.2f} hPa")
    print(f"Humidity    : {humidity:.2f} %RH")
