from datetime import datetime, timezone, timedelta
import logging
from zoneinfo import ZoneInfo

class SunPredictor:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude
        try:
            from astral import LocationInfo
            from astral.sun import sun
            self.timezone = ZoneInfo("Europe/London")

            if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
                raise ValueError(f"Invalid coordinates: lat={latitude}, lon={longitude}")

            self.location = LocationInfo(
                'SensorLocation',  # Name is required but not used
                'Region',         # Region is required but not used
                timezone="Europe/London",  # Using GMT timezone
                latitude=latitude,
                longitude=longitude
            )
            self.sun_calc = sun
            self.use_mock = False
            logging.info(f"Initialized SunPredictor in production mode using Astral (lat={latitude}, lon={longitude})")
        except ImportError as e:
            logging.error(f"Failed to import Astral library: {str(e)}")
            self.use_mock = True
        except ValueError as e:
            logging.error(f"Configuration error: {str(e)}")
            self.use_mock = True
        except Exception as e:
            logging.error(f"Unexpected error initializing SunPredictor: {str(e)}")
            self.use_mock = True

    def get_sun_position(self, current_time=None):
        """Calculate current sun position relative to the panel's range."""
        try:
            current_time = current_time or datetime.now(timezone.utc)
            # Convert input time to sensor's local timezone
            local_time = current_time.astimezone(self.timezone)
            logging.info(f"Calculating sun position for time: {local_time.strftime('%H:%M:%S %Z')}")

            if self.use_mock:
                # Mock implementation using fixed sunrise/sunset times
                mock_base = local_time.replace(hour=0, minute=0, second=0, microsecond=0)
                mock_sunrise = mock_base.replace(hour=6)  # 6 AM sunrise
                mock_sunset = mock_base.replace(hour=18)  # 6 PM sunset

                logging.info(f"Mock sun times - Sunrise: {mock_sunrise.strftime('%H:%M:%S')}, Sunset: {mock_sunset.strftime('%H:%M:%S')}")

                # Before sunrise or after sunset - return east position
                if local_time < mock_sunrise or local_time >= mock_sunset:
                    logging.info("Outside daylight hours: Panel positioned for morning (east)")
                    return 0.0  # East position

                # Calculate position as percentage of daylight hours
                day_duration = (mock_sunset - mock_sunrise).total_seconds()
                time_since_sunrise = (local_time - mock_sunrise).total_seconds()
                position = min(1.0, max(0.0, time_since_sunrise / day_duration))
                logging.info(f"Mock sun position calculated: {position:.2%} of east-west range ({time_since_sunrise/3600:.1f} hours since sunrise)")
                return position

            # Get sun information for today using astral
            s = self.sun_calc(self.location.observer, date=local_time.date())

            # Convert all times to GMT for consistent comparison
            sunrise_time = s['sunrise'].astimezone(self.timezone)
            solar_noon = s['noon'].astimezone(self.timezone)
            sunset_time = s['sunset'].astimezone(self.timezone)
            
            # Ensure local_time is in the same timezone
            local_time = local_time.astimezone(self.timezone)

            # Handle case where sunset is on the next day
            if sunset_time < sunrise_time:
                sunset_time += timedelta(days=1)

            day_length = (sunset_time - sunrise_time).total_seconds() / 3600

            logging.info(f"Astronomical calculations for {local_time.strftime('%Y-%m-%d')}:")
            logging.info(f"Sunrise: {sunrise_time.strftime('%H:%M:%S %Z')}")
            logging.info(f"Solar noon: {solar_noon.strftime('%H:%M:%S %Z')}")
            logging.info(f"Sunset: {sunset_time.strftime('%H:%M:%S %Z')}")
            logging.info(f"Day length: {day_length:.1f} hours")

            # Check if we're in the current day's daylight period
            if local_time < sunrise_time or local_time > sunset_time:
                logging.info("Outside daylight hours: Panel positioned for morning (east)")
                return 0.0

            # Calculate position as percentage of daylight hours, ensuring all times are in the same timezone
            day_duration = (sunset_time - sunrise_time).total_seconds()
            time_since_sunrise = (local_time - sunrise_time).total_seconds()
            position = min(1.0, max(0.0, time_since_sunrise / day_duration))

            logging.info(f"Sun position calculated: {position:.2%} of east-west range ({time_since_sunrise/3600:.1f} hours since sunrise)")
            return position

        except Exception as e:
            logging.error(f"Error calculating sun position: {str(e)}")
            return 0.5  # Default to middle position on error