from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from api.app.db.enums import RadiationDatabase, PVTechnology, MountingPlace, TrackingType, OutputFormat


class PVCalcRequest(BaseModel):
    """Request schema for grid-connected PV system calculations."""
    
    lat: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    lon: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    peakpower: float = Field(..., gt=0, description="Nominal PV power in kW")
    loss: float = Field(..., ge=0, le=100, description="Sum of system losses in %")
    
    raddatabase: Optional[RadiationDatabase] = Field(None, description="Radiation database")
    pvtechchoice: Optional[PVTechnology] = Field(PVTechnology.CRYSTSI, description="PV technology")
    mountingplace: Optional[MountingPlace] = Field(MountingPlace.FREE, description="Mounting type")
    
    # Fixed system parameters
    fixed: Optional[int] = Field(1, description="1=fixed, 0=tracking")
    angle: Optional[float] = Field(0, ge=0, le=90, description="Inclination angle (degrees)")
    aspect: Optional[float] = Field(0, ge=-180, le=180, description="Azimuth angle (0=south)")
    optimalinclination: Optional[int] = Field(0, description="Calculate optimal inclination")
    optimalangles: Optional[int] = Field(0, description="Calculate optimal inclination & azimuth")
    
    # Tracking system parameters
    inclined_axis: Optional[int] = Field(0, description="Single inclined axis tracking")
    inclined_optimum: Optional[int] = Field(0, description="Optimal inclined axis angle")
    inclinedaxisangle: Optional[float] = Field(0, ge=0, le=90)
    
    vertical_axis: Optional[int] = Field(0, description="Single vertical axis tracking")
    vertical_optimum: Optional[int] = Field(0, description="Optimal vertical axis angle")
    verticalaxisangle: Optional[float] = Field(0, ge=0, le=90)
    
    twoaxis: Optional[int] = Field(0, description="Two axis tracking")
    
    # Horizon
    usehorizon: Optional[int] = Field(1, description="Use horizon data")
    userhorizon: Optional[str] = Field(None, description="Comma-separated horizon heights")
    
    # Economic parameters
    pvprice: Optional[int] = Field(0, description="Calculate PV electricity price")
    systemcost: Optional[float] = Field(None, description="Total system cost")
    interest: Optional[float] = Field(None, description="Interest rate %/year")
    lifetime: Optional[int] = Field(25, ge=1, le=50, description="System lifetime in years")
    
    startyear: Optional[int] = Field(None, ge=2005, le=2020)
    endyear: Optional[int] = Field(None, ge=2005, le=2020)
    
    outputformat: Optional[OutputFormat] = Field(OutputFormat.JSON)
    browser: Optional[int] = Field(0)


class SHSCalcRequest(BaseModel):
    """Request schema for off-grid (stand-alone) PV system calculations."""
    
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    peakpower: float = Field(..., gt=0, description="Nominal PV power in Watts")
    batterysize: float = Field(..., gt=0, description="Battery capacity in Wh")
    cutoff: float = Field(..., ge=0, le=100, description="Battery cutoff in %")
    consumptionday: float = Field(..., gt=0, description="Daily consumption in Wh")
    
    angle: Optional[float] = Field(0, ge=0, le=90)
    aspect: Optional[float] = Field(0, ge=-180, le=180)
    
    hourconsumption: Optional[str] = Field(None, description="Comma-separated 24 hourly fractions")
    
    raddatabase: Optional[RadiationDatabase] = Field(None)
    usehorizon: Optional[int] = Field(1)
    userhorizon: Optional[str] = Field(None)
    
    outputformat: Optional[OutputFormat] = Field(OutputFormat.JSON)
    browser: Optional[int] = Field(0)


