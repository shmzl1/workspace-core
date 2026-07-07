"""Database session and SQLAlchemy declarative base."""

from collections.abc import Iterator

from sqlalchemy import DateTime, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class TimestampMixin:
    """Common created/updated timestamps for business tables."""

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db_session() -> Iterator[Session]:
    """Yield a database session for repository dependencies."""

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
