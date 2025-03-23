import time
import json
import logging
import requests
import smbus2
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from sensors import *
from motor import SunPredictor, StepperController
from config import *

# Set up logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sensor_app.log'),
        logging.StreamHandler()
    ]
)

class SensorManager:
    def __init__(self):
        self.mock_mode = USE_MOCK
        self.session = self._setup_requests_session()

        # Initialize sun tracking system
        try:
            self.stepper = StepperController(mock_mode=self.mock_mode)
            logging.info("Stepper motor controller initialized")
            self.sun_predictor = SunPredictor(LATITUDE, LONGITUDE)
            logging.info("Sun position predictor initialized")
        except Exception as e:
            logging.error(f"Failed to initialize sun tracking system: {str(e)}")
            if not self.mock_mode:
                self.mock_mode = True
                logging.info("Falling back to mock mode")

        if not self.mock_mode:
            try:
                self.bus = smbus2.SMBus(1)  # Use I2C bus 1
                self.bme280 = BME280Sensor(self.bus, BME280_ADDR)
                self.tsl2591 = TSL2591Sensor(self.bus, TSL2591_ADDR)
                self.ltr390 = LTR390Sensor(self.bus, LTR390_ADDR)
                self.icm20948 = ICM20948Sensor(self.bus, ICM20948_ADDR)
                self.sgp40 = SGP40Sensor(self.bus, SGP40_ADDR)
                logging.info("Hardware sensors initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize hardware sensors: {str(e)}")
                logging.info("Falling back to mock mode")
                self.mock_mode = True

        if self.mock_mode:
            self.mock_sensor = MockSensor()
            logging.info("Mock sensor initialized")

    def _setup_requests_session(self):
        session = requests.Session()
        retry_strategy = Retry(
            total=3,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4 seconds between retries
            status_forcelist=[408, 429, 500, 502, 503, 504]  # HTTP status codes to retry on
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def update_panel_position(self):
        """Update the solar panel position based on sun prediction."""
        try:
            if not self.mock_mode:
                position = self.sun_predictor.get_sun_position()
                self.stepper.move_to_position(position)
                logging.info(f"Updated panel position to {position:.2%} of east-west range")
        except Exception as e:
            logging.error(f"Failed to update panel position: {str(e)}")

    def read_sensors(self):
        try:
            if self.mock_mode:
                return self.mock_sensor.get_mock_data()

            data = {
                'timestamp': time.time(),
                'device_id': DEVICE_ID,
                'location': {
                    'latitude': LATITUDE,
                    'longitude': LONGITUDE
                },
                'bme280': self.bme280.read(),
                'tsl2591': self.tsl2591.read(),
                'ltr390': self.ltr390.read(),
                'icm20948': self.icm20948.read(),
                'sgp40': self.sgp40.read()
            }
            return data
        except Exception as e:
            logging.error(f"Error reading sensors: {str(e)}")
            raise

    def send_data(self, data):
        try:
            response = self.session.post(
                ENDPOINT_URL,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10  # increased timeout to 10 seconds
            )
            response.raise_for_status()
            logging.info(f"Data sent successfully to {ENDPOINT_URL}")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send data to endpoint: {str(e)}")
            return False

    def run(self):
        logging.info(f"Starting sensor readings ({'mock' if self.mock_mode else 'hardware'} mode)")
        logging.info(f"Sending data to: {ENDPOINT_URL}")
        logging.info(f"Reading interval: {READ_INTERVAL} seconds")

        try:
            while True:
                try:
                    # Update solar panel position
                    self.update_panel_position()

                    # Read and send sensor data
                    data = self.read_sensors()
                    self.send_data(data)
                    time.sleep(READ_INTERVAL)
                except Exception as e:
                    logging.error(f"Error in main loop: {str(e)}")
                    time.sleep(5)  # Wait before retrying
        finally:
            if not self.mock_mode:
                self.stepper.cleanup()  # Ensure proper cleanup of GPIO

if __name__ == "__main__":
    manager = SensorManager()
    manager.run()