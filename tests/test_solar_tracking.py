"""Test routine for solar tracking system."""
import logging
import time
import sys
from datetime import datetime, timezone, timedelta
from os.path import dirname, abspath, join
from zoneinfo import ZoneInfo
sys.path.append(dirname(dirname(abspath(__file__))))

from motor import SunPredictor, StepperController
from config import LATITUDE, LONGITUDE

def test_solar_tracking():
    """Test routine for solar tracking system with mock data."""
    logging.info("Starting solar tracking test routine")

    # Initialize components
    stepper = StepperController(mock_mode=True)
    sun_predictor = SunPredictor(LATITUDE, LONGITUDE)
    sun_predictor.use_mock = True  # Force mock mode for testing

    # Test positions throughout the day
    test_hours = [4, 8, 12, 16, 20]  # Different times to test

    # Create a base time in GMT timezone
    local_tz = ZoneInfo("Europe/London")
    base_time = datetime.now(local_tz).replace(hour=0, minute=0, second=0, microsecond=0)

    # Expected positions in local time (0.0 = east, 1.0 = west)
    expected_positions = {
        4: 0.0,    # Before sunrise (6 AM): east position
        8: 0.167,  # 2 hours after sunrise: ~16.7%
        12: 0.5,   # Midday: 50%
        16: 0.833, # 10 hours after sunrise: ~83.3%
        20: 0.0,   # After sunset (6 PM): back to east
    }

    for hour in test_hours:
        logging.info(f"\nTesting solar tracking for hour: {hour:02d}:00")
        test_time = base_time + timedelta(hours=hour)
        position = sun_predictor.get_sun_position(test_time)

        # Verify position is within expected range
        expected = expected_positions[hour]
        assert abs(position - expected) < 0.01, \
            f"Position at {hour:02d}:00 ({position:.2%}) differs from expected ({expected:.2%})"

        stepper.move_to_position(position)
        time.sleep(1)

def test_production_mode():
    """Test solar tracking in production mode using real astronomical calculations."""
    logging.info("\nTesting solar tracking in production mode")

    sun_predictor = SunPredictor(LATITUDE, LONGITUDE)
    stepper = StepperController(mock_mode=True)  # Keep stepper in mock mode to avoid hardware requirements

    if not sun_predictor.use_mock:
        logging.info("Production mode active - using Astral for calculations")
        # Create test date in GMT timezone for consistent testing
        gmt_tz = ZoneInfo("Europe/London")
        base_time = datetime(2025, 6, 21, tzinfo=gmt_tz).replace(
            hour=0, minute=0, second=0, microsecond=0
        )  # Summer solstice for most predictable day length

        # Test different days of the year
        test_days = [
            base_time,  # Today
            base_time + timedelta(days=90),  # ~3 months ahead (Summer)
            base_time + timedelta(days=180), # ~6 months ahead (Fall)
            base_time + timedelta(days=270)  # ~9 months ahead (Winter)
        ]

        for test_day in test_days:
            logging.info(f"\nTesting seasonal variation: {test_day.strftime('%Y-%m-%d')}")

            # Test exact times of astronomical events
            s = sun_predictor.sun_calc(sun_predictor.location.observer, date=test_day.date())
            test_times = {
                'sunrise': s['sunrise'].astimezone(gmt_tz),
                'solar_noon': s['noon'].astimezone(gmt_tz),
                'sunset': s['sunset'].astimezone(gmt_tz)
            }

            expected_positions = {
                'sunrise': 0.0,      # Just at sunrise: east position
                'solar_noon': 0.5,   # Solar noon: middle position
                'sunset': 1.0        # Just at sunset: west position
            }

            for event, test_time in test_times.items():
                position = sun_predictor.get_sun_position(test_time)
                expected = expected_positions[event]

                logging.info(f"{event.replace('_', ' ').title()}: {test_time.strftime('%H:%M:%S %Z')}")
                logging.info(f"Position: {position:.2%} (Expected: {expected:.2%})")

                # Allow some deviation from exact positions due to seasonal variations
                max_deviation = 0.1  # 10% deviation allowed
                assert abs(position - expected) <= max_deviation, \
                    f"{event} position ({position:.2%}) too far from expected ({expected:.2%})"

                stepper.move_to_position(position)
                time.sleep(1)

            # Test additional times during the day in local timezone
            for hour in [9, 15]:  # Test morning and afternoon
                test_time = test_day.replace(hour=hour)
                position = sun_predictor.get_sun_position(test_time)

                # Verify position is within valid range
                assert 0.0 <= position <= 1.0, \
                    f"Position at {hour:02d}:00 ({position:.2%}) outside valid range [0%, 100%]"

                # Morning (before noon) should be in first half, afternoon in second half
                expected_range = (0.0, 0.5) if hour < 12 else (0.5, 1.0)
                assert expected_range[0] <= position <= expected_range[1], \
                    f"Position at {hour:02d}:00 ({position:.2%}) not in expected range {expected_range}"

                logging.info(f"Position at {hour:02d}:00: {position:.2%}")
                stepper.move_to_position(position)
                time.sleep(1)
    else:
        logging.warning("Production mode test skipped - Astral library not available")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('solar_tracking_test.log'),
            logging.StreamHandler()
        ]
    )

    test_solar_tracking()
    test_production_mode()