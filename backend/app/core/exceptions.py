"""Exception types and response helpers."""

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.shared.response import fail
from app.shared.trace import get_trace_id


class TalentFlowError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def talentflow_error_handler(request: Request, exc: TalentFlowError) -> JSONResponse:
    trace_id = get_trace_id() or request.headers.get("X-Trace-Id")
    return JSONResponse(status_code=exc.status_code, content=fail(exc.code, exc.message, trace_id).model_dump())


async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    trace_id = get_trace_id() or request.headers.get("X-Trace-Id")
    return JSONResponse(
        status_code=exc.status_code,
        content=fail("HTTP_ERROR", str(exc.detail), trace_id).model_dump(),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    trace_id = get_trace_id() or request.headers.get("X-Trace-Id")
    return JSONResponse(
        status_code=422,
        content=fail("VALIDATION_ERROR", "请求参数不符合接口契约", trace_id).model_dump(),
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    trace_id = get_trace_id() or request.headers.get("X-Trace-Id")
    return JSONResponse(
        status_code=500,
        content=fail("INTERNAL_ERROR", "服务端处理失败，请联系管理员并提供 trace_id", trace_id).model_dump(),
    )
