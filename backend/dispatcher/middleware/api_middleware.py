import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class APIMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except HTTPException as ex:
            logger.error(f"Handled error occured. {ex}")
            return JSONResponse(
                status_code=ex.status_code,
                content={"error": ex.detail},
            )
        except Exception as ex:
            logger.error(f"Unknown error occured. {ex}")
            return JSONResponse(
                status_code=500,
                content={"error": "Something went wrong down the line."},
            )
