import logging
import sys
from loguru import logger
from app.core.config import settings

class InterceptHandler(logging.Handler):
    """
    Intercept standard logging messages and route them to Loguru.
    """
    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def setup_logging():
    # Remove standard loggers
    logging.getLogger().handlers = [InterceptHandler()]
    
    # Configure Loguru
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
                "level": "INFO",
            }
        ]
    )
    
    # Optional: Log to file in JSON format for production ingestion
    # logger.add("logs/app.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", serialize=True)
