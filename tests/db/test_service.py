"""Tests for db.service.DatabaseService error handling."""

import pytest

from db.service import DatabaseService


def test_database_service_raises_clear_error_when_db_url_missing():
    with pytest.raises(ValueError, match="DB_URL is not set"):
        DatabaseService(db_url=None)

    with pytest.raises(ValueError, match="DB_URL is not set"):
        DatabaseService(db_url="")


def test_database_service_raises_clear_error_for_invalid_db_url():
    with pytest.raises(ValueError, match="Invalid DB_URL"):
        DatabaseService(db_url="not-a-valid-url")


def test_database_service_accepts_valid_db_url():
    service = DatabaseService(db_url="postgresql+psycopg2://user:pass@localhost/db")
    assert service.engine is not None
