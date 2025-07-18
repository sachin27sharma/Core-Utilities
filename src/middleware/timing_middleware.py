from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger
from time import perf_counter


class AuditTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = perf_counter()
        try:
            response = await call_next(request)
        except Exception as e:
            duration = (perf_counter() - start_time) * 1000
            logger.exception(
                f"Exception for {request.method} {request.url.path} after {duration:.2f} ms"
            )
            raise e

        duration = (perf_counter() - start_time) * 1000

        logger.info(
            f"{request.method} {request.url.path} completed in {duration:.2f} ms "
            f"with status {response.status_code} from {request.client.host}"
        )

        response.headers["X-Response-Time"] = f"{duration:.2f}ms"
        return response
