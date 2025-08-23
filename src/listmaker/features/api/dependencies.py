"""Shared dependencies for API endpoints."""

from typing import Generator

from sqlalchemy.orm import Session

from ...database.connection import get_db as get_database_session


def get_db() -> Generator[Session, None, None]:
    """Get database session dependency."""
    yield from get_database_session()
