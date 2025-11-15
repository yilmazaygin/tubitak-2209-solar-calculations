import requests
from typing import List, Dict, Tuple, Any
from collections import defaultdict
from ..schemas.pvgis_schemas import *
from ..core.logger import app_logger as logger
from ..core.response_utils import truncate_large_arrays, get_response_summary


class PVGISService:
    """Service for interacting with all PVGIS API endpoints."""
    
    BASE_URL_V52 = "https://re.jrc.ec.europa.eu/api/v5_2"
    BASE_URL_V53 = "https://re.jrc.ec.europa.eu/api/v5_3"
    TIMEOUT = 30
    
    @staticmethod
    def _make_request(endpoint: str, params: Dict[str, Any], use_v53: bool = False, truncate_response: bool = True) -> Dict:
        """
        Make HTTP request to PVGIS API with error handling.
        
        Args:
            endpoint: API endpoint name (e.g., 'PVcalc', 'seriescalc')
            params: Query parameters
            use_v53: Use PVGIS 5.3 instead of 5.2
            truncate_response: Whether to truncate large arrays for client compatibility
        
        Returns:
            Parsed JSON response
            
        Raises:
            RuntimeError: On API errors or connection issues
        """
        try:
            base_url = PVGISService.BASE_URL_V53 if use_v53 else PVGISService.BASE_URL_V52
            url = f"{base_url}/{endpoint}"
            
            # Remove None values and add required defaults
            clean_params = {k: v for k, v in params.items() if v is not None}
            
            # Ensure outputformat and browser are set
            if 'outputformat' not in clean_params:
                clean_params['outputformat'] = 'json'
            if 'browser' not in clean_params:
                clean_params['browser'] = '0'
            
            logger.info(f"Requesting PVGIS {endpoint} with params: {clean_params}")
            
            response = requests.get(url, params=clean_params, timeout=PVGISService.TIMEOUT)
            
            # Log response details for debugging
            logger.info(f"PVGIS response status: {response.status_code}, content-type: {response.headers.get('content-type', 'unknown')}")
            
            response.raise_for_status()
            
            # Check if response is actually JSON
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                logger.error(f"PVGIS returned non-JSON response. Content-Type: {content_type}, Body preview: {response.text[:500]}")
                raise ValueError(f"PVGIS API returned non-JSON response (Content-Type: {content_type}). This may indicate invalid parameters.")
            
            data = response.json()
            
            # Check for PVGIS error messages
            if "message" in data and "error" in data.get("message", "").lower():
                raise ValueError(f"PVGIS API error: {data['message']}")
            
            # Log successful response summary
            logger.info(f"PVGIS {endpoint} response received successfully. Keys: {list(data.keys())}")
            if 'outputs' in data:
                logger.info(f"Response outputs keys: {list(data['outputs'].keys())}")
                # Log data sizes for arrays
                for key, value in data['outputs'].items():
                    if isinstance(value, list):
                        logger.info(f"  - {key}: {len(value)} records")
            
            # Truncate large arrays for client compatibility (uses MAX_RECORDS_PER_ARRAY from config)
            if truncate_response:
                data = truncate_large_arrays(data)
            
            return data
            
        except requests.Timeout as e:
            raise RuntimeError(f"PVGIS API request timed out: {str(e)}") from e
        
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                raise RuntimeError("Rate limit exceeded (30 calls/second). Please wait and try again.") from e
            elif e.response.status_code == 529:
                raise RuntimeError("PVGIS server is overloaded. Please try again in a few seconds.") from e
            else:
                # Try to get response body for better error message
                try:
                    error_body = e.response.text[:500]
                    raise RuntimeError(f"HTTP {e.response.status_code} from PVGIS API. Response: {error_body}") from e
                except:
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
            
            # Don't truncate response since we need all data for internal processing
            data = PVGISService._make_request("seriescalc", params, truncate_response=False)
            
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
    
    
    
