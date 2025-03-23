import smbus2
from time import sleep

class TSL2591Sensor:
    def __init__(self, bus, address):
        self.bus = bus
        self.address = address
        try:
            self.initialize()
        except Exception as e:
            raise Exception(f"Failed to initialize TSL2591: {str(e)}")

    def initialize(self):
        # Enable the device
        self.bus.write_byte_data(self.address, 0xA0, 0x03)
        # Set gain and integration time
        self.bus.write_byte_data(self.address, 0xA1, 0x12)
        sleep(0.1)

    def read(self):
        try:
            # Read visible + IR channel
            data = self.bus.read_i2c_block_data(self.address, 0xB4, 4)
            ch0 = (data[1] << 8) | data[0]
            ch1 = (data[3] << 8) | data[2]

            # Calculate lux
            lux = self.calculate_lux(ch0, ch1)

            return {
                'visible_light': ch0,
                'ir_light': ch1,
                'lux': lux
            }
        except Exception as e:
            raise Exception(f"Failed to read TSL2591: {str(e)}")

    def calculate_lux(self, ch0, ch1):
        # Simplified lux calculation
        return (ch0 - ch1) * 0.6
