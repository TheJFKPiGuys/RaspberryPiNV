import os
from dotenv import load_dotenv

load_dotenv()

# Sensor I2C addresses
BME280_ADDR = 0x76
TSL2591_ADDR = 0x29
LTR390_ADDR = 0x53
ICM20948_ADDR = 0x68
SGP40_ADDR = 0x59

# Configuration from environment variables
ENDPOINT_URL = os.getenv('ENDPOINT_URL', 'https://httpbin.org/post')  # Default to httpbin for testing
READ_INTERVAL = int(os.getenv('READ_INTERVAL', '60'))  # seconds
USE_MOCK = os.getenv('USE_MOCK', 'false').lower() == 'false'

# Device identification and location
DEVICE_ID = os.getenv('DEVICE_ID', 'pi-0001')  # Unique identifier for this device
LATITUDE = float(os.getenv('LATITUDE', '51.5007')) 
LONGITUDE = float(os.getenv('LONGITUDE', '0.1246'))