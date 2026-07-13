import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import settings
from app.utils.logger import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        start = time.time()

        response = await call_next(request)

        duration_ms = int((time.time() - start) * 1000)
        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        response.headers["X-Request-ID"] = request_id
        return response


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.error(
                "unhandled error",
                extra={
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                },
                exc_info=settings.debug,
            )
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"code": 500, "message": "Internal server error"},
            )
