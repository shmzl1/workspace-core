"""Application configuration skeleton."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_name: str = "TalentFlow"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "postgresql+psycopg://talentflow:talentflow_dev_password_change_me@localhost:5432/talentflow"
    jwt_secret_key: str = Field(default="replace_with_a_local_random_secret")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120
    cors_origins: str = "http://localhost:5173"
    llm_enabled: bool = False
    openai_base_url: str = ""
    openai_api_key: str = ""
    openai_model: str = ""
    chroma_persist_dir: str = "../data/runtime/chroma"
    policy_data_dir: str = "../data/policies"
    upload_dir: str = "../data/runtime/uploads"
    report_dir: str = "../data/runtime/reports"

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
