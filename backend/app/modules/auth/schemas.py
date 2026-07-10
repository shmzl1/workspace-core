"""Authentication request and response schemas."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


class AuthUserRead(BaseModel):
    id: int
    username: str
    role: str
    permissions: list[str] = Field(default_factory=list)
    employee_id: int | None = None
    full_name: str | None = None
    department: str | None = None
    job_title: str | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AuthUserRead
