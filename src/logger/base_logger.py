from loguru import logger
from typing import Optional

class BaseLogger:
    def __init__(self, config: Optional[dict] = None):
        self.logger = logger
        if config:
            self.configure(config)

    def configure(self, config: dict):
        # Remove default handlers
        self.logger.remove()
        # Add new handler from config
        self.logger.add(
            config.get("sink", "sys.stderr"),
            level=config.get("level", "INFO"),
            format=config.get("format", "<green>{time}</green> <level>{message}</level>"),
            rotation=config.get("rotation", None),
            retention=config.get("retention", None),
            compression=config.get("compression", None),
            enqueue=config.get("enqueue", False),
        )

    def get_logger(self):
        return self.logger

