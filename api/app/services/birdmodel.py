# https://instesre.org/Solar/BirdModelNew.htm

from ..dataclasses.solar_io_dc import SolarInputsDataclass, SolarOutputsDataclass
import math
from ..utils.julianday import JulianDateCalculator
from ..utils.pressure import PressureCalculator
from ..utils.solar_position import SolarPositionCalculator
from ..core.logger import app_logger as logger

class BirdModel:
    """Implementation of the Bird & Hulstrom (1981) clear sky irradiance model."""

    @staticmethod
    def calculate(inputs: SolarInputsDataclass) -> SolarOutputsDataclass:
        """Run the Bird model with the given inputs."""
        
        logger.info(
            f"Starting Bird model calculation for ({inputs.latitude}, {inputs.longitude}) "
            f"on {inputs.year}-{inputs.month:02d}-{inputs.day:02d} {inputs.hour:02d}:{inputs.minute:02d}"
        )
        
        try:
            jd = JulianDateCalculator.calculate(
                inputs.month, inputs.day, inputs.year,
                inputs.hour, inputs.minute, inputs.second
            )

            p = PressureCalculator.station_pressure(inputs.station_pressure, inputs.elevation)
            zenith_angle, R = SolarPositionCalculator.calculate(jd, inputs.longitude, inputs.latitude)
            
            logger.debug(f"Initial calculations: JD={jd:.2f}, pressure={p:.2f}mbar, zenith={zenith_angle:.2f}°")

            dr = math.pi / 180.0
            Z_rad = zenith_angle * dr

            # Relative air mass
            AM = 1.0 / (math.cos(Z_rad) + 0.15 * pow(93.885 - zenith_angle, -1.25))
            AMp = AM * p / 1013.0
            
            logger.debug(f"Air mass: AM={AM:.4f}, AMp={AMp:.4f}")

            # Rayleigh scattering
            Tr = math.exp(-0.0903 * pow(AMp, 0.84) * (1.0 + AMp - pow(AMp, 1.01)))

            # Ozone absorption
            Ozm = inputs.ozone * AM
            Toz = (1.0 - 0.1611 * Ozm * pow(1.0 + 139.48 * Ozm, -0.3035) -
                   0.002715 * Ozm / (1.0 + 0.044 * Ozm + 0.0003 * Ozm * Ozm))

            # Mixed gases
            Tm = math.exp(-0.0127 * pow(AMp, 0.26))

            # Water vapor
            Wm = AM * inputs.water_vapor
            Tw = 1.0 - 2.4959 * Wm / ((1.0 + pow(79.034 * Wm, 0.6828)) + 6.385 * Wm)

            # Aerosols
            Tau = 0.2758 * inputs.aot380 + 0.35 * inputs.aot500
            Ta = math.exp((-pow(Tau, 0.873)) * (1.0 + Tau - pow(Tau, 0.7088)) * pow(AM, 0.9108))
            TAA = 1.0 - 0.1 * (1.0 - AM + pow(AM, 1.06)) * (1.0 - Ta)
            TAs = Ta / TAA
            Rs = 0.0685 + (1.0 - 0.84) * (1.0 - TAs)
            
            logger.debug(
                f"Atmospheric transmittances: Rayleigh={Tr:.4f}, Ozone={Toz:.4f}, "
                f"MixedGas={Tm:.4f}, Water={Tw:.4f}, Aerosol={Ta:.4f}"
            )

            # Earth–Sun distance correction
            Rsq = 1.0 / (R * R)

            # Direct irradiance
            Id = Rsq * inputs.solar_constant * 0.9662 * Tr * Toz * Tm * Tw * Ta
            Idh = Id * math.cos(Z_rad)

            # Diffuse irradiance
            Ias = 0.79 * inputs.solar_constant * math.cos(Z_rad) * Toz * Tm * Tw * TAA
            Ias *= (0.5 * (1.0 - Tr) + 0.85 * (1.0 - TAs)) / (1.0 - AM + pow(AM, 1.02))

            # Total irradiance
            Itot = (Idh + Ias) / (1.0 - inputs.albedo * Rs)
            Idif = Itot - Idh
            
            logger.info(
                f"Bird model completed: Direct={Idh:.2f} W/m², Diffuse={Idif:.2f} W/m², "
                f"Total={Itot:.2f} W/m²"
            )

            return SolarOutputsDataclass(
                julian_date=jd,
                station_pressure=p,
                earth_sun_distance=R,
                zenith_angle=zenith_angle,
                air_mass=AM,
                corrected_solar_constant=Rsq * inputs.solar_constant,
                direct_horizontal=Idh,
                diffuse_horizontal=Idif,
                total_horizontal=Itot
            )
            
        except Exception as e:
            logger.error(f"Error in Bird model calculation: {str(e)}")
            raise