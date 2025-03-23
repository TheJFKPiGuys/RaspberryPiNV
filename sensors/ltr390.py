import smbus2
from time import sleep

class LTR390Sensor:
    def __init__(self, bus, address):
        self.bus = bus
        self.address = address
        try:
            self.initialize()
        except Exception as e:
            raise Exception(f"Failed to initialize LTR390: {str(e)}")

    def initialize(self):
        # Enable UV measurement
        self.bus.write_byte_data(self.address, 0x00, 0x0A)
        # Set gain and resolution
        self.bus.write_byte_data(self.address, 0x04, 0x02)
        sleep(0.1)

    def read(self):
        try:
            # Read UV data
            data = self.bus.read_i2c_block_data(self.address, 0x0C, 3)
            uv_raw = (data[2] << 16) | (data[1] << 8) | data[0]
            
            # Calculate UV index
            uv_index = self.calculate_uv_index(uv_raw)

            return {
                'uv_raw': uv_raw,
                'uv_index': uv_index
            }
        except Exception as e:
            raise Exception(f"Failed to read LTR390: {str(e)}")

    def calculate_uv_index(self, raw_value):
        # Simplified UV index calculation
        return raw_value / 2300.0
