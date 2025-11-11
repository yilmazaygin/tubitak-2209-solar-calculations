from fastapi import APIRouter, HTTPException
from fastapi import status as http_status
from pydantic import ValidationError
from ..core.logger import app_logger as logger
from ..services.pvgis_plus import PVGISPlusService
from ..schemas.pvgis_schemas import (
    PVGISDayAverageRequest,
    PVGISDayAverageResponse
)

router = APIRouter(prefix="/pvgis-plus", tags=["PVGIS Plus"])


@router.post("/day-average", response_model=PVGISDayAverageResponse)
def get_day_average(request: PVGISDayAverageRequest) -> PVGISDayAverageResponse:
    """
    Calculate hourly average solar data for a specific calendar day across multiple years.
    
    This custom analysis tool processes historical PVGIS data to provide:
    - Hourly averages for a specific date (e.g., all April 15ths from 2005-2020)
    - Peak production hour identification
    - Daily total energy calculation
    - Sample counts showing data quality
    
    Use cases:
    - Predict typical solar production on any given calendar day
    - Plan system sizing based on seasonal patterns
    - Forecast battery storage requirements
    - Compare production across different dates
    
    For example, requesting April 15 will return the average hourly data
    for all April 15ths between start_year and end_year from PVGIS historical data.
    """
    logger.info(
        f"Calculating day average for {request.month:02d}/{request.day:02d} "
        f"at ({request.latitude}, {request.longitude})"
    )
    
    try:
        result = PVGISPlusService.calculate_day_average(request)
        
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
