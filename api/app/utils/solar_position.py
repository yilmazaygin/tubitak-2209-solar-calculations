import math


class SolarPositionCalculator:
    """Utility class for solar position calculations."""

    @staticmethod
    def calculate(julian_date: float, longitude: float, latitude: float) -> tuple[float, float]:
        """
        Calculate the solar zenith angle and Earth–Sun distance.
        Input validation is handled by schemas/dataclasses before this method is called.

        Returns:
            zenith_angle (degrees), earth_sun_distance (AU)
        """
        try:
            dr = math.pi / 180.0
            T = (julian_date - 2451545.0) / 36525.0

            L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T * T
            M = 357.52910 + 35999.05030 * T - 0.0001559 * T * T - 0.00000048 * T * T * T
            M_rad = M * dr

            e = 0.016708617 - 0.000042037 * T - 0.0000001236 * T * T
            C = ((1.914600 - 0.004817 * T - 0.000014 * T * T) * math.sin(M_rad) +
                 (0.019993 - 0.000101 * T) * math.sin(2.0 * M_rad) +
                 0.000290 * math.sin(3.0 * M_rad))

            L_true = (L0 + C) % 360.0
            f = M_rad + C * dr
            R = 1.000001018 * (1.0 - e * e) / (1.0 + e * math.cos(f))

            sidereal_time = (280.46061837 +
                             360.98564736629 * (julian_date - 2451545.0) +
                             0.000387933 * T * T -
                             T * T * T / 38710000.0) % 360.0

            obliquity = (23.0 + 26.0 / 60.0 +
                         21.448 / 3600.0 -
                         46.8150 / 3600.0 * T -
                         0.00059 / 3600.0 * T * T +
                         0.001813 / 3600.0 * T * T * T)

            right_ascension = math.atan2(math.sin(L_true * dr) * math.cos(obliquity * dr),
                                         math.cos(L_true * dr))
            declination = math.asin(math.sin(obliquity * dr) * math.sin(L_true * dr))

            hour_angle = sidereal_time + longitude - (right_ascension / dr)
            elevation = math.asin(math.sin(latitude * dr) * math.sin(declination) +
                                  math.cos(latitude * dr) * math.cos(declination) *
                                  math.cos(hour_angle * dr)) / dr

            zenith_angle = 90.0 - elevation
            return zenith_angle, R

        except OverflowError as e:
            raise OverflowError(
                f"Numeric overflow in solar position calculation. Error: {str(e)}"
            ) from e
        
        except (ValueError, ZeroDivisionError) as e:
            raise RuntimeError(f"Mathematical error during solar position calculation: {str(e)}") from e
        
        except Exception as e:
            raise RuntimeError(f"Unexpected error in solar position calculation: {str(e)}") from e