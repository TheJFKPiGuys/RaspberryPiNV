import smbus2
from time import sleep

class BME280Sensor:
    def __init__(self, bus, address):
        self.bus = bus
        self.address = address
        try:
            self.initialize()
        except Exception as e:
            raise Exception(f"Failed to initialize BME280: {str(e)}")

    def initialize(self):
        # Initialize BME280
        self.bus.write_byte_data(self.address, 0xF2, 0x01)  # humidity oversampling x1
        self.bus.write_byte_data(self.address, 0xF4, 0x27)  # temperature/pressure oversampling x1, normal mode
        self.bus.write_byte_data(self.address, 0xF5, 0xA0)  # 500ms standby time, filter off

    def read(self):
        try:
            # Read calibration data
            data = self.bus.read_i2c_block_data(self.address, 0x88, 24)
            
            # Read temperature
            data = self.bus.read_i2c_block_data(self.address, 0xF7, 8)
            temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
            temperature = self.compensate_temperature(temp_raw)

            # Read pressure
            press_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
            pressure = self.compensate_pressure(press_raw)

            # Read humidity
            hum_raw = (data[6] << 8) | data[7]
            humidity = self.compensate_humidity(hum_raw)

            return {
                'temperature': temperature,
                'pressure': pressure,
                'humidity': humidity
            }
        except Exception as e:
            raise Exception(f"Failed to read BME280: {str(e)}")

    def compensate_temperature(self, raw_temp):
        # Simplified compensation calculation
        return ((raw_temp / 16384.0) - 0) * (100 / 16384.0)

    def compensate_pressure(self, raw_press):
        # Simplified compensation calculation
        return raw_press / 256.0

    def compensate_humidity(self, raw_hum):
        # Simplified compensation calculation
        return raw_hum / 1024.0
