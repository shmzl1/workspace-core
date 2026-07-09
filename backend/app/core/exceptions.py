"""
模块说明：系统全局异常处理与 HTTP 错误响应拦截器
对应路径：workspace-core-dev/backend/app/core/exceptions.py
"""

# pyrefly: ignore [missing-import]
from fastapi import Request
# pyrefly: ignore [missing-import]
from fastapi.exceptions import RequestValidationError
# pyrefly: ignore [missing-import]
from fastapi.responses import JSONResponse
# pyrefly: ignore [missing-import]
from starlette.exceptions import HTTPException as StarletteHTTPException

# 跨模块引用共享响应格式与链路追踪工具
from app.shared.response import fail
from app.shared.trace import get_trace_id


class TalentFlowError(Exception):

    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def talentflow_error_handler(request: Request, exc: TalentFlowError) -> JSONResponse:

    trace_id = get_trace_id() or request.headers.get("X-Trace-Id") or request.headers.get("X-Trace-ID", "")
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(
            code=exc.code,
            message=exc.message,
            trace_id=trace_id
        ).model_dump()
    )


async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:

    trace_id = get_trace_id() or request.headers.get("X-Trace-Id") or request.headers.get("X-Trace-ID", "")
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(
            code="HTTP_ERROR",
            message=str(exc.detail),
            trace_id=trace_id
        ).model_dump()
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:

    trace_id = get_trace_id() or request.headers.get("X-Trace-Id") or request.headers.get("X-Trace-ID", "")
    error_details = exc.errors()
    first_error_msg = error_details[0].get("msg", "请求参数格式错误") if error_details else "校验失败"
    
    return JSONResponse(
        status_code=422,
        content=fail(
            code="PARAM_VALIDATION_ERROR",
            message=f"参数校验失败: {first_error_msg}",
            trace_id=trace_id
        ).model_dump()
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:

    trace_id = get_trace_id() or request.headers.get("X-Trace-Id") or request.headers.get("X-Trace-ID", "")
    return JSONResponse(
        status_code=500,
        content=fail(
            code="INTERNAL_ERROR",
            message="服务端处理失败，请联系管理员并提供 trace_id",
            trace_id=trace_id
        ).model_dump()
    )

