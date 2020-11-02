# try:
#     while True:
#         reading_time = datetime.utcnow()
#         for sensor in data.get_sensors():
#             #print(f'Sensor {sensor.id} type {sensor.sensor_type} pin {sensor.sensor_pin}')
#             humidity, temperature = Adafruit_DHT.read_retry(sensor.sensor_type, sensor.sensor_pin)
#             if valid_data(humidity,temperature):
#                 #print(f'Read from Sensor {sensor.id} humidity: {humidity:.0f} temperature: {temperature:.1f}')
#                 data.add_reading(reading_time, 'hum', round(humidity), sensor.id)
#                 data.add_reading(reading_time, 'temp', round(temperature,1), sensor.id)
#         time.sleep(2.0)
# finally:
#     True

import datetime
import Adafruit_DHT
import time
from app.models import DHTData #, Readings
data = DHTData()

try:
    while True:
        reading_time = datetime.datetime.utcnow()
        for sensor in data.get_sensors():
            #print(f'Sensor {sensor.id} type {sensor.sensor_type} pin {sensor.sensor_pin}')
            humidity, temperature = Adafruit_DHT.read_retry(sensor.sensor_type, sensor.sensor_pin)
            if data.consistence(humidity,temperature):
                if data.filtering(humidity,temperature):
                    #print(f'Read from Sensor {sensor.id} humidity: {round(humidity,1)} temperature: {round(temperature,1)}')
                    data.add_reading(reading_time, 'hum', round(humidity,1), sensor.id)
                    data.add_reading(reading_time, 'temp', round(temperature,1), sensor.id)
            else:
                print(f'{humidity} {temperature}')
        time.sleep(2.0)
finally:
    True