from fastapi import FastAPI
from typing import List, Optional, Callable
from fastapi.middleware.cors import CORSMiddleware
from src.config.settings import Settings
from src.core.events.server_events import execute_backend_server_event_handler, terminate_backend_server_event_handler
from src.middleware.list_middleware import MiddlewareList
from src.middleware.exception_middleware import ExceptionHandlerMiddleware
from src.logger.base_logger import BaseLogger
from src.middleware.timing_middleware import AuditTimingMiddleware


class BaseApp:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.settings = self.get_settings(config_path)
        # You can now use self.settings throughout your app

    def get_settings(self, config_path: str):
        """
        Loads settings using the get_settings function from settings.py, passing the config.yaml path.
        """
        from src.config.settings import get_settings
        return get_settings(config_path)

    def setup_middlewares(self, app):
        middleware_list = MiddlewareList()
        middleware_list.add(
            CORSMiddleware,
            allow_origins=self.settings.ALLOWED_ORIGINS,
            allow_credentials=self.settings.IS_ALLOWED_CREDENTIALS,
            allow_methods=self.settings.ALLOWED_METHODS,
            allow_headers=self.settings.ALLOWED_HEADERS,
        )
        exception_handlers = {}  # Add custom exception handlers if needed
        middleware_list.add(
            ExceptionHandlerMiddleware,
            exception_handlers=exception_handlers
        )
        middleware_list.add(
            AuditTimingMiddleware
        )
        # Add more middlewares as needed
        # TBD
        middleware_list.apply(app)

    def setup_logger(self, routers):
        from loguru import logger
        from src.logger.base_logger import BaseLogger
        BaseLogger.configure(self.settings.log_settings)
        logger.info("Starting FastAPI app instance...")
        logger.debug(f"Routers to include: {routers}")
        logger.success("Logger initialized and log file created.")

    def include_routers(self, app, base_router, routers):
        app.include_router(base_router, prefix=self.settings.app.api_prefix)
        if routers:
            for router in routers:
                app.include_router(router, prefix=self.settings.app.api_prefix)

    def create_app(self, routers: Optional[List] = None):
        """
        Returns the FastAPI app instance with the base router and any additional routers included.
        """
        from src.api.base import router as base_router
        app = FastAPI(**self.settings.get_fastapi_cls_attributes)

        self.setup_logger(routers)

        self.setup_middlewares(app)

        app.add_event_handler(
            "startup",
            lambda: execute_backend_server_event_handler(backend_app=app),
        )
        app.add_event_handler(
            "shutdown",
            lambda: terminate_backend_server_event_handler(backend_app=app),
        )

        self.include_routers(app, base_router, routers)
        return app

