"""api/middleware - latency, correlation-id, auth, compression middleware."""
from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LatencyCorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.correlation_id = request.headers.get("x-correlation-id", uuid.uuid4().hex)
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        response.headers["X-Correlation-ID"] = request.state.correlation_id
        response.headers["X-Process-Time-ms"] = f"{elapsed_ms:.3f}"
        if request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "public, max-age=300"
        rt = getattr(request.app.state, "runtime", None)
        if rt is not None:
            rt.monitoring.record_dispatch(elapsed_ms)  # <1ms dispatch budget tracked
        return response
