"""
bird_model.py

A Python implementation of the Bird & Hulstrom (1981) Clear Sky Solar Irradiance Model.
Provides utilities for calculating solar position, atmospheric corrections,
and irradiance values (direct, diffuse, and total).

References:
- Bird, R. E., & Hulstrom, R. L. (1981).
  A Simplified Clear Sky Model for Direct and Diffuse Insolation on Horizontal Surfaces.
  SERI/TR-642-761. Solar Energy Research Institute, Golden, Colorado, USA.
"""

import math
from dataclasses import dataclass


@dataclass
class SolarInputs:
    """Container for the input parameters required by the Bird Model."""
    solar_constant: float  # W/m² (mean solar constant ~1367 W/m²)
    longitude: float       # degrees (West negative)
    latitude: float        # degrees (North positive)
    elevation: float       # meters above sea level
    month: int             # 1–12
    day: int               # 1–31
    year: int              # full year (e.g., 2025)
    hour: int              # UTC hour (0–23)
    minute: int            # 0–59
    second: int            # 0–59
    station_pressure: float  # mbar (sea-level weather report pressure)
    albedo: float            # dimensionless surface reflectivity (0–1)
    ozone: float             # total column ozone (atm-cm)
    water_vapor: float       # precipitable water vapor (cm)
    aot500: float            # aerosol optical depth @ 500 nm
    aot380: float            # aerosol optical depth @ 380 nm


@dataclass
class SolarOutputs:
    """Container for the outputs from the Bird Model."""
    julian_date: float
    station_pressure: float
    earth_sun_distance: float
    zenith_angle: float
    air_mass: float
    corrected_solar_constant: float
    direct_horizontal: float
    diffuse_horizontal: float
    total_horizontal: float


class JulianDateCalculator:
    """Utility class for Julian Date calculations."""

    @staticmethod
    def calculate(month: int, day: int, year: int,
                  hour: int, minute: int, second: int) -> float:
        """Convert Gregorian calendar date and time to Julian Date."""
        m, d, y = int(month), int(day), int(year)
        hr, mn, sec = float(hour), float(minute), float(second)

        if m < 3:
            y -= 1
            m += 12

        A = math.floor(y / 100.0)
        B = 2 - A + math.floor(A / 4.0)

        JD = (math.floor(365.25 * (y + 4716)) +
              math.floor(30.6001 * (m + 1)) +
              d + B - 1524.5)

        return JD + hr / 24.0 + mn / 1440.0 + sec / 86400.0


class PressureCalculator:
    """Utility class for atmospheric pressure conversion."""

    @staticmethod
    def station_pressure(p_sea_level: float, elevation_m: float) -> float:
        """
        Convert sea-level pressure to station pressure using exponential approximation.
        """
        H = float(elevation_m) / 1000.0
        return float(p_sea_level) * math.exp(-0.119 * H - 0.0013 * H * H)


class SolarPositionCalculator:
    """Utility class for solar position calculations."""

    @staticmethod
    def calculate(julian_date: float, longitude: float, latitude: float) -> tuple[float, float]:
        """
        Calculate the solar zenith angle and Earth–Sun distance.

        Returns:
            zenith_angle (degrees), earth_sun_distance (AU)
        """
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

        # Sidereal time
        sidereal_time = (280.46061837 +
                         360.98564736629 * (julian_date - 2451545.0) +
                         0.000387933 * T * T -
                         T * T * T / 38710000.0) % 360.0

        # Obliquity
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


class BirdModel:
    """Implementation of the Bird & Hulstrom (1981) clear sky irradiance model."""

    @staticmethod
    def calculate(inputs: SolarInputs) -> SolarOutputs:
        """Run the Bird model with the given inputs."""

        jd = JulianDateCalculator.calculate(
            inputs.month, inputs.day, inputs.year,
            inputs.hour, inputs.minute, inputs.second
        )

        p = PressureCalculator.station_pressure(inputs.station_pressure, inputs.elevation)
        zenith_angle, R = SolarPositionCalculator.calculate(jd, inputs.longitude, inputs.latitude)

        dr = math.pi / 180.0
        Z_rad = zenith_angle * dr

        # Relative air mass
        AM = 1.0 / (math.cos(Z_rad) + 0.15 * pow(93.885 - zenith_angle, -1.25))
        AMp = AM * p / 1013.0

        # Rayleigh scattering
        Tr = math.exp(-0.0903 * pow(AMp, 0.84) * (1.0 + AMp - pow(AMp, 1.01)))

        # Ozone absorption
        Ozm = inputs.ozone * AM
        Toz = (1.0 - 0.1611 * Ozm * pow(1.0 + 139.48 * Ozm, -0.3035) -
               0.002715 * Ozm / (1.0 + 0.044 * Ozm + 0.0003 * Ozm * Ozm))

        # Mixed gases
        Tm = math.exp(-0.0127 * pow(AMp, 0.26))

        # Water vapor
        Wm = AM * inputs.water_vapor
        Tw = 1.0 - 2.4959 * Wm / ((1.0 + pow(79.034 * Wm, 0.6828)) + 6.385 * Wm)

        # Aerosols
        Tau = 0.2758 * inputs.aot380 + 0.35 * inputs.aot500
        Ta = math.exp((-pow(Tau, 0.873)) * (1.0 + Tau - pow(Tau, 0.7088)) * pow(AM, 0.9108))
        TAA = 1.0 - 0.1 * (1.0 - AM + pow(AM, 1.06)) * (1.0 - Ta)
        TAs = Ta / TAA
        Rs = 0.0685 + (1.0 - 0.84) * (1.0 - TAs)

        # Earth–Sun distance correction
        Rsq = 1.0 / (R * R)

        # Direct irradiance
        Id = Rsq * inputs.solar_constant * 0.9662 * Tr * Toz * Tm * Tw * Ta
        Idh = Id * math.cos(Z_rad)

        # Diffuse irradiance
        Ias = 0.79 * inputs.solar_constant * math.cos(Z_rad) * Toz * Tm * Tw * TAA
        Ias *= (0.5 * (1.0 - Tr) + 0.85 * (1.0 - TAs)) / (1.0 - AM + pow(AM, 1.02))

        # Total irradiance
        Itot = (Idh + Ias) / (1.0 - inputs.albedo * Rs)
        Idif = Itot - Idh

        return SolarOutputs(
            julian_date=jd,
            station_pressure=p,
            earth_sun_distance=R,
            zenith_angle=zenith_angle,
            air_mass=AM,
            corrected_solar_constant=Rsq * inputs.solar_constant,
            direct_horizontal=Idh,
            diffuse_horizontal=Idif,
            total_horizontal=Itot
        )


# --- Example usage ---
if __name__ == "__main__":
    inputs = SolarInputs(
        solar_constant=1367,
        longitude=-75,
        latitude=40,
        elevation=120,
        month=6,
        day=21,
        year=2007,
        hour=17,
        minute=0,
        second=0,
        station_pressure=1012,
        albedo=0.2,
        ozone=0.3,
        water_vapor=1.5,
        aot500=0.10,
        aot380=0.15
    )

    outputs = BirdModel.calculate(inputs)

    for output_name, output_value in outputs.__dict__.items():
        print(f"{output_name}: {output_value}")
