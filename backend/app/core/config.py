"""Application configuration skeleton."""

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_name: str = "TalentFlow"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = ""
    postgres_host: str = "localhost"
    postgres_port: int = 5433
    postgres_user: str = "talentflow"
    postgres_password: str = "talentflow_dev_password_change_me"
    postgres_db: str = "talentflow"
    jwt_secret_key: str = Field(default="replace_with_a_local_random_secret")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120
    cors_origins: str = "http://localhost:5173"
    llm_enabled: bool = False
    llm_provider: str = "openai_compatible"
    llm_timeout_seconds: float = Field(default=30, gt=0)
    llm_max_retries: int = Field(default=2, ge=0)
    llm_temperature: float = Field(default=0.2, ge=0, le=2)
    agent_strategy_model_timeout_seconds: float = Field(default=25, gt=0)
    agent_strategy_max_completion_tokens: int = Field(default=512, gt=0)
    agent_report_model_timeout_seconds: float = Field(default=35, gt=0)
    agent_report_max_completion_tokens: int = Field(default=768, gt=0)
    llm_proxy_url: SecretStr = Field(default_factory=lambda: SecretStr(""))
    llm_trust_env: bool = True
    openai_base_url: str = ""
    openai_api_key: SecretStr = Field(default_factory=lambda: SecretStr(""))
    openai_model: str = ""
    rag_enabled: bool = False
    rag_auto_initialize: bool = False
    chroma_persist_dir: str = "../data/runtime/chroma"
    chroma_collection_name: str = "talentflow_policies"
    embedding_provider: str = "openai_compatible"
    embedding_base_url: str = ""
    embedding_api_key: SecretStr = Field(default_factory=lambda: SecretStr(""))
    embedding_model: str = ""
    embedding_batch_size: int = Field(default=32, gt=0, le=256)
    rag_top_k: int = Field(default=6, gt=0)
    rag_score_threshold: float = Field(default=0.2, ge=0, le=1)
    rag_chunk_size: int = Field(default=800, gt=0)
    rag_chunk_overlap: int = Field(default=120, ge=0)
    policy_data_dir: str = "../data/policies"
    upload_dir: str = "../data/runtime/uploads"
    report_dir: str = "../data/runtime/reports"

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        """Use DATABASE_URL when set, otherwise build it from POSTGRES_* values."""

        if not self.database_url:
            self.database_url = (
                f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        if self.rag_chunk_overlap >= self.rag_chunk_size:
            raise ValueError("RAG_CHUNK_OVERLAP 必须小于 RAG_CHUNK_SIZE")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def llm_configured(self) -> bool:
        return bool(
            self.llm_enabled
            and self.llm_provider.strip().casefold() == "openai_compatible"
            and self.openai_base_url.strip()
            and self.openai_api_key.get_secret_value().strip()
            and self.openai_model.strip()
        )

    @property
    def rag_configured(self) -> bool:
        return bool(
            self.rag_enabled
            and self.chroma_persist_dir.strip()
            and self.policy_data_dir.strip()
            and self.embedding_provider.strip().casefold()
            in {"openai_compatible", "volcengine_multimodal"}
            and self.effective_embedding_base_url
            and self.effective_embedding_api_key.get_secret_value().strip()
            and self.embedding_model.strip()
        )

    @property
    def effective_embedding_base_url(self) -> str:
        return self.embedding_base_url.strip() or self.openai_base_url.strip()

    @property
    def effective_embedding_api_key(self) -> SecretStr:
        if self.embedding_api_key.get_secret_value().strip():
            return self.embedding_api_key
        return self.openai_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
