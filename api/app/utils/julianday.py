import math


class JulianDateCalculator:
    """Utility class for Julian Date calculations."""

    @staticmethod
    def calculate(month: int, day: int, year: int,
                  hour: int, minute: int, second: int) -> float:
        """
        Convert Gregorian calendar date and time to Julian Date.
        Input validation is handled by schemas/dataclasses before this method is called.
        """
        try:
            m, d, y = int(month), int(day), int(year)
            hr, mn, sec = float(hour), float(minute), float(second)

            if m < 3:
                y -= 1
                m += 12

            # A is the century number, B is the leap year correction
            A = math.floor(y / 100.0)
            B = 2 - A + math.floor(A / 4.0)

            # Calculate Julian Date at midnight
            JD = (math.floor(365.25 * (y + 4716)) +
                  math.floor(30.6001 * (m + 1)) +
                  d + B - 1524.5)

            # Add time fraction to get full Julian Date
            time_fraction = hr / 24.0 + mn / 1440.0 + sec / 86400.0
            
            return JD + time_fraction

        except OverflowError as e:
            raise OverflowError(
                f"Numeric overflow in Julian Date calculation for year {year}. "
                f"Error: {str(e)}"
            ) from e
        
        except (ValueError, ZeroDivisionError) as e:
            raise RuntimeError(f"Mathematical error during Julian Date calculation: {str(e)}") from e
        
        except Exception as e:
            raise RuntimeError(f"Unexpected error in Julian Date calculation: {str(e)}") from e