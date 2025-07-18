from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exception_handlers: dict):
        super().__init__(app)
        self.exception_handlers = exception_handlers

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            exc_type = type(exc)
            handler = self.exception_handlers.get(exc_type)
            if handler:
                return await handler(request, exc)
            # Default fallback
            return JSONResponse(status_code=500, content={"detail": str(exc)})
