from pydantic import BaseModel, Field

class SolarInputsSchema(BaseModel):
    """Schema for the input parameters required by the Bird Model."""

    solar_constant: float = Field(..., description="W/m² (mean solar constant ~1367 W/m²)")
    longitude: float = Field(..., description="Degrees (West negative)")
    latitude: float = Field(..., description="Degrees (North positive)")
    elevation: float = Field(..., description="Meters above sea level")
    month: int = Field(..., ge=1, le=12, description="Month (1–12)")
    day: int = Field(..., ge=1, le=31, description="Day (1–31)")
    year: int = Field(..., ge=1900, le=2100, description="Full year (e.g., 2025)")
    hour: int = Field(..., ge=0, le=23, description="UTC hour (0–23)")
    minute: int = Field(..., ge=0, le=59, description="Minute (0–59)")
    second: int = Field(..., ge=0, le=59, description="Second (0–59)")
    station_pressure: float = Field(..., description="mbar (sea-level weather report pressure)")
    albedo: float = Field(..., ge=0.0, le=1.0, description="Dimensionless surface reflectivity (0–1)")
    ozone: float = Field(..., description="Total column ozone (atm-cm)")
    water_vapor: float = Field(..., description="Precipitable water vapor (cm)")
    aot500: float = Field(..., description="Aerosol optical depth @ 500 nm")
    aot380: float = Field(..., description="Aerosol optical depth @ 380 nm")

    class Config:
        json_schema_extra = {
            "example": {
                "solar_constant": 1367,
                "longitude": -75,
                "latitude": 40,
                "elevation": 120,
                "month": 6,
                "day": 21,
                "year": 2007,
                "hour": 17,
                "minute": 0,
                "second": 0,
                "station_pressure": 1012,
                "albedo": 0.2,
                "ozone": 0.3,
                "water_vapor": 1.5,
                "aot500": 0.10,
                "aot380": 0.15
            }
        }

class SolarOutputsSchema(BaseModel):
    """Schema for the outputs from the Bird Model."""

    julian_date: float = Field(..., description="Julian date")
    station_pressure: float = Field(..., description="Station pressure in mbar")
    earth_sun_distance: float = Field(..., description="Earth-Sun distance in AU")
    zenith_angle: float = Field(..., description="Solar zenith angle in degrees")
    air_mass: float = Field(..., description="Air mass")
    corrected_solar_constant: float = Field(..., description="Corrected solar constant in W/m²")
    direct_horizontal: float = Field(..., description="Direct horizontal irradiance in W/m²")
    diffuse_horizontal: float = Field(..., description="Diffuse horizontal irradiance in W/m²")
    total_horizontal: float = Field(..., description="Total horizontal irradiance in W/m²")
