import sys
from loguru import logger
from typing import Optional
from src.config.log_settings import LogSettings

class BaseLogger:
    @staticmethod
    def configure(settings: LogSettings):
        logger.remove()
        # Console handler
        logger.add(
            sys.stdout,
            format=settings.format,
            level=settings.level,
            enqueue=settings.enqueue,
            backtrace=settings.backtrace,
            diagnose=settings.diagnose,
            serialize=settings.serialize,
            colorize=settings.colorize,
        )
        # Optional: File handler with dynamic app name
        log_file_path = f"logs/{settings.app_name}.log"
        logger.add(
            log_file_path,
            rotation=settings.rotation,
            retention=settings.retention,
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
            compression=settings.compression,
            enqueue=settings.enqueue,
            backtrace=settings.backtrace,
            diagnose=settings.diagnose,
            serialize=settings.serialize,
            colorize=settings.colorize,
        )

