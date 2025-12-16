"""Pytest fixtures for NexusLEO backend."""
from __future__ import annotations

import os
from typing import Iterator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.db import get_db
from app.main import app

DATABASE_URL = os.getenv("DATABASE_URL_TEST") or os.getenv(
    "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/nexusleo"
)

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def _apply_migrations() -> None:
    """Apply alembic migrations to the test database.

    Tests assume schema exists. We run migrations once per test session.
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    alembic_ini = os.path.join(repo_root, "alembic.ini")
    script_location = os.path.join(repo_root, "alembic")

    cfg = Config(alembic_ini)
    cfg.set_main_option("script_location", script_location)
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(cfg, "head")


@pytest.fixture
def db_session(_apply_migrations) -> Iterator[Session]:
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def db_session_factory(db_session: Session) -> Iterator[Session]:
    created_sessions: list[Session] = []

    def _factory() -> Session:
        session = TestingSessionLocal(bind=db_session.connection())
        created_sessions.append(session)
        return session

    yield _factory

    for session in created_sessions:
        session.close()


@pytest.fixture
def fresh_session(db_session_factory):
    session = db_session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
