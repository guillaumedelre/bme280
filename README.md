# bme280

## BME280 driver

Run `python bme280.py` in a shell to get the sensor's data, it will output:

```
Chip ID     : 96
Version     : 0
Temperature : 21.04 °C
Pressure    : 1001.86890002 hPa
Humidity    : 52.7615936619 %RH
```

## Http API

Run `python sensor-api.py` to expose the http api on port `5000`.

### Endpoints

| Path | Status | Data | Comment |
|---|---|---|---|
| `/` | 200 | `{}` | nc |
| `/bme280` | 200 | [Sensor Resource](#sensor-resource) | return the sensor resource with measure |
| `/bme280/publish` | 200 | `{}` | publish in mqtt the sensor measure |

### Resource

```json

{
  "sku": 15231,
  "name": "bme280",
  "brand": "Waveshare",
  "upc": 614961952638,
  "capabilities": {
    "pressure": {
      "unit_of_measurement": "hPa",
      "max": 1100,
      "accuracy": 0.0018,
      "resolution": 0.008,
      "min": 300
    },
    "temperature": {
      "unit_of_measurement": "\u00b0C",
      "max": 85,
      "accuracy": 1,
      "resolution": 0.01,
      "min": -40
    },
    "humidity": {
      "unit_of_measurement": "%RH",
      "max": 100,
      "accuracy": 3,
      "resolution": 0.008,
      "min": 0
    }
  },
  "part_number": "BME280 Environmental Sensor",
  "data": {
    "pressure": 1005.1562396432168,
    "temperature": 21.55,
    "humidity": 44.566495623372525
  },
  "chip": {
    "version": 0,
    "id": 96
  }
}
```

## Setup the crontab

This is a cron job that actually sends the data via mqtt by calling the API every minute.

`* * * * * curl 192.168.86.31:5000/bme280/publish`
