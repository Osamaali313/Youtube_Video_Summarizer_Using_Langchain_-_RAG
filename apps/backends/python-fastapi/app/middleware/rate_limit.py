"""
Rate limiting middleware
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
from loguru import logger

from app.config import settings
from app.tools.cache import rate_limit_cache


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""

    def __init__(
        self,
        app,
        requests_per_period: int = None,
        period_seconds: int = None
    ):
        super().__init__(app)
        self.requests_per_period = requests_per_period or settings.RATE_LIMIT_REQUESTS
        self.period_seconds = period_seconds or settings.RATE_LIMIT_PERIOD

    async def dispatch(self, request: Request, call_next: Callable):
        """Process request with rate limiting"""
        # Skip rate limiting for health check and docs
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get identifier (IP address)
        identifier = self._get_identifier(request)

        # Check rate limit
        allowed, remaining = await rate_limit_cache.check_rate_limit(
            identifier=identifier,
            max_requests=self.requests_per_period,
            window_seconds=self.period_seconds
        )

        # Add rate limit headers
        response = None

        if allowed:
            # Process request
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_period)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(self.period_seconds)

        else:
            # Rate limit exceeded
            logger.warning(
                f"Rate limit exceeded for {identifier} on {request.url.path}"
            )

            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {self.requests_per_period} requests per {self.period_seconds} seconds.",
                    "retry_after": self.period_seconds
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_period),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(self.period_seconds),
                    "Retry-After": str(self.period_seconds)
                }
            )

        return response

    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting"""
        # Try to get real IP if behind proxy
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Use client IP
        client_host = request.client.host if request.client else "unknown"
        return client_host


# Helper function to apply rate limit to specific endpoints
def rate_limit(max_requests: int, window_seconds: int):
    """
    Decorator for route-specific rate limiting

    Usage:
        @app.post("/api/summarize")
        @rate_limit(max_requests=10, window_seconds=60)
        async def summarize():
            ...
    """
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            identifier = request.client.host if request.client else "unknown"

            allowed, remaining = await rate_limit_cache.check_rate_limit(
                identifier=f"endpoint:{func.__name__}:{identifier}",
                max_requests=max_requests,
                window_seconds=window_seconds
            )

            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded for this endpoint",
                        "max_requests": max_requests,
                        "window_seconds": window_seconds
                    }
                )

            return await func(request, *args, **kwargs)

        return wrapper
    return decorator
