import random
from time import time
from config import DEVICE_ID, LATITUDE, LONGITUDE

class MockSensor:
    def get_mock_data(self):
        return {
            'timestamp': time(),
            'device_id': DEVICE_ID,
            'location': {
                'latitude': LATITUDE,
                'longitude': LONGITUDE
            },
            'bme280': {
                'temperature': random.uniform(20.0, 30.0),
                'pressure': random.uniform(980.0, 1020.0),
                'humidity': random.uniform(30.0, 70.0)
            },
            'tsl2591': {
                'visible_light': random.uniform(100, 1000),
                'ir_light': random.uniform(50, 500),
                'lux': random.uniform(0, 1000)
            },
            'ltr390': {
                'uv_raw': random.uniform(0, 10000),
                'uv_index': random.uniform(0, 11)
            },
            'icm20948': {
                'accelerometer': {
                    'x': random.uniform(-4.0, 4.0),
                    'y': random.uniform(-4.0, 4.0),
                    'z': random.uniform(-4.0, 4.0)
                },
                'gyroscope': {
                    'x': random.uniform(-2000, 2000),
                    'y': random.uniform(-2000, 2000),
                    'z': random.uniform(-2000, 2000)
                }
            },
            'sgp40': {
                'voc_raw': random.uniform(0, 65535),
                'voc_index': random.uniform(0, 500)
            }
        }