import smbus2
from time import sleep

class SGP40Sensor:
    def __init__(self, bus, address):
        self.bus = bus
        self.address = address
        try:
            self.initialize()
        except Exception as e:
            raise Exception(f"Failed to initialize SGP40: {str(e)}")

    def initialize(self):
        # Initialize SGP40
        self.bus.write_i2c_block_data(self.address, 0x20, [0x03])
        sleep(0.1)

    def read(self):
        try:
            # Measure VOC
            self.bus.write_i2c_block_data(self.address, 0x26, [0x0F])
            sleep(0.05)
            
            data = self.bus.read_i2c_block_data(self.address, 0x00, 3)
            voc_raw = (data[0] << 8) | data[1]
            
            return {
                'voc_raw': voc_raw,
                'voc_index': self.calculate_voc_index(voc_raw)
            }
        except Exception as e:
            raise Exception(f"Failed to read SGP40: {str(e)}")

    def calculate_voc_index(self, raw_value):
        # Convert raw value to VOC index (0-500)
        return min(500, max(0, int(raw_value / 65535 * 500)))
