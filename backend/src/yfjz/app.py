from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from yfjz.api.provider_configs import router as provider_configs_router
from yfjz.api.runs import router as runs_router
from yfjz.api.suites import router as suites_router
from yfjz.core.errors import register_error_handlers
from yfjz.storage.database import init_db


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(
        title="yfjz LLM Evaluation API",
        version="0.1.0",
        description="Backend API for custom LLM evaluation and benchmark tasks.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        return {"status": "ok", "service": "yfjz-backend"}

    register_error_handlers(app)
    app.include_router(provider_configs_router, prefix="/api")
    app.include_router(suites_router, prefix="/api")
    app.include_router(runs_router, prefix="/api")
    return app


app = create_app()
