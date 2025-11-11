from fastapi import APIRouter, HTTPException
from fastapi import status as http_status
from pydantic import ValidationError
from ..core.logger import app_logger as logger
from ..services.birdmodel import BirdModel
from ..schemas.solar_io_schemas import SolarInputsSchema, SolarOutputsSchema

router = APIRouter(prefix="/calculator", tags=["Calculator"])


@router.post("/bird_model", response_model=SolarOutputsSchema)
def bird_model(inputs: SolarInputsSchema) -> SolarOutputsSchema:
    """Calculate solar outputs using the Bird model."""
    logger.debug("Starting Bird model calculation")

    try:
        outputs = BirdModel.calculate(inputs)

        # Sanity-check the result before constructing the response model
        if outputs is None:
            logger.error("BirdModel.calculate returned None for inputs: %s", inputs)
            raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Model returned no result")

        # Log output fields at debug level (avoid printing to stdout)
        try:
            output_dict = outputs.__dict__

        except Exception:
            # If outputs isn't a simple dataclass-like object, try to coerce
            logger.debug("Outputs has no __dict__, attempting to coerce to dict")
            output_dict = dict(outputs)

        logger.debug("Bird model outputs: %s", output_dict)
        return SolarOutputsSchema(**output_dict)

    except ValidationError as e:
        logger.exception("Validation error while processing Bird model: %s", e)
        raise HTTPException(status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    except ValueError as e:
        logger.exception("Value error in Bird model calculation: %s", e)
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))

    except HTTPException:
        # Re-raise HTTPExceptions we intentionally raised above
        raise

    except Exception as e:
        logger.exception("Unexpected error in Bird model endpoint: %s", e)
        raise HTTPException(status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Internal server error while calculating Bird model")