class MRCalcRequest(BaseModel):
    """Request schema for monthly radiation calculations."""
    
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    
    raddatabase: Optional[RadiationDatabase] = Field(None)
    startyear: Optional[int] = Field(None, ge=2005, le=2020)
    endyear: Optional[int] = Field(None, ge=2005, le=2020)
    
    horirrad: Optional[int] = Field(0, description="Horizontal plane irradiation")
    optrad: Optional[int] = Field(0, description="Optimal angle plane irradiation")
    selectrad: Optional[int] = Field(0, description="Selected angle irradiation")
    angle: Optional[float] = Field(0, ge=0, le=90, description="Inclination for selectrad")
    mr_dni: Optional[int] = Field(0, description="Direct normal irradiation")
    d2g: Optional[int] = Field(0, description="Diffuse to global ratio")
    avtemp: Optional[int] = Field(0, description="Average daily temperature")
    
    usehorizon: Optional[int] = Field(1)
    userhorizon: Optional[str] = Field(None)
    
    outputformat: Optional[OutputFormat] = Field(OutputFormat.JSON)
    browser: Optional[int] = Field(0)


class DRCalcRequest(BaseModel):
    """Request schema for daily radiation calculations."""
    
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    month: int = Field(..., ge=0, le=12, description="Month (0=all months)")
    
    raddatabase: Optional[RadiationDatabase] = Field(None)
    angle: Optional[float] = Field(0, ge=0, le=90)
    aspect: Optional[float] = Field(0, ge=-180, le=180)
    
    global_: Optional[int] = Field(0, alias="global", description="Global, direct, diffuse")
    glob_2axis: Optional[int] = Field(0, description="Two-axis tracking irradiances")
    clearsky: Optional[int] = Field(0, description="Clear-sky irradiance")
    clearsky_2axis: Optional[int] = Field(0, description="Clear-sky 2-axis tracking")
    showtemperatures: Optional[int] = Field(0, description="Daily temperature profile")
    localtime: Optional[int] = Field(0, description="Use local time instead of UTC")
    
    usehorizon: Optional[int] = Field(1)
    userhorizon: Optional[str] = Field(None)
    
    outputformat: Optional[OutputFormat] = Field(OutputFormat.JSON)
    browser: Optional[int] = Field(0)
    
    class Config:
        populate_by_name = True


class SeriesCalcRequest(BaseModel):
    """Request schema for hourly radiation time series."""
    
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    
    raddatabase: Optional[RadiationDatabase] = Field(None)
    startyear: Optional[int] = Field(None, ge=2005, le=2020)
    endyear: Optional[int] = Field(None, ge=2005, le=2020)
    
    # PV calculation
    pvcalculation: Optional[int] = Field(0, description="Include PV production estimation")
    peakpower: Optional[float] = Field(None, description="Required if pvcalculation=1, in kW")
    pvtechchoice: Optional[PVTechnology] = Field(PVTechnology.CRYSTSI)
    mountingplace: Optional[MountingPlace] = Field(MountingPlace.FREE)
    loss: Optional[float] = Field(None, description="Required if pvcalculation=1")
    
    # Mounting configuration
    trackingtype: Optional[TrackingType] = Field(TrackingType.FIXED)
    angle: Optional[float] = Field(0, ge=0, le=90)
    aspect: Optional[float] = Field(0, ge=-180, le=180)
    optimalinclination: Optional[int] = Field(0)
    optimalangles: Optional[int] = Field(0)
    
    components: Optional[int] = Field(0, description="Output beam, diffuse, reflected components")
    
    usehorizon: Optional[int] = Field(1)
    userhorizon: Optional[str] = Field(None)
    
    outputformat: Optional[OutputFormat] = Field(OutputFormat.JSON)
    browser: Optional[int] = Field(0)


class TMYRequest(BaseModel):
    """Request schema for Typical Meteorological Year data."""
    
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    
    raddatabase: Optional[RadiationDatabase] = Field(None)
    startyear: Optional[int] = Field(None, ge=2005, le=2020)
    endyear: Optional[int] = Field(None, ge=2005, le=2020, description="Period should be >= 10 years")
    
    usehorizon: Optional[int] = Field(1)
    userhorizon: Optional[str] = Field(None)
    
    outputformat: Optional[OutputFormat] = Field(OutputFormat.JSON, description="json, csv, basic, or epw")
    browser: Optional[int] = Field(0)


class HorizonRequest(BaseModel):
    """Request schema for horizon profile data."""
    
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    
    userhorizon: Optional[str] = Field(None, description="User-defined horizon heights")
    
    outputformat: Optional[OutputFormat] = Field(OutputFormat.JSON)
    browser: Optional[int] = Field(0)


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
