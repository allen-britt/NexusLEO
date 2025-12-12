"""Pytest fixtures for NexusLEO backend."""
from __future__ import annotations

import os
from typing import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.db import get_db
from app.main import app

DATABASE_URL = os.getenv("DATABASE_URL_TEST") or os.getenv(
    "DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/nexusleo"
)

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@pytest.fixture
def db_session() -> Iterator[Session]:
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
