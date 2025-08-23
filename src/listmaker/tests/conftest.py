"""Test configuration and fixtures."""

from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..database.models import Base


@pytest.fixture(scope="session")
def test_engine():
    """Create a test database engine."""
    # Use in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def test_session(test_engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def sample_faction_data():
    """Sample faction data for testing."""
    return {
        "faction_id": "SM",
        "name": "Space Marines",
        "link": "https://wahapedia.ru/wh40k10ed/factions/space-marines",
    }


@pytest.fixture
def sample_datasheet_data():
    """Sample datasheet data for testing."""
    return {
        "datasheet_id": "000000001",
        "name": "Space Marine Captain",
        "faction_id": "SM",
        "role": "HQ",
        "base_cost": 85,
        "is_legend": False,
        "keywords": ["INFANTRY", "CHARACTER", "CAPTAIN"],
    }
