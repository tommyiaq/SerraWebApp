# from app import app, db
# from app.models import Readings, DHTData
# from datetime import datetime
# import Adafruit_DHT
# import time

# data = DHTData()

# try:
#     while True:
#         reading_time = datetime.utcnow()
#         for sensor in data.get_sensors():
#             #print(f'Sensor {sensor.id} type {sensor.sensor_type} pin {sensor.sensor_pin}')
#             humidity, temperature = Adafruit_DHT.read_retry(sensor.sensor_type, sensor.sensor_pin)
#             #print(f'Read from Sensor {sensor.id} humidity: {humidity:.0f} temperature: {temperature:.1f}')
#             data.add_reading(reading_time, 'hum', humidity, sensor.id)
#             data.add_reading(reading_time, 'temp', temperature, sensor.id)
#         time.sleep(2.0)
# finally:
#     True

from app import app, db
from app.models import Readings, DHTData
from datetime import datetime
import Adafruit_DHT
import time

data = DHTData()

def valid_data(humidity,temperature):
    if (humidity==None) or (temperature==None):
        return False
    elif ((humidity>= 1 and humidity<=100) and (temperature>= 1 and temperature<=100)):
        return True
    else:
        return False
try:
    while True:
        reading_time = datetime.utcnow()
        for sensor in data.get_sensors():
            #print(f'Sensor {sensor.id} type {sensor.sensor_type} pin {sensor.sensor_pin}')
            humidity, temperature = Adafruit_DHT.read_retry(sensor.sensor_type, sensor.sensor_pin)
            if valid_data(humidity,temperature):
                #print(f'Read from Sensor {sensor.id} humidity: {humidity:.0f} temperature: {temperature:.1f}')
                data.add_reading(reading_time, 'hum', round(humidity), sensor.id)
                data.add_reading(reading_time, 'temp', round(temperature,1), sensor.id)
        time.sleep(2.0)
finally:
    True