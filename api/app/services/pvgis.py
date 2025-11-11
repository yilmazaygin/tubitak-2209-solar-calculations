import requests
from typing import List, Dict, Tuple, Any
from collections import defaultdict
from ..schemas.pvgis_schemas import *
from ..core.logger import app_logger as logger


class PVGISService:
    """Service for interacting with all PVGIS API endpoints."""
    
    BASE_URL_V52 = "https://re.jrc.ec.europa.eu/api/v5_2"
    BASE_URL_V53 = "https://re.jrc.ec.europa.eu/api/v5_3"
    TIMEOUT = 30
    
    @staticmethod
    def _make_request(endpoint: str, params: Dict[str, Any], use_v53: bool = False) -> Dict:
        """
        Make HTTP request to PVGIS API with error handling.
        
        Args:
            endpoint: API endpoint name (e.g., 'PVcalc', 'seriescalc')
            params: Query parameters
            use_v53: Use PVGIS 5.3 instead of 5.2
        
        Returns:
            Parsed JSON response
            
        Raises:
            RuntimeError: On API errors or connection issues
        """
        try:
            base_url = PVGISService.BASE_URL_V53 if use_v53 else PVGISService.BASE_URL_V52
            url = f"{base_url}/{endpoint}"
            
            # Remove None values
            clean_params = {k: v for k, v in params.items() if v is not None}
            
            logger.info(f"Requesting PVGIS {endpoint} with params: {clean_params}")
            
            response = requests.get(url, params=clean_params, timeout=PVGISService.TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for PVGIS error messages
            if "message" in data and "error" in data.get("message", "").lower():
                raise ValueError(f"PVGIS API error: {data['message']}")
            
            return data
            
        except requests.Timeout as e:
            raise RuntimeError(f"PVGIS API request timed out: {str(e)}") from e
        
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise RuntimeError("Rate limit exceeded (30 calls/second). Please wait and try again.") from e
            elif e.response.status_code == 529:
                raise RuntimeError("PVGIS server is overloaded. Please try again in a few seconds.") from e
            else:
                raise RuntimeError(f"HTTP error from PVGIS API: {str(e)}") from e
        
        except requests.RequestException as e:
            raise RuntimeError(f"Error connecting to PVGIS API: {str(e)}") from e
        
        except ValueError as e:
            raise RuntimeError(f"Error parsing PVGIS response: {str(e)}") from e
        
        except Exception as e:
            raise RuntimeError(f"Unexpected error in PVGIS request: {str(e)}") from e
    
        
    @staticmethod
    def pvcalc(request: PVCalcRequest) -> Dict:
        """
        Calculate PV energy production for grid-connected systems.
        Supports fixed, single-axis, and two-axis tracking configurations.
        """
        try:
            params = request.model_dump(by_alias=True, exclude_none=True, mode='json')
            return PVGISService._make_request("PVcalc", params)
            
        except Exception as e:
            raise RuntimeError(f"Error in PVcalc: {str(e)}") from e
    
        
    @staticmethod
    def shscalc(request: SHSCalcRequest) -> Dict:
        """
        Calculate performance of off-grid (stand-alone) PV systems with battery storage.
        """
        try:
            params = request.model_dump(by_alias=True, exclude_none=True, mode='json')
            return PVGISService._make_request("SHScalc", params)
            
        except Exception as e:
            raise RuntimeError(f"Error in SHScalc: {str(e)}") from e
    
        
    @staticmethod
    def mrcalc(request: MRCalcRequest) -> Dict:
        """
        Calculate monthly radiation values.
        Can output horizontal, optimal angle, or selected angle irradiation.
        """
        try:
            params = request.model_dump(by_alias=True, exclude_none=True, mode='json')
            return PVGISService._make_request("MRcalc", params)
            
        except Exception as e:
            raise RuntimeError(f"Error in MRcalc: {str(e)}") from e
    
        
    @staticmethod
    def drcalc(request: DRCalcRequest) -> Dict:
        """
        Calculate daily radiation profiles for a specific month.
        Set month=0 to get all 12 months.
        """
        try:
            params = request.model_dump(by_alias=True, exclude_none=True, mode='json')
            # Handle 'global' field properly
            if 'global' in params:
                params['global'] = params.pop('global')
            return PVGISService._make_request("DRcalc", params)
            
        except Exception as e:
            raise RuntimeError(f"Error in DRcalc: {str(e)}") from e
    
    
    @staticmethod
    def seriescalc(request: SeriesCalcRequest) -> Dict:
        """
        Get hourly radiation time series data.
        Optionally includes PV power production estimates.
        """
        try:
            params = request.model_dump(by_alias=True, exclude_none=True, mode='json')
            return PVGISService._make_request("seriescalc", params)
            
        except Exception as e:
            raise RuntimeError(f"Error in seriescalc: {str(e)}") from e
    
    
    @staticmethod
    def tmy(request: TMYRequest) -> Dict:
        """
        Get Typical Meteorological Year (TMY) data.
        Useful for energy simulation software like EnergyPlus.
        """
        try:
            params = request.model_dump(by_alias=True, exclude_none=True, mode='json')
            return PVGISService._make_request("tmy", params)
            
        except Exception as e:
            raise RuntimeError(f"Error in TMY: {str(e)}") from e
    
    
    @staticmethod
    def printhorizon(request: HorizonRequest) -> Dict:
        """
        Get horizon profile data for a location.
        Returns height of horizon at different directions.
        """
        try:
            params = request.model_dump(by_alias=True, exclude_none=True, mode='json')
            return PVGISService._make_request("printhorizon", params)
            
        except Exception as e:
            raise RuntimeError(f"Error in printhorizon: {str(e)}") from e
    
    
    # ----Legacy Methods----
    
    @staticmethod
    def fetch_hourly_data(request: PVGISBasicRequest) -> Tuple[PVGISMetadata, List[Dict]]:
        """
        Legacy method: Fetch hourly solar data from PVGIS API using seriescalc.
        Input validation is handled by schemas/dataclasses before this method is called.
        
        Returns:
            Tuple of (metadata, hourly_data_list)
        """
        try:
            params = {
                "lat": request.latitude,
                "lon": request.longitude,
                "startyear": request.start_year,
                "endyear": request.end_year,
                "angle": request.slope,
                "aspect": request.azimuth,
                "outputformat": "json",
                "browser": "0"
            }
            
            logger.info(f"Fetching PVGIS data for lat={request.latitude}, lon={request.longitude}")
            
            data = PVGISService._make_request("seriescalc", params)
            
            # Extract metadata
            inputs = data.get("inputs", {})
            location = inputs.get("location", {})
            mounting = inputs.get("mounting_system", {})
            
            metadata = PVGISMetadata(
                latitude=location.get("latitude", request.latitude),
                longitude=location.get("longitude", request.longitude),
                elevation=location.get("elevation", 0),
                radiation_database=inputs.get("meteo_data", {}).get("source", "Unknown"),
                slope=mounting.get("slope", {}).get("value", request.slope),
                azimuth=mounting.get("azimuth", {}).get("value", request.azimuth)
            )
            
            # Extract hourly data
            hourly_data = data.get("outputs", {}).get("hourly", [])
            
            logger.info(f"Successfully fetched {len(hourly_data)} hourly records")
            
            return metadata, hourly_data
            
        except Exception as e:
            raise RuntimeError(f"Error fetching hourly data: {str(e)}") from e
    
    
    
