# src/core/events/server_events.py

from fastapi import FastAPI
from loguru import logger


def execute_backend_server_event_handler(backend_app: FastAPI):
    logger.info("Executing backend server startup event handler.")
    # Add startup logic here...


def terminate_backend_server_event_handler(backend_app: FastAPI):
    logger.info("Executing backend server shutdown event handler.")
    # Add shutdown logic here ...
