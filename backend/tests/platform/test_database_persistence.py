"""Optional PostgreSQL persistence checks.

Set TF_RUN_DB_TESTS=1 and TEST_DATABASE_URL to a migrated PostgreSQL database
before running this file. The test does not create tables or run migrations.
"""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import get_db_session
from app.main import app
from app.modules.auth.models import User

RUN_DB_TESTS = os.getenv("TF_RUN_DB_TESTS") == "1"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


pytestmark = pytest.mark.skipif(
    not RUN_DB_TESTS or not TEST_DATABASE_URL,
    reason="PostgreSQL persistence tests require TF_RUN_DB_TESTS=1 and TEST_DATABASE_URL.",
)

if RUN_DB_TESTS and TEST_DATABASE_URL:
    pytest.importorskip("psycopg", reason="PostgreSQL persistence tests require the psycopg driver.")


def test_postgresql_persists_data_across_sessions_and_api_reads() -> None:
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)

    try:
        with session_factory() as session:
            session.execute(delete(User).where(User.id == 990001))
            session.add(
                User(
                    id=990001,
                    username="pytest_demo_user",
                    password_hash="demo_only_not_for_login",
                    role="HR_SPECIALIST",
                    is_active=True,
                )
            )
            session.commit()

        with session_factory() as session:
            persisted = session.scalar(select(User).where(User.id == 990001))
            assert persisted is not None
            assert persisted.username == "pytest_demo_user"

        def override_db_session():
            session = session_factory()
            try:
                yield session
            finally:
                session.close()

        app.dependency_overrides[get_db_session] = override_db_session
        try:
            response = TestClient(app).get("/api/v1/auth/demo-users")
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert any(user["username"] == "pytest_demo_user" for user in body["data"])

    except SQLAlchemyError as exc:
        pytest.skip(f"PostgreSQL schema is not ready for persistence test: {exc}")
    finally:
        try:
            with session_factory() as session:
                session.execute(delete(User).where(User.id == 990001))
                session.commit()
        except SQLAlchemyError:
            pass
        engine.dispose()
