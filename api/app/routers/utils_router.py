from fastapi import APIRouter, HTTPException
from fastapi import status as http_status
from pydantic import ValidationError
from ..core.logger import app_logger as logger
from ..utils.julianday import JulianDateCalculator
from ..utils.pressure import PressureCalculator
from ..utils.solar_position import SolarPositionCalculator
from ..schemas.utils_schemas import (
    JulianDayRequest,
    JulianDayResponse,
    PressureRequest,
    PressureResponse,
    SolarPositionRequest,
    SolarPositionResponse,
    SolarPositionBatchRequest,
    SolarPositionBatchResponse
)

router = APIRouter(prefix="/utils", tags=["Utilities"])


@router.post("/julian-day", response_model=JulianDayResponse)
def calculate_julian_day(request: JulianDayRequest) -> JulianDayResponse:
    """
    Calculate Julian Date from Gregorian calendar date and time.
    
    The Julian Date (JD) is a continuous count of days since the beginning of the 
    Julian Period (January 1, 4713 BC at noon UTC). It's widely used in astronomy 
    and solar calculations.
    
    **Use cases:**
    - Solar position calculations
    - Astronomical computations
    - Time series analysis across long periods
    - Converting between calendar systems
    
    **Note:** Valid for dates after October 15, 1582 (Gregorian calendar adoption).
    """
    logger.info(
        f"Calculating Julian Date for {request.year}-{request.month:02d}-{request.day:02d} "
        f"{request.hour:02d}:{request.minute:02d}:{request.second:02d}"
    )
    
    try:
        julian_date = JulianDateCalculator.calculate(
            month=request.month,
            day=request.day,
            year=request.year,
            hour=request.hour,
            minute=request.minute,
            second=request.second
        )
        
        input_date_str = (
            f"{request.year:04d}-{request.month:02d}-{request.day:02d}T"
            f"{request.hour:02d}:{request.minute:02d}:{request.second:02d}"
        )
        
        logger.info(f"Julian Date calculated: {julian_date}")
        
        return JulianDayResponse(
            julian_date=julian_date,
            input_date=input_date_str
        )
        
    except ValidationError as e:
        logger.exception("Validation error in Julian Date calculation: %s", e)
        raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    except ValueError as e:
        logger.exception("Value error in Julian Date calculation: %s", e)
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except OverflowError as e:
        logger.exception("Overflow error in Julian Date calculation: %s", e)
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        logger.exception("Unexpected error in Julian Date calculation: %s", e)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during Julian Date calculation"
        )


@router.post("/pressure", response_model=PressureResponse)
def calculate_station_pressure(request: PressureRequest) -> PressureResponse:
    """
    Convert sea-level pressure to station pressure at a given elevation.
    
    Uses an exponential approximation formula that accounts for atmospheric 
    pressure decrease with altitude. Essential for accurate solar radiation 
    calculations at different elevations.
    
    **Formula:** P_station = P_sea * exp(-0.119*H - 0.0013*H²)
    where H is elevation in kilometers.
    
    **Use cases:**
    - Solar irradiance calculations (BIRD model, etc.)
    - Atmospheric corrections for PV system modeling
    - Weather station data normalization
    - High-altitude solar installations
    
    **Typical values:**
    - Sea level: 1013.25 mbar (standard atmosphere)
    - 500m: ~954 mbar
    - 1000m: ~899 mbar
    - 2000m: ~795 mbar
    """
    logger.info(
        f"Calculating station pressure: sea_level={request.sea_level_pressure}mbar, "
        f"elevation={request.elevation}m"
    )
    
    try:
        station_pressure = PressureCalculator.station_pressure(
            p_sea_level=request.sea_level_pressure,
            elevation_m=request.elevation
        )
        
        pressure_drop = request.sea_level_pressure - station_pressure
        pressure_ratio = station_pressure / request.sea_level_pressure
        
        logger.info(
            f"Station pressure calculated: {station_pressure:.2f}mbar "
            f"(drop: {pressure_drop:.2f}mbar, ratio: {pressure_ratio:.4f})"
        )
        
        return PressureResponse(
            station_pressure=station_pressure,
            sea_level_pressure=request.sea_level_pressure,
            elevation=request.elevation,
            pressure_drop=pressure_drop,
            pressure_ratio=pressure_ratio
        )
        
    except ValidationError as e:
        logger.exception("Validation error in pressure calculation: %s", e)
        raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    except ValueError as e:
        logger.exception("Value error in pressure calculation: %s", e)
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except OverflowError as e:
        logger.exception("Overflow error in pressure calculation: %s", e)
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        logger.exception("Unexpected error in pressure calculation: %s", e)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during pressure calculation"
        )


