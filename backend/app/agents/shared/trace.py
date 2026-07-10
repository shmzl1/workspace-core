"""Trace redaction declarations for Agent event summaries."""

from typing import Any, Protocol

FORBIDDEN_TRACE_FIELDS = (
    "api_key",
    "jwt",
    "password",
    "database_connection_string",
    "full_resume",
    "full_phone_number",
    "full_email_address",
    "full_salary_details",
)


class TraceRedactionPolicy(Protocol):
    def redact(self, payload: dict[str, Any]) -> dict[str, Any]: ...

