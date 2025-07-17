from pydantic import BaseModel

class LogSettings(BaseModel):
    app_name: str = "app"  # Used for log file naming, e.g., logs/app.log
    level: str = "INFO"  # Loguru default level
    format: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    rotation: str = "10 MB"  # Log file rotation interval
    retention: str = "7 days"  # Log file retention period
    compression: str = "zip"  # Log file compression
    enqueue: bool = True  # Use multiprocessing-safe logging
    backtrace: bool = True  # Show backtrace in errors
    diagnose: bool = True  # Show variable values in errors
    serialize: bool = False  # Output logs as JSON if True
    colorize: bool = True  # Colorize output in terminal

