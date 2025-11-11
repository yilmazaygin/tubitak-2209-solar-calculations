from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from api.app.db.enums import RadiationDatabase, PVTechnology, MountingPlace, TrackingType, OutputFormat


class PVCalcRequest(BaseModel):
    """Request schema for grid-connected PV system calculations."""
    
    # Required parameters
    lat: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    peakpower: float = Field(..., gt=0, description="Nominal PV power in kW")
    loss: float = Field(..., ge=0, le=100, description="Sum of system losses in %")
    
    # Database and technology
    raddatabase: Optional[RadiationDatabase] = Field(None, description="Radiation database")
    pvtechchoice: Optional[PVTechnology] = Field(None, description="PV technology")
    mountingplace: Optional[MountingPlace] = Field(None, description="Mounting type")
    
    # Fixed system parameters
    fixed: Optional[int] = Field(None, description="1=fixed, 0=tracking")
    angle: Optional[float] = Field(None, ge=0, le=90, description="Inclination angle (degrees)")
    aspect: Optional[float] = Field(None, ge=-180, le=180, description="Azimuth angle (0=south)")
    optimalinclination: Optional[int] = Field(None, description="Calculate optimal inclination")
    optimalangles: Optional[int] = Field(None, description="Calculate optimal inclination & azimuth")
    
    # Tracking system parameters
    inclined_axis: Optional[int] = Field(None, description="Single inclined axis tracking")
    inclined_optimum: Optional[int] = Field(None, description="Optimal inclined axis angle")
    inclinedaxisangle: Optional[float] = Field(None, ge=0, le=90, description="Inclined axis angle")
    
    vertical_axis: Optional[int] = Field(None, description="Single vertical axis tracking")
    vertical_optimum: Optional[int] = Field(None, description="Optimal vertical axis angle")
    verticalaxisangle: Optional[float] = Field(None, ge=0, le=90, description="Vertical axis angle")
    
    twoaxis: Optional[int] = Field(None, description="Two axis tracking")
    
    # Horizon
    usehorizon: Optional[int] = Field(None, description="Use horizon data (1=yes, 0=no)")
    userhorizon: Optional[str] = Field(None, description="Comma-separated horizon heights (36 values)")
    
    # Economic parameters
    pvprice: Optional[int] = Field(None, description="Calculate PV electricity price")
    systemcost: Optional[float] = Field(None, description="Total system cost")
    interest: Optional[float] = Field(None, description="Interest rate %/year")
    lifetime: Optional[int] = Field(None, ge=1, le=50, description="System lifetime in years")
    
    # Time range
    startyear: Optional[int] = Field(None, ge=2005, le=2020, description="Start year")
    endyear: Optional[int] = Field(None, ge=2005, le=2020, description="End year")
    
    # Output format
    outputformat: Optional[OutputFormat] = Field(None, description="Output format (json, csv, basic)")
    # browser: Optional[int] = Field(None, description="Browser mode (0=no, 1=yes) - Commented out, set automatically")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lat": 38.447,
                "lon": 27.149,
                "peakpower": 1.0,
                "loss": 14.0,
                "angle": 35,
                "aspect": 0,
                "startyear": 2020,
                "endyear": 2020
            }
        }


