import math
from ..core.logger import app_logger as logger


class PressureCalculator:
    """Utility class for atmospheric pressure conversion."""

    @staticmethod
    def station_pressure(p_sea_level: float, elevation_m: float) -> float:
        """
        Convert sea-level pressure to station pressure using exponential approximation.
        Input validation is handled by schemas/dataclasses before this method is called.
        """
        try:
            logger.debug(f"Calculating station pressure: sea_level={p_sea_level}mbar, elevation={elevation_m}m")
            
            H = float(elevation_m) / 1000.0
            
            # Apply exponential approximation formula for pressure decrease with altitude
            # Formula accounts for both linear and quadratic elevation effects
            pressure = float(p_sea_level) * math.exp(-0.119 * H - 0.0013 * H * H)
            
            logger.debug(f"Station pressure calculated: {pressure:.2f}mbar")
            
            return pressure

        except OverflowError as e:
            logger.error(f"Overflow error in pressure calculation for elevation {elevation_m}m")
            raise OverflowError(
                f"Numeric overflow in pressure calculation for elevation {elevation_m}m. "
                f"Error: {str(e)}"
            ) from e
        
        except (ValueError, ZeroDivisionError) as e:
            logger.error(f"Mathematical error in pressure calculation: {str(e)}")
            raise RuntimeError(f"Mathematical error during pressure calculation: {str(e)}") from e
        
        except Exception as e:
            logger.error(f"Unexpected error in pressure calculation: {str(e)}")
            raise RuntimeError(f"Unexpected error in pressure calculation: {str(e)}") from e