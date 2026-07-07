"""FastAPI application entry point for TalentFlow."""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.dependencies import trace_context
from app.core.exceptions import TalentFlowError, talentflow_error_handler
from app.core.logging_config import configure_logging
from app.shared.constants import API_V1_PREFIX
from app.shared.response import ok

configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_exception_handler(TalentFlowError, talentflow_error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", dependencies=[Depends(trace_context)])
def health() -> object:
    return ok({"status": "ok"})


app.include_router(api_router, prefix=API_V1_PREFIX, dependencies=[Depends(trace_context)])
