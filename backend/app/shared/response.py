"""Shared API response envelopes.

This module only defines cross-module response shapes. Business services remain
responsible for their own data contracts.
"""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    error: ErrorDetail | None = None
    trace_id: str | None = Field(default=None, description="Request trace id")


def ok(data: T | None = None, trace_id: str | None = None) -> ApiResponse[T]:
    return ApiResponse(data=data, trace_id=trace_id)


def fail(code: str, message: str, trace_id: str | None = None) -> ApiResponse[None]:
    return ApiResponse(success=False, error=ErrorDetail(code=code, message=message), trace_id=trace_id)
