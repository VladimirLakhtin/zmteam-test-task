"""Logger configuration module."""

import logging
import logging.handlers
import sys
from pathlib import Path

from app.infrastructure.config import settings


def setup_logger(name: str) -> logging.Logger:
    """Set up and configure logger.

    Args:
        name: Logger name

    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(settings.logger.level)

    # Create formatter
    formatter = logging.Formatter(
        fmt=settings.logger.format,
        datefmt=settings.logger.date_format
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if file_path is configured)
    if settings.logger.file_path:
        log_path = Path(settings.logger.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_path,
            maxBytes=settings.logger.max_bytes,
            backupCount=settings.logger.backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Create default logger instance
logger = setup_logger("app")
