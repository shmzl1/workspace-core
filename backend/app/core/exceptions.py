"""Exception types and response helpers."""

from fastapi import Request
from fastapi.responses import JSONResponse

from app.shared.response import fail
from app.shared.trace import get_trace_id


class TalentFlowError(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


async def talentflow_error_handler(request: Request, exc: TalentFlowError) -> JSONResponse:
    trace_id = get_trace_id() or request.headers.get("X-Trace-Id")
    return JSONResponse(status_code=400, content=fail(exc.code, exc.message, trace_id).model_dump())