class SHSCalcRequest(BaseModel):
    """Request schema for off-grid (stand-alone) PV system calculations."""
    
    # Required parameters
    lat: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    peakpower: float = Field(..., gt=0, description="Nominal PV power in Watts")
    batterysize: float = Field(..., gt=0, description="Battery capacity in Wh")
    cutoff: float = Field(..., ge=0, le=100, description="Battery cutoff in %")
    consumptionday: float = Field(..., gt=0, description="Daily consumption in Wh")
    
    # System configuration
    angle: Optional[float] = Field(None, ge=0, le=90, description="Inclination angle")
    aspect: Optional[float] = Field(None, ge=-180, le=180, description="Azimuth angle")
    
    # Consumption pattern
    hourconsumption: Optional[str] = Field(None, description="Comma-separated 24 hourly consumption fractions (sum must = 1)")
    
    # Database and horizon
    raddatabase: Optional[RadiationDatabase] = Field(None, description="Radiation database")
    usehorizon: Optional[int] = Field(None, description="Use horizon data (1=yes, 0=no)")
    userhorizon: Optional[str] = Field(None, description="Comma-separated horizon heights")
    
    # Time range
    startyear: Optional[int] = Field(None, ge=2005, le=2020, description="Start year")
    endyear: Optional[int] = Field(None, ge=2005, le=2020, description="End year")
    
    # Output format
    outputformat: Optional[OutputFormat] = Field(None, description="Output format")
    # browser: Optional[int] = Field(None, description="Browser mode - Commented out, set automatically")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lat": 38.447,
                "lon": 27.149,
                "peakpower": 3000,
                "batterysize": 10000,
                "cutoff": 40,
                "consumptionday": 5000,
                "angle": 35,
                "aspect": 0,
                "raddatabase": "PVGIS-SARAH",
                "startyear": 2019,
                "endyear": 2020,
                "outputformat": "json"
            }
        }


class MRCalcRequest(BaseModel):
    """Request schema for monthly radiation calculations."""
    
    # Required parameters
    lat: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    
    # Database and time
    raddatabase: Optional[RadiationDatabase] = Field(None, description="Radiation database")
    startyear: Optional[int] = Field(None, ge=2005, le=2020, description="Start year")
    endyear: Optional[int] = Field(None, ge=2005, le=2020, description="End year")
    
    # Radiation output options
    horirrad: Optional[int] = Field(None, description="Horizontal plane irradiation (1=yes)")
    optrad: Optional[int] = Field(None, description="Optimal angle plane irradiation (1=yes)")
    selectrad: Optional[int] = Field(None, description="Selected angle irradiation (1=yes)")
    angle: Optional[float] = Field(None, ge=0, le=90, description="Inclination for selectrad")
    mr_dni: Optional[int] = Field(None, description="Direct normal irradiation (1=yes)")
    d2g: Optional[int] = Field(None, description="Diffuse to global ratio (1=yes)")
    avtemp: Optional[int] = Field(None, description="Average daily temperature (1=yes)")
    
    # Horizon
    usehorizon: Optional[int] = Field(None, description="Use horizon data")
    userhorizon: Optional[str] = Field(None, description="Comma-separated horizon heights")
    
    # Output format
    outputformat: Optional[OutputFormat] = Field(None, description="Output format")
    # browser: Optional[int] = Field(None, description="Browser mode - Commented out")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lat": 38.447,
                "lon": 27.149,
                "raddatabase": "PVGIS-SARAH",
                "horirrad": 1,
                "optrad": 1,
                "avtemp": 1,
                "startyear": 2019,
                "endyear": 2020,
                "outputformat": "json"
            }
        }


class DRCalcRequest(BaseModel):
    """Request schema for daily radiation calculations."""
    
    # Required parameters
    lat: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    month: int = Field(..., ge=0, le=12, description="Month (0=all months, 1-12=specific month)")
    
    # Database and configuration
    raddatabase: Optional[RadiationDatabase] = Field(None, description="Radiation database")
    angle: Optional[float] = Field(None, ge=0, le=90, description="Inclination angle")
    aspect: Optional[float] = Field(None, ge=-180, le=180, description="Azimuth angle")
    
    # Output options
    global_: Optional[int] = Field(None, alias="global", description="Global, direct, diffuse (1=yes)")
    glob_2axis: Optional[int] = Field(None, description="Two-axis tracking irradiances (1=yes)")
    clearsky: Optional[int] = Field(None, description="Clear-sky irradiance (1=yes)")
    clearsky_2axis: Optional[int] = Field(None, description="Clear-sky 2-axis tracking (1=yes)")
    showtemperatures: Optional[int] = Field(None, description="Daily temperature profile (1=yes)")
    localtime: Optional[int] = Field(None, description="Use local time instead of UTC (1=yes)")
    
    # Time range (optional for specific years)
    startyear: Optional[int] = Field(None, ge=2005, le=2020, description="Start year")
    endyear: Optional[int] = Field(None, ge=2005, le=2020, description="End year")
    
    # Horizon
    usehorizon: Optional[int] = Field(None, description="Use horizon data")
    userhorizon: Optional[str] = Field(None, description="Comma-separated horizon heights")
    
    # Output format
    outputformat: Optional[OutputFormat] = Field(None, description="Output format")
    # browser: Optional[int] = Field(None, description="Browser mode - Commented out")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "lat": 38.447,
                "lon": 27.149,
                "month": 4,
                "raddatabase": "PVGIS-SARAH",
                "angle": 35,
                "aspect": 0,
                "global_": 1,
                "showtemperatures": 1,
                "outputformat": "json"
            }
        }


