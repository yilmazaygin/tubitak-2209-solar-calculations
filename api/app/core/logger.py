import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logger(name: str = "unnamed_logger", level: str = "DEBUG") -> logging.Logger:
    """
    Creates and configures a logger instance.\n
    Logs to both stdout and a daily log file under /api/logs/.
    """
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    # Find /api directory (2 levels up from /api/app/core/logger.py)
    base_dir = Path(__file__).resolve().parents[1].parent
    log_dir = base_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"{datetime.now():%Y-%m-%d}.log"

    # Include the source filename so logs show which file emitted the message.
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s, %(filename)s: %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(level)
    logger.propagate = False

    return logger


# Global reusable logger instances
app_logger = setup_logger("app_logger", "DEBUG")
app_logger.info("Logger initialized.")
