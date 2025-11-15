from pydantic import BaseModel, Field
from typing import Optional


class JulianDayRequest(BaseModel):
    """Request schema for Julian Date calculation."""
    
    year: int = Field(..., ge=1582, le=9999, description="Year (Gregorian calendar, >= 1582)")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    day: int = Field(..., ge=1, le=31, description="Day of month (1-31)")
    hour: int = Field(0, ge=0, le=23, description="Hour (0-23, UTC)")
    minute: int = Field(0, ge=0, le=59, description="Minute (0-59)")
    second: int = Field(0, ge=0, le=59, description="Second (0-59)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "year": 2025,
                "month": 4,
                "day": 15,
                "hour": 12,
                "minute": 30,
                "second": 0
            }
        }


class JulianDayResponse(BaseModel):
    """Response schema for Julian Date calculation."""
    
    julian_date: float = Field(..., description="Julian Date (days since January 1, 4713 BC at noon UTC)")
    input_date: str = Field(..., description="Input date in ISO 8601 format")
    
    class Config:
        json_schema_extra = {
            "example": {
                "julian_date": 2460047.0208333335,
                "input_date": "2025-04-15T12:30:00"
            }
        }


class PressureRequest(BaseModel):
    """Request schema for station pressure calculation."""
    
    sea_level_pressure: float = Field(..., gt=0, le=1100, description="Sea level pressure (mbar/hPa)")
    elevation: float = Field(..., ge=-500, le=9000, description="Elevation above sea level (meters)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sea_level_pressure": 1013.25,
                "elevation": 500
            }
        }


class PressureResponse(BaseModel):
    """Response schema for station pressure calculation."""
    
    station_pressure: float = Field(..., description="Station pressure at given elevation (mbar/hPa)")
    sea_level_pressure: float = Field(..., description="Input sea level pressure (mbar/hPa)")
    elevation: float = Field(..., description="Elevation above sea level (meters)")
    pressure_drop: float = Field(..., description="Pressure decrease from sea level (mbar/hPa)")
    pressure_ratio: float = Field(..., description="Station pressure / Sea level pressure")
    
    class Config:
        json_schema_extra = {
            "example": {
                "station_pressure": 954.32,
                "sea_level_pressure": 1013.25,
                "elevation": 500,
                "pressure_drop": 58.93,
                "pressure_ratio": 0.9418
            }
        }


class SolarPositionRequest(BaseModel):
    """Request schema for solar position calculation."""
    
    # Date/Time input
    year: int = Field(..., ge=1582, le=9999, description="Year (Gregorian calendar)")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    day: int = Field(..., ge=1, le=31, description="Day of month (1-31)")
    hour: int = Field(12, ge=0, le=23, description="Hour (0-23, UTC)")
    minute: int = Field(0, ge=0, le=59, description="Minute (0-59)")
    second: int = Field(0, ge=0, le=59, description="Second (0-59)")
    
    # Location
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees (negative = South)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees (negative = West)")
    
    # Optional: If Julian Date is already known, can be provided directly
    julian_date: Optional[float] = Field(None, description="Julian Date (if provided, date fields are ignored)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "year": 2025,
                "month": 6,
                "day": 21,
                "hour": 12,
                "minute": 0,
                "second": 0,
                "latitude": 38.447,
                "longitude": 27.149
            }
        }


class SolarPositionResponse(BaseModel):
    """Response schema for solar position calculation."""
    
    # Position data
    zenith_angle: float = Field(..., description="Solar zenith angle (degrees, 0=directly overhead)")
    solar_elevation: float = Field(..., description="Solar elevation angle (degrees above horizon)")
    earth_sun_distance: float = Field(..., description="Earth-Sun distance (Astronomical Units)")
    
    # Input reference
    julian_date: float = Field(..., description="Julian Date used for calculation")
    datetime_utc: str = Field(..., description="Date and time in ISO 8601 format (UTC)")
    latitude: float = Field(..., description="Latitude (degrees)")
    longitude: float = Field(..., description="Longitude (degrees)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "zenith_angle": 8.45,
                "solar_elevation": 81.55,
                "earth_sun_distance": 1.01593,
                "julian_date": 2460116.0,
                "datetime_utc": "2025-06-21T12:00:00",
                "latitude": 38.447,
                "longitude": 27.149
            }
        }


class SolarPositionBatchRequest(BaseModel):
    """Request schema for batch solar position calculations (multiple times at one location)."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    
    # Single day, multiple hours
    year: int = Field(..., ge=1582, le=9999, description="Year")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    day: int = Field(..., ge=1, le=31, description="Day of month (1-31)")
    
    hour_start: int = Field(0, ge=0, le=23, description="Starting hour (UTC)")
    hour_end: int = Field(23, ge=0, le=23, description="Ending hour (UTC)")
    hour_step: int = Field(1, ge=1, le=24, description="Hour step (e.g., 1 for every hour)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 38.447,
                "longitude": 27.149,
                "year": 2025,
                "month": 6,
                "day": 21,
                "hour_start": 0,
                "hour_end": 23,
                "hour_step": 1
            }
        }


class SolarPositionBatchResponse(BaseModel):
    """Response schema for batch solar position calculations."""
    
    latitude: float = Field(..., description="Latitude (degrees)")
    longitude: float = Field(..., description="Longitude (degrees)")
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    
    hourly_positions: list[dict] = Field(..., description="Solar position for each hour")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 38.447,
                "longitude": 27.149,
                "date": "2025-06-21",
                "hourly_positions": [
                    {
                        "hour": 0,
                        "datetime_utc": "2025-06-21T00:00:00",
                        "julian_date": 2460115.5,
                        "zenith_angle": 108.23,
                        "solar_elevation": -18.23,
                        "earth_sun_distance": 1.01593
                    },
                    {
                        "hour": 12,
                        "datetime_utc": "2025-06-21T12:00:00",
                        "julian_date": 2460116.0,
                        "zenith_angle": 8.45,
                        "solar_elevation": 81.55,
                        "earth_sun_distance": 1.01593
                    }
                ]
            }
        }