class SeriesCalcRequest(BaseModel):
    """Request schema for hourly radiation time series."""
    
    # Required parameters
    lat: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    
    # Database and time range
    raddatabase: Optional[RadiationDatabase] = Field(None, description="Radiation database")
    startyear: Optional[int] = Field(None, ge=2005, le=2020, description="Start year")
    endyear: Optional[int] = Field(None, ge=2005, le=2020, description="End year")
    
    # PV calculation options
    pvcalculation: Optional[int] = Field(None, description="Include PV production (1=yes, 0=no)")
    peakpower: Optional[float] = Field(None, description="Required if pvcalculation=1, in kW")
    pvtechchoice: Optional[PVTechnology] = Field(None, description="PV technology")
    mountingplace: Optional[MountingPlace] = Field(None, description="Mounting type")
    loss: Optional[float] = Field(None, description="System losses % (required if pvcalculation=1)")
    
    # Mounting configuration
    trackingtype: Optional[TrackingType] = Field(None, description="Tracking type (0=fixed, 1=horiz N-S, 2=two-axis, etc.)")
    angle: Optional[float] = Field(None, ge=0, le=90, description="Inclination angle")
    aspect: Optional[float] = Field(None, ge=-180, le=180, description="Azimuth angle")
    optimalinclination: Optional[int] = Field(None, description="Calculate optimal inclination (1=yes)")
    optimalangles: Optional[int] = Field(None, description="Calculate optimal angles (1=yes)")
    
    # Output options
    components: Optional[int] = Field(None, description="Output beam, diffuse, reflected components (1=yes)")
    
    # Horizon
    usehorizon: Optional[int] = Field(None, description="Use horizon data")
    userhorizon: Optional[str] = Field(None, description="Comma-separated horizon heights")
    
    # Output format
    outputformat: Optional[OutputFormat] = Field(None, description="Output format")
    # browser: Optional[int] = Field(None, description="Browser mode - Commented out")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lat": 38.447,
                "lon": 27.149,
                "raddatabase": "PVGIS-SARAH",
                "startyear": 2020,
                "endyear": 2020,
                "pvcalculation": 1,
                "peakpower": 1.0,
                "pvtechchoice": "crystSi",
                "mountingplace": "free",
                "loss": 14,
                "angle": 35,
                "aspect": 0,
                "outputformat": "json"
            }
        }


class TMYRequest(BaseModel):
    """Request schema for Typical Meteorological Year data. WARNING: Requires minimum 10 years! Very slow (30-90 seconds)!"""
    
    # Required parameters
    lat: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    
    # Database and time (minimum 10 years required)
    raddatabase: Optional[RadiationDatabase] = Field(None, description="Radiation database")
    startyear: Optional[int] = Field(None, ge=2005, le=2020, description="Start year")
    endyear: Optional[int] = Field(None, ge=2005, le=2020, description="End year (must be >= startyear + 9)")
    
    # Horizon
    usehorizon: Optional[int] = Field(None, description="Use horizon data")
    userhorizon: Optional[str] = Field(None, description="Comma-separated horizon heights")
    
    # Output format
    outputformat: Optional[OutputFormat] = Field(None, description="Output format (json, csv, basic, epw)")
    # browser: Optional[int] = Field(None, description="Browser mode - Commented out")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lat": 38.447,
                "lon": 27.149,
                "raddatabase": "PVGIS-SARAH2",
                "startyear": 2010,
                "endyear": 2020,
                "outputformat": "json"
            }
        }


