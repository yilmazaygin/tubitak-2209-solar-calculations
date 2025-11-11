import requests
from ..schemas.pvgis_schemas import PVGISDayAverageRequest, PVGISDayAverageResponse, PVGISBasicRequest, HourlyData
from ..core.logger import app_logger as logger
from .pvgis import PVGISService
from collections import defaultdict

class PVGISPlusService:
    @staticmethod
    def calculate_day_average(request: PVGISDayAverageRequest) -> PVGISDayAverageResponse:
        """
        Calculate hourly averages for a specific day across multiple years.
        Input validation is handled by schemas/dataclasses before this method is called.
        
        For example: April 15 - calculate average for each hour (0-23) across all April 15ths
        from start_year to end_year.
        """
        try:
            # Fetch data from PVGIS
            basic_request = PVGISBasicRequest(
                latitude=request.latitude,
                longitude=request.longitude,
                start_year=request.start_year,
                end_year=request.end_year,
                slope=request.slope,
                azimuth=request.azimuth
            )
            
            metadata, hourly_data = PVGISService.fetch_hourly_data(basic_request)
            
            # Filter for specific month/day and group by hour
            target_date = f"{request.month:02d}{request.day:02d}"
            hourly_groups = defaultdict(list)
            years_found = set()
            
            logger.info(f"Filtering data for month={request.month}, day={request.day}")
            
            for record in hourly_data:
                timestamp = record.get("time", "")
                # Format: YYYYMMDD:HHMM
                if len(timestamp) >= 8:
                    date_part = timestamp[4:8]  # MMDD
                    year = int(timestamp[:4])
                    
                    if date_part == target_date:
                        hour = int(timestamp[9:11])  # Extract HH from :HHMM
                        years_found.add(year)
                        
                        hourly_groups[hour].append({
                            "G_i": record.get("G(i)", 0.0),
                            "H_sun": record.get("H_sun", 0.0),
                            "T2m": record.get("T2m", 0.0),
                            "WS10m": record.get("WS10m", 0.0),
                            "Int": record.get("Int", 0.0)
                        })
            
            if not hourly_groups:
                raise ValueError(
                    f"No data found for {request.month:02d}/{request.day:02d} "
                    f"in years {request.start_year}-{request.end_year}"
                )
            
            logger.info(f"Found data for {len(years_found)} years: {sorted(years_found)}")
            
            # Calculate averages for each hour
            hourly_averages = []
            peak_hour = 0
            peak_irradiance = 0.0
            daily_total = 0.0
            
            for hour in range(24):
                if hour in hourly_groups:
                    records = hourly_groups[hour]
                    
                    avg_data = HourlyData(
                        hour=hour,
                        G_i=sum(r["G_i"] for r in records) / len(records),
                        H_sun=sum(r["H_sun"] for r in records) / len(records),
                        T2m=sum(r["T2m"] for r in records) / len(records),
                        WS10m=sum(r["WS10m"] for r in records) / len(records),
                        Int=sum(r["Int"] for r in records) / len(records),
                        sample_count=len(records)
                    )
                    
                    hourly_averages.append(avg_data)
                    daily_total += avg_data.G_i
                    
                    if avg_data.G_i > peak_irradiance:
                        peak_irradiance = avg_data.G_i
                        peak_hour = hour
                else:
                    # No data for this hour, add zeros
                    hourly_averages.append(HourlyData(
                        hour=hour,
                        G_i=0.0,
                        H_sun=0.0,
                        T2m=0.0,
                        WS10m=0.0,
                        Int=0.0,
                        sample_count=0
                    ))
            
            logger.info(
                f"Calculated averages: peak at hour {peak_hour} "
                f"with {peak_irradiance:.2f} W/m², daily total: {daily_total:.2f} Wh/m²"
            )
            
            return PVGISDayAverageResponse(
                latitude=metadata.latitude,
                longitude=metadata.longitude,
                month=request.month,
                day=request.day,
                years_analyzed=sorted(list(years_found)),
                hourly_averages=hourly_averages,
                peak_hour=peak_hour,
                peak_irradiance=peak_irradiance,
                daily_total_energy=daily_total
            )
            
        except ValueError as e:
            raise RuntimeError(f"Data processing error: {str(e)}") from e
        
        except Exception as e:
            raise RuntimeError(f"Unexpected error in day average calculation: {str(e)}") from e