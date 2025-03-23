# Environmental Sensor and Solar Tracking System

This application reads data from a Waveshare Environment Sensor HAT and controls a solar panel position using a PiStep2 HAT stepper motor controller.

## Hardware Requirements

- Raspberry Pi (any model with I2C support)
- Waveshare Environment Sensor HAT
  - BME280 (Temperature, Pressure, Humidity)
  - TSL2591 (Light)
  - LTR-390UV-01 (UV)
  - ICM-20948 (Motion)
  - SGP40 (VOC)
- PiStep2 HAT (Stepper Motor Controller)
  - Controls solar panel east-west movement
  - 32 steps per revolution (11.25° per step)
  - 1/16 reduction gear ratio (516 total steps)
  - Automatic positioning based on sun position

## Solar Tracking System

The system automatically adjusts a solar panel's position from east to west throughout the day:

- At sunrise: Panel faces east (0% position)
- During day: Panel tracks sun's position (0-100% range)
- At sunset: Panel returns to east position for next morning
- Positioning calculated using astronomical data or mock time-based simulation

### Production Mode
Uses the Astral library to calculate precise sun positions based on:
- Device latitude/longitude
- Real-time astronomical calculations
- Actual sunrise/sunset times

### Mock Mode

The application includes a mock mode for development and testing on non-Raspberry Pi systems. Mock mode is automatically enabled when:

1. The USE_MOCK environment variable is set to 'true'
2. Required hardware (I2C bus or GPIO) is not available
3. Hardware initialization fails

In mock mode:
- Sensor data is simulated with realistic random values
- Solar tracking uses simplified time-based position calculation:
  - Fixed sunrise at 06:00 and sunset at 18:00
  - Linear position interpolation during daylight hours
  - East position (0%) during night hours
- Stepper motor movements are logged but not physically executed

## Configuration

Environment variables:
- ENDPOINT_URL: Data submission endpoint (default: https://httpbin.org/post for testing)
- READ_INTERVAL: Sensor reading interval in seconds (default: 60)
- USE_MOCK: Force mock mode ('true'/'false', default: 'false')
- DEVICE_ID: Unique identifier for this device (default: 'pi-0001')
- LATITUDE: Device location latitude (default: London)
- LONGITUDE: Device location longitude (default: London)

## Testing

Run the solar tracking test routine:
```bash
python tests/test_solar_tracking.py
```

This will simulate sun position calculations and stepper movements at different times of day:
- Tests panel positions at 04:00, 08:00, 12:00, 16:00, and 20:00
- Verifies correct positioning logic for night and day periods
- Logs detailed position calculations and motor movements

Example test output:
```
04:00 - Panel at east position (night time)
08:00 - Panel at 16.67% (2 hours after sunrise)
12:00 - Panel at 50% (midday)
16:00 - Panel at 83.33% (10 hours after sunrise)
20:00 - Panel back to east position (night time)