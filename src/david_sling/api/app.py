"""L14 api/app - FastAPI application factory & lifespan (Phase 1 web version)."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from david_sling import BRAND, __version__
from david_sling.api.middleware import LatencyCorrelationMiddleware
from david_sling.api.routers import (
    analysis,
    audit,
    core,
    market,
    mission_control,
    trade_execution,
)
from david_sling.api.websocket import router as ws_router
from david_sling.core.errors import DavidSlingError

STATIC_DIR = Path(__file__).parent / "static"


def create_app(runtime) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.runtime = runtime
        yield
        await runtime.stop()

    app = FastAPI(title=f"{BRAND} IATOS API", version=__version__, lifespan=lifespan)
    app.state.runtime = runtime
    app.add_middleware(LatencyCorrelationMiddleware)

    # CORS: explicit allowlist - localhost dev + the Arena preview host pattern
    import os

    from fastapi.middleware.cors import CORSMiddleware

    origins = ["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:3000"]
    origins += [o.strip() for o in os.environ.get("DAVID_SLING_ALLOWED_ORIGINS", "").split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=r"https://\d+-[a-z0-9]+\.e2b\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(DavidSlingError)
    async def david_error_handler(request: Request, exc: DavidSlingError):
        from david_sling.api.serialization import ORJSONResponse

        return ORJSONResponse({"error": type(exc).__name__, "message": exc.message,
                               "context": exc.context,
                               "correlation_id": getattr(request.state, "correlation_id", None)}, status_code=400)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        """Global boundary: structured 500 + ledger + alert; the macro-system never crashes."""
        from david_sling.api.serialization import ORJSONResponse

        rt = getattr(app.state, "runtime", None)
        cid = getattr(request.state, "correlation_id", None)
        if rt is not None:
            try:
                rt.ledger.append("api.error", {"path": request.url.path, "error": repr(exc), "cid": cid})
                await rt.alerts.emit("WARNING", f"unhandled API error {request.url.path}: {exc!r}")
            except Exception:
                pass
        return ORJSONResponse({"error": "InternalError", "message": str(exc), "correlation_id": cid},
                              status_code=500)

    for r in (core.router, mission_control.router, trade_execution.router, market.router,
              analysis.router, audit.router, ws_router):
        app.include_router(r)

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    async def index():
        return FileResponse(STATIC_DIR / "index.html")

    return app


async def serve(runtime, host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn

    app = create_app(runtime)
    config = uvicorn.Config(app, host=host, port=port, log_level="info", access_log=False)
    server = uvicorn.Server(config)
    await server.serve()
