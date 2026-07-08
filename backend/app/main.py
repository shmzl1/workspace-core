"""FastAPI application entry point for TalentFlow."""

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.dependencies import trace_context
from app.core.exceptions import (
    TalentFlowError,
    http_error_handler,
    talentflow_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from app.core.logging_config import configure_logging
from app.shared.constants import API_V1_PREFIX
from app.shared.response import ok
from app.shared.trace import TRACE_ID_HEADER, get_trace_id, set_trace_id

configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_exception_handler(TalentFlowError, talentflow_error_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def trace_id_middleware(request: Request, call_next):
    trace_id = set_trace_id(request.headers.get(TRACE_ID_HEADER))
    response = await call_next(request)
    response.headers[TRACE_ID_HEADER] = get_trace_id() or trace_id
    return response


@app.get("/health", dependencies=[Depends(trace_context)])
def health() -> object:
    return ok({"status": "ok"})


app.include_router(api_router, prefix=API_V1_PREFIX, dependencies=[Depends(trace_context)])
