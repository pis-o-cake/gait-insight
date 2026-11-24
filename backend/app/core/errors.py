"""도메인 오류와 FastAPI 예외 핸들러.

오류 본문은 {code, message} 형태이며 message 는 locale 파일에서 조립한다.
code 는 화면이 분기에 쓰는 식별자이므로 영문 고정이다.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.locales import translate


class AppError(Exception):
    """사용자에게 코드와 문구로 전달하는 오류."""

    status_code = 400

    def __init__(self, code: str, **params: object) -> None:
        super().__init__(code)
        self.code = code
        self.params = params


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class UnauthorizedError(AppError):
    status_code = 401


class UnprocessableError(AppError):
    status_code = 422


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _handle(_: Request, exc: AppError) -> JSONResponse:
        logger.info("app error code={} params={}", exc.code, exc.params)
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.code, "message": translate(exc.code, **exc.params)},
        )