class HorizonRequest(BaseModel):
    """Request schema for horizon profile data."""
    
    # Required parameters
    lat: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    
    # User-defined horizon (optional)
    userhorizon: Optional[str] = Field(None, description="User-defined horizon heights (36 comma-separated values)")
    
    # Output format
    outputformat: Optional[OutputFormat] = Field(None, description="Output format")
    # browser: Optional[int] = Field(None, description="Browser mode - Commented out")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lat": 38.447,
                "lon": 27.149,
                "outputformat": "json"
            }
        }


class PVGISBasicRequest(BaseModel):
    """Request schema for basic PVGIS data."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    start_year: int = Field(2005, ge=2005, le=2020, description="Start year for data")
    end_year: int = Field(2020, ge=2005, le=2020, description="End year for data")
    slope: int = Field(90, ge=0, le=90, description="Slope angle in degrees")
    azimuth: int = Field(0, ge=-180, le=180, description="Azimuth angle in degrees")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 38.447,
                "longitude": 27.149,
                "start_year": 2005,
                "end_year": 2020,
                "slope": 90,
                "azimuth": 0
            }
        }


class PVGISDayAverageRequest(BaseModel):
    """Request schema for specific day average across years."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    day: int = Field(..., ge=1, le=31, description="Day (1-31)")
    start_year: int = Field(2005, ge=2005, le=2020, description="Start year for analysis")
    end_year: int = Field(2020, ge=2005, le=2020, description="End year for analysis")
    slope: int = Field(90, ge=0, le=90, description="Slope angle in degrees")
    azimuth: int = Field(0, ge=-180, le=180, description="Azimuth angle in degrees")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 38.447,
                "longitude": 27.149,
                "month": 4,
                "day": 15,
                "start_year": 2005,
                "end_year": 2020,
                "slope": 90,
                "azimuth": 0
            }
        }


class HourlyData(BaseModel):
    """Hourly solar data."""
    
    hour: int = Field(..., ge=0, le=23, description="UTC hour")
    G_i: float = Field(..., description="Global irradiance on inclined surface (W/m²)")
    H_sun: float = Field(..., description="Sun height (degrees)")
    T2m: float = Field(..., description="Temperature at 2m (°C)")
    WS10m: float = Field(..., description="Wind speed at 10m (m/s)")
    Int: float = Field(..., description="Intensity/clearness")
    sample_count: int = Field(..., description="Number of samples averaged")


class PVGISDayAverageResponse(BaseModel):
    """Response schema for specific day average."""
    
    latitude: float
    longitude: float
    month: int
    day: int
    years_analyzed: List[int]
    hourly_averages: List[HourlyData]
    peak_hour: int = Field(..., description="Hour with maximum G(i)")
    peak_irradiance: float = Field(..., description="Maximum G(i) value (W/m²)")
    daily_total_energy: float = Field(..., description="Total daily energy (Wh/m²)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 38.447,
                "longitude": 27.149,
                "month": 4,
                "day": 15,
                "years_analyzed": [2005, 2006, 2007],
                "hourly_averages": [
                    {
                        "hour": 0,
                        "G_i": 0.0,
                        "H_sun": 0.0,
                        "T2m": 15.2,
                        "WS10m": 2.5,
                        "Int": 0.0,
                        "sample_count": 3
                    }
                ],
                "peak_hour": 12,
                "peak_irradiance": 850.5,
                "daily_total_energy": 5420.3
            }
        }


class PVGISMetadata(BaseModel):
    """Metadata from PVGIS response."""
    
    latitude: float
    longitude: float
    elevation: float
    radiation_database: str
    slope: int
    azimuth: int
