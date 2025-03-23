import smbus2
from time import sleep

class ICM20948Sensor:
    def __init__(self, bus, address):
        self.bus = bus
        self.address = address
        try:
            self.initialize()
        except Exception as e:
            raise Exception(f"Failed to initialize ICM20948: {str(e)}")

    def initialize(self):
        # Wake up the device
        self.bus.write_byte_data(self.address, 0x06, 0x00)
        # Configure accelerometer and gyroscope
        self.bus.write_byte_data(self.address, 0x07, 0x00)
        sleep(0.1)

    def read(self):
        try:
            # Read accelerometer data
            data = self.bus.read_i2c_block_data(self.address, 0x2D, 6)
            accel_x = (data[0] << 8) | data[1]
            accel_y = (data[2] << 8) | data[3]
            accel_z = (data[4] << 8) | data[5]

            # Read gyroscope data
            data = self.bus.read_i2c_block_data(self.address, 0x33, 6)
            gyro_x = (data[0] << 8) | data[1]
            gyro_y = (data[2] << 8) | data[3]
            gyro_z = (data[4] << 8) | data[5]

            return {
                'accelerometer': {
                    'x': self.convert_accel(accel_x),
                    'y': self.convert_accel(accel_y),
                    'z': self.convert_accel(accel_z)
                },
                'gyroscope': {
                    'x': self.convert_gyro(gyro_x),
                    'y': self.convert_gyro(gyro_y),
                    'z': self.convert_gyro(gyro_z)
                }
            }
        except Exception as e:
            raise Exception(f"Failed to read ICM20948: {str(e)}")

    def convert_accel(self, raw_value):
        # Convert to g (±4g range)
        return raw_value * 4.0 / 32768.0

    def convert_gyro(self, raw_value):
        # Convert to degrees per second (±2000dps range)
        return raw_value * 2000.0 / 32768.0
