"""FastAPI 진입점.

app/domain/*/api.py 를 스캔해 /api/<domain> 에 자동 등록한다. 도메인을 추가할 때
이 파일을 고치지 않는다. React 빌드 결과가 있으면 / 에서 함께 서빙한다.
"""
import importlib
import pkgutil
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.core.config import get_settings
from app.core.errors import register_error_handlers

settings = get_settings()


def _configure_logging() -> None:
    logger.remove()
    # WARNING: 콘솔 없는 환경에서는 stderr 가 None 이 될 수 있다.
    if sys.stderr is not None:
        logger.add(sys.stderr, level=settings.log_level, backtrace=False, diagnose=False)


def _register_domain_routers(app: FastAPI) -> None:
    import app.domain as domain_pkg

    for module in pkgutil.iter_modules(domain_pkg.__path__):
        if not module.ispkg:
            continue
        name = module.name
        try:
            api = importlib.import_module(f"app.domain.{name}.api")
        except ModuleNotFoundError:
            logger.warning("domain {} has no api module", name)
            continue
        router: APIRouter | None = getattr(api, "router", None)
        if router is None:
            logger.warning("domain {} api has no router", name)
            continue
        app.include_router(router, prefix=f"/api/{name}")
        logger.info("mounted /api/{}", name)


@asynccontextmanager
async def lifespan(_: FastAPI):
    _configure_logging()
    logger.info("gait-insight api starting. data_dir={}", settings.data_dir)
    logger.info("local network demo only. do not expose this server to the internet.")
    yield
    from app.core.db import engine

    await engine.dispose()


app = FastAPI(
    title="gait-insight API",
    version="0.1.0",
    description="공개 보행 기록 분석 프로토타입. 로컬망 시연 전용입니다.",
    lifespan=lifespan,
)

if settings.cors_origin_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

register_error_handlers(app)
_register_domain_routers(app)


@app.get("/api/health", tags=["meta"], summary="상태 확인")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def _mount_static(application: FastAPI) -> None:
    static_dir: Path = settings.static_dir
    index = static_dir / "index.html"
    if not index.is_file():
        logger.info("static build not found at {}; serving api only", static_dir)
        return
    application.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @application.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str) -> FileResponse:
        candidate = static_dir / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(index)


_mount_static(app)
