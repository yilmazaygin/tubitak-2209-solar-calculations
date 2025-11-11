from dataclasses import dataclass
from ..core.config_loader import settings

"""
# Preset decimal precision based on configuration
# Will be used in calculations involving Decimal types next update
from decimal import Decimal, getcontext
getcontext().prec = settings.DECIMAL_PRECISION
"""

@dataclass
class SolarInputsDataclass:
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
class SolarOutputsDataclass:
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