@router.post("/solar-position", response_model=SolarPositionResponse)
def calculate_solar_position(request: SolarPositionRequest) -> SolarPositionResponse:
    """
    Calculate solar position (zenith angle, elevation) and Earth-Sun distance.
    
    Computes the sun's position in the sky at a given time and location using 
    high-precision astronomical algorithms. Essential for solar energy calculations.
    
    **Outputs:**
    - **Zenith angle**: Angle from vertical (0° = sun directly overhead)
    - **Solar elevation**: Angle above horizon (90° = sun directly overhead)
    - **Earth-Sun distance**: In Astronomical Units (varies ±3% yearly)
    
    **Use cases:**
    - Solar irradiance modeling (direct/diffuse radiation)
    - PV system angle optimization
    - Shading analysis
    - Sun path diagrams
    - Daylighting studies
    
    **Note:** All times are in UTC. Convert local time to UTC before calling.
    
    **Relationship:** elevation = 90° - zenith
    """
    logger.info(
        f"Calculating solar position at ({request.latitude}, {request.longitude}) "
        f"for {request.year}-{request.month:02d}-{request.day:02d} "
        f"{request.hour:02d}:{request.minute:02d}:{request.second:02d}"
    )
    
    try:
        # Calculate or use provided Julian Date
        if request.julian_date is not None:
            julian_date = request.julian_date
            datetime_str = "N/A (JD provided directly)"
        else:
            julian_date = JulianDateCalculator.calculate(
                month=request.month,
                day=request.day,
                year=request.year,
                hour=request.hour,
                minute=request.minute,
                second=request.second
            )
            datetime_str = (
                f"{request.year:04d}-{request.month:02d}-{request.day:02d}T"
                f"{request.hour:02d}:{request.minute:02d}:{request.second:02d}"
            )
        
        # Calculate solar position
        zenith_angle, earth_sun_distance = SolarPositionCalculator.calculate(
            julian_date=julian_date,
            longitude=request.longitude,
            latitude=request.latitude
        )
        
        solar_elevation = 90.0 - zenith_angle
        
        logger.info(
            f"Solar position calculated: zenith={zenith_angle:.2f}°, "
            f"elevation={solar_elevation:.2f}°, distance={earth_sun_distance:.6f}AU"
        )
        
        return SolarPositionResponse(
            zenith_angle=zenith_angle,
            solar_elevation=solar_elevation,
            earth_sun_distance=earth_sun_distance,
            julian_date=julian_date,
            datetime_utc=datetime_str,
            latitude=request.latitude,
            longitude=request.longitude
        )
        
    except ValidationError as e:
        logger.exception("Validation error in solar position calculation: %s", e)
        raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    except ValueError as e:
        logger.exception("Value error in solar position calculation: %s", e)
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except OverflowError as e:
        logger.exception("Overflow error in solar position calculation: %s", e)
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        logger.exception("Unexpected error in solar position calculation: %s", e)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during solar position calculation"
        )


@router.post("/solar-position/batch", response_model=SolarPositionBatchResponse)
def calculate_solar_position_batch(request: SolarPositionBatchRequest) -> SolarPositionBatchResponse:
    """
    Calculate solar positions for multiple hours on a single day at one location.
    
    Efficiently computes hourly solar positions without making separate API calls.
    Useful for generating sun path diagrams or analyzing daily solar patterns.
    
    **Use cases:**
    - Daily solar trajectory analysis
    - Sunrise/sunset time estimation
    - Optimal panel angle determination
    - Shading analysis throughout the day
    - PV system performance modeling
    
    **Example:** Calculate sun position every hour from sunrise to sunset on summer solstice.
    
    **Note:** All times are in UTC. Results include negative elevations (sun below horizon).
    """
    logger.info(
        f"Batch solar position calculation at ({request.latitude}, {request.longitude}) "
        f"for {request.year}-{request.month:02d}-{request.day:02d}, "
        f"hours {request.hour_start}-{request.hour_end} (step: {request.hour_step})"
    )
    
    try:
        hourly_positions = []
        
        for hour in range(request.hour_start, request.hour_end + 1, request.hour_step):
            # Calculate Julian Date for this hour
            julian_date = JulianDateCalculator.calculate(
                month=request.month,
                day=request.day,
                year=request.year,
                hour=hour,
                minute=0,
                second=0
            )
            
            # Calculate solar position
            zenith_angle, earth_sun_distance = SolarPositionCalculator.calculate(
                julian_date=julian_date,
                longitude=request.longitude,
                latitude=request.latitude
            )
            
            solar_elevation = 90.0 - zenith_angle
            
            datetime_str = (
                f"{request.year:04d}-{request.month:02d}-{request.day:02d}T"
                f"{hour:02d}:00:00"
            )
            
            hourly_positions.append({
                "hour": hour,
                "datetime_utc": datetime_str,
                "julian_date": julian_date,
                "zenith_angle": round(zenith_angle, 4),
                "solar_elevation": round(solar_elevation, 4),
                "earth_sun_distance": round(earth_sun_distance, 6)
            })
        
        date_str = f"{request.year:04d}-{request.month:02d}-{request.day:02d}"
        
        logger.info(
            f"Batch calculation completed: {len(hourly_positions)} positions calculated"
        )
        
        return SolarPositionBatchResponse(
            latitude=request.latitude,
            longitude=request.longitude,
            date=date_str,
            hourly_positions=hourly_positions
        )
        
    except ValidationError as e:
        logger.exception("Validation error in batch solar position calculation: %s", e)
        raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    except ValueError as e:
        logger.exception("Value error in batch solar position calculation: %s", e)
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except OverflowError as e:
        logger.exception("Overflow error in batch solar position calculation: %s", e)
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except Exception as e:
        logger.exception("Unexpected error in batch solar position calculation: %s", e)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during batch solar position calculation"
        )
