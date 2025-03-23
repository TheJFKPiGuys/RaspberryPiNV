import time
import logging
from typing import Optional

class StepperController:
    # PiStep2 HAT pin definitions
    DIR_PIN = 20    # Direction GPIO Pin
    STEP_PIN = 21   # Step GPIO Pin
    ENABLE_PIN = 16 # Enable GPIO Pin

    # Movement constants
    STEPS_PER_REV = 32       # 32 steps per revolution (11.25° per step)
    GEAR_RATIO = 16.128      # Exact 1/16.128 reduction gear ratio
    TOTAL_STEPS = int(STEPS_PER_REV * GEAR_RATIO)  # 516.096 steps rounded to 516

    def __init__(self, mock_mode: bool = False):
        self.current_position = 0  # 0 = east, TOTAL_STEPS = west
        self.mock_mode = mock_mode
        if not self.mock_mode:
            try:
                self.setup_gpio()
            except Exception as e:
                logging.error(f"Failed to initialize GPIO: {str(e)}")
                self.mock_mode = True

    def setup_gpio(self):
        """Initialize GPIO pins for stepper control."""
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.DIR_PIN, GPIO.OUT)
            GPIO.setup(self.STEP_PIN, GPIO.OUT)
            GPIO.setup(self.ENABLE_PIN, GPIO.OUT)

            # Enable the stepper driver
            GPIO.output(self.ENABLE_PIN, GPIO.LOW)

        except Exception as e:
            logging.error(f"Failed to initialize GPIO: {str(e)}")
            raise

    def move_to_position(self, target_position: float):
        """
        Move to a relative position (0.0 = east, 1.0 = west)
        """
        if self.mock_mode:
            logging.info(f"Mock stepper moved to position: {target_position:.2%}")
            return

        try:
            import RPi.GPIO as GPIO
            # Convert relative position to steps
            target_steps = int(target_position * self.TOTAL_STEPS)

            # Determine direction and steps needed
            steps_to_move = target_steps - self.current_position

            if steps_to_move == 0:
                logging.info("Panel already at target position")
                return

            # Set direction
            GPIO.output(self.DIR_PIN, GPIO.HIGH if steps_to_move > 0 else GPIO.LOW)
            direction = "west" if steps_to_move > 0 else "east"
            logging.info(f"Moving panel {direction}: {abs(steps_to_move)} steps")

            # Move the required number of steps
            for _ in range(abs(steps_to_move)):
                GPIO.output(self.STEP_PIN, GPIO.HIGH)
                time.sleep(0.001)  # 1ms delay
                GPIO.output(self.STEP_PIN, GPIO.LOW)
                time.sleep(0.001)  # 1ms delay

            self.current_position = target_steps
            logging.info(f"Panel movement complete. Current position: {(self.current_position / self.TOTAL_STEPS):.2%}")

        except Exception as e:
            logging.error(f"Error moving stepper: {str(e)}")
            raise

    def cleanup(self):
        """Clean up GPIO on shutdown."""
        if self.mock_mode:
            return

        try:
            import RPi.GPIO as GPIO
            GPIO.output(self.ENABLE_PIN, GPIO.HIGH)  # Disable the driver
            GPIO.cleanup()
        except Exception as e:
            logging.error(f"Error during GPIO cleanup: {str(e)}")