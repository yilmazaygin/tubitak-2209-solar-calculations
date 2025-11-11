from fastapi import APIRouter, HTTPException
from fastapi import status as http_status
from pydantic import ValidationError
from typing import Dict, Any
from ..core.logger import app_logger as logger
from ..services.pvgis import PVGISService
from ..schemas.pvgis_schemas import *

router = APIRouter(prefix="/pvgis", tags=["PVGIS"])


@router.post("/pvcalc", response_model=Dict[str, Any])
def pv_calculator(request: PVCalcRequest) -> Dict[str, Any]:
    """
    Calculate PV energy production for grid-connected systems.
    
    Supports:
    - Fixed mounting systems
    - Single-axis tracking (horizontal, vertical, inclined)
    - Two-axis tracking
    - Optimal angle calculation
    - Economic analysis (optional)
    
    Returns monthly and yearly energy production, optimal angles, and system performance metrics.
    """
    logger.info(f"PVcalc request for ({request.lat}, {request.lon}), power={request.peakpower}kW")
    
    try:
        result = PVGISService.pvcalc(request)
        logger.info("PVcalc completed successfully")
        return result
        
    except ValidationError as e:
        logger.exception("Validation error in PVcalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    except RuntimeError as e:
        logger.exception("Runtime error in PVcalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_502_BAD_GATEWAY, detail=str(e))
    
    except Exception as e:
        logger.exception("Unexpected error in PVcalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error in PVcalc")


@router.post("/shscalc", response_model=Dict[str, Any])
def off_grid_calculator(request: SHSCalcRequest) -> Dict[str, Any]:
    """
    Calculate performance of off-grid (stand-alone) PV systems with battery storage.
    
    Analyzes:
    - Battery charge/discharge cycles
    - System autonomy
    - Energy deficit/surplus
    - Optimal battery and PV sizing
    
    Useful for remote installations, backup power systems, and off-grid applications.
    """
    logger.info(f"SHScalc request for ({request.lat}, {request.lon}), battery={request.batterysize}Wh")
    
    try:
        result = PVGISService.shscalc(request)
        logger.info("SHScalc completed successfully")
        return result
        
    except ValidationError as e:
        logger.exception("Validation error in SHScalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    except RuntimeError as e:
        logger.exception("Runtime error in SHScalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_502_BAD_GATEWAY, detail=str(e))
    
    except Exception as e:
        logger.exception("Unexpected error in SHScalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error in SHScalc")


@router.post("/mrcalc", response_model=Dict[str, Any])
def monthly_radiation(request: MRCalcRequest) -> Dict[str, Any]:
    """
    Calculate monthly average radiation values.
    
    Can output:
    - Horizontal plane irradiation
    - Optimal angle plane irradiation
    - Selected angle irradiation
    - Direct normal irradiation (DNI)
    - Diffuse to global ratio
    - Average daily temperature
    
    Returns monthly averages over the specified year range.
    """
    logger.info(f"MRcalc request for ({request.lat}, {request.lon})")
    
    try:
        result = PVGISService.mrcalc(request)
        logger.info("MRcalc completed successfully")
        return result
        
    except ValidationError as e:
        logger.exception("Validation error in MRcalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    except RuntimeError as e:
        logger.exception("Runtime error in MRcalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_502_BAD_GATEWAY, detail=str(e))
    
    except Exception as e:
        logger.exception("Unexpected error in MRcalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error in MRcalc")


@router.post("/drcalc", response_model=Dict[str, Any])
def daily_radiation(request: DRCalcRequest) -> Dict[str, Any]:
    """
    Calculate daily radiation profiles for a specific month.
    
    Set month=0 to get data for all 12 months.
    
    Can output:
    - Global, direct, and diffuse irradiances
    - Two-axis tracking irradiances
    - Clear-sky irradiance
    - Daily temperature profile
    
    Returns hour-by-hour values for each day of the month.
    """
    logger.info(f"DRcalc request for ({request.lat}, {request.lon}), month={request.month}")
    
    try:
        result = PVGISService.drcalc(request)
        logger.info("DRcalc completed successfully")
        return result
        
    except ValidationError as e:
        logger.exception("Validation error in DRcalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    except RuntimeError as e:
        logger.exception("Runtime error in DRcalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_502_BAD_GATEWAY, detail=str(e))
    
    except Exception as e:
        logger.exception("Unexpected error in DRcalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error in DRcalc")


@router.post("/seriescalc", response_model=Dict[str, Any])
def hourly_time_series(request: SeriesCalcRequest) -> Dict[str, Any]:
    """
    Get hourly radiation time series data for a multi-year period.
    
    Optionally includes PV power production estimates.
    
    Returns:
    - Hourly irradiance values (G(i), Gb(i), Gd(i))
    - Sun position (height, azimuth)
    - Temperature and wind speed
    - PV power output (if pvcalculation=1)
    
    Useful for detailed energy simulations and validations.
    """
    logger.info(f"Seriescalc request for ({request.lat}, {request.lon}), years={request.startyear}-{request.endyear}")
    
    try:
        result = PVGISService.seriescalc(request)
        logger.info("Seriescalc completed successfully")
        return result
        
    except ValidationError as e:
        logger.exception("Validation error in Seriescalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    except RuntimeError as e:
        logger.exception("Runtime error in Seriescalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_502_BAD_GATEWAY, detail=str(e))
    
    except Exception as e:
        logger.exception("Unexpected error in Seriescalc: %s", e)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error in Seriescalc")


@router.post("/tmy", response_model=Dict[str, Any])
def typical_meteorological_year(request: TMYRequest) -> Dict[str, Any]:
    """
    Get Typical Meteorological Year (TMY) data.
    
    TMY consists of 12 representative months selected from a multi-year dataset
    to represent typical weather conditions.
    
    Useful for:
    - Energy simulation software (EnergyPlus, etc.)
    - Long-term performance predictions
    - System design validation
    
    Can export in CSV, JSON, or EPW (EnergyPlus Weather) format.
    """
    logger.info(f"TMY request for ({request.lat}, {request.lon}), years={request.startyear}-{request.endyear}")
    
    try:
        result = PVGISService.tmy(request)
        logger.info("TMY completed successfully")
        return result
        
    except ValidationError as e:
        logger.exception("Validation error in TMY: %s", e)
        raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    except RuntimeError as e:
        logger.exception("Runtime error in TMY: %s", e)
        raise HTTPException(status_code=http_status.HTTP_502_BAD_GATEWAY, detail=str(e))
    
    except Exception as e:
        logger.exception("Unexpected error in TMY: %s", e)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error in TMY")


@router.post("/horizon", response_model=Dict[str, Any])
def horizon_profile(request: HorizonRequest) -> Dict[str, Any]:
    """
    Get horizon profile data for a location.
    
    Returns the height of the horizon (in degrees) at different azimuth angles
    around the point of interest.
    
    Useful for:
    - Shading analysis
    - Solar access studies
    - Site assessment
    
    Can also validate user-supplied horizon data.
    """
    logger.info(f"Horizon request for ({request.lat}, {request.lon})")
    
    try:
        result = PVGISService.printhorizon(request)
        logger.info("Horizon completed successfully")
        return result
        
    except ValidationError as e:
        logger.exception("Validation error in Horizon: %s", e)
        raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    except RuntimeError as e:
        logger.exception("Runtime error in Horizon: %s", e)
        raise HTTPException(status_code=http_status.HTTP_502_BAD_GATEWAY, detail=str(e))
    
    except Exception as e:
        logger.exception("Unexpected error in Horizon: %s", e)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error in Horizon")


@router.post("/day-average", response_model=PVGISDayAverageResponse)
def get_day_average(request: PVGISDayAverageRequest) -> PVGISDayAverageResponse:
    """
    Calculate hourly average solar data for a specific day across multiple years.
    
    For example, requesting April 15 will return the average hourly data
    for all April 15ths between start_year and end_year from PVGIS historical data.
    
    This is useful for predicting typical solar production on a given calendar day.
    """
    logger.info(
        f"Calculating day average for {request.month:02d}/{request.day:02d} "
        f"at ({request.latitude}, {request.longitude})"
    )
    
    try:
        result = PVGISService.calculate_day_average(request)
        
        logger.info(
            f"Successfully calculated averages for {len(result.years_analyzed)} years. "
            f"Peak: {result.peak_irradiance:.2f} W/m² at hour {result.peak_hour}"
        )
        
        return result
        
    except ValidationError as e:
        logger.exception("Validation error in PVGIS day average: %s", e)
        raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    
    except ValueError as e:
        logger.exception("Value error in PVGIS day average: %s", e)
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    except RuntimeError as e:
        logger.exception("Runtime error in PVGIS day average: %s", e)
        raise HTTPException(status_code=http_status.HTTP_502_BAD_GATEWAY, detail=f"Error communicating with PVGIS API: {str(e)}")
    
    except Exception as e:
        logger.exception("Unexpected error in PVGIS day average endpoint: %s", e)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error while calculating day average")
