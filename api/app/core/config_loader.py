# api/app/infrastructure/config/loader.py
from pathlib import Path
from pydantic import AnyUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from .logger import app_logger as logger

MAX_DECIMAL_PRECISION = 28

class Settings(BaseSettings):
    """Minimal configuration loader for the Solar API project."""
    
    DATABASE_URL: AnyUrl = Field(..., description="PostgreSQL connection URL")
    DECIMAL_PRECISION: int = Field(default=10, description="Default precision for Decimal calculations")
    YEAR_LIMIT_START: int = Field(default=1900, description="Minimum valid year for date inputs")
    YEAR_LIMIT_END: int = Field(default=2100, description="Maximum valid year for date inputs")
    MAX_RECORDS_PER_ARRAY: int = Field(default=500, description="Max records per array in API responses to prevent client issues")
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("DECIMAL_PRECISION", mode="before")
    @classmethod
    def validate_decimal_precision(cls, v):
        try:
            v_int = int(v)
            if v_int <= 0 or v_int > MAX_DECIMAL_PRECISION:
                # Hatalıysa default kullan ve logla
                logger.error(
                    f"DECIMAL_PRECISION '{v}' out of range (1-{MAX_DECIMAL_PRECISION}), using default 10."
                )
                return 10
            return v_int
        except Exception as e:
            logger.error(f"Invalid DECIMAL_PRECISION '{v}', using default 10. Error: {e}")
            return 10


# Get project root and construct full path to .env
base_dir = Path(__file__).resolve().parents[3]  # 3 levels up from this file
env_file = base_dir / ".env"

# Singleton settings instance
settings = Settings(_env_file=env_file)
logger.info(f"Configuration loaded from {env_file}")
