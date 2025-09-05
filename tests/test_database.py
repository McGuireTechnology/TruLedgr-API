"""Test database configuration (async-first)."""

import pytest
from truledgr_api.config import Settings


def test_async_sqlite_database_url():
    """Test async SQLite database URL (preferred)."""
    settings = Settings(database_url="sqlite+aiosqlite:///./test.db")
    assert settings.database_url == "sqlite+aiosqlite:///./test.db"
    assert settings.sync_database_url == "sqlite:///./test.db"


def test_async_postgresql_database_url():
    """Test async PostgreSQL database URL (preferred)."""
    postgres_url = "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb"
    settings = Settings(database_url=postgres_url)
    
    assert settings.database_url == postgres_url
    assert settings.sync_database_url == "postgresql://testuser:testpass@localhost:5432/testdb"


def test_async_mysql_database_url():
    """Test async MySQL database URL."""
    mysql_url = "mysql+aiomysql://testuser:testpass@localhost:3306/testdb"
    settings = Settings(database_url=mysql_url)
    
    assert settings.database_url == mysql_url
    assert settings.sync_database_url == "mysql://testuser:testpass@localhost:3306/testdb"


def test_sync_sqlite_auto_converted():
    """Test that sync SQLite URLs are automatically converted to async."""
    settings = Settings(database_url="sqlite:///./test.db")
    assert settings.database_url == "sqlite+aiosqlite:///./test.db"
    assert settings.sync_database_url == "sqlite:///./test.db"


def test_sync_postgresql_auto_converted():
    """Test that sync PostgreSQL URLs are automatically converted to async."""
    sync_url = "postgresql://testuser:testpass@localhost:5432/testdb"
    settings = Settings(database_url=sync_url)
    
    assert settings.database_url == "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb"
    assert settings.sync_database_url == sync_url


def test_sync_mysql_auto_converted():
    """Test that sync MySQL URLs are automatically converted to async."""
    sync_url = "mysql://testuser:testpass@localhost:3306/testdb"
    settings = Settings(database_url=sync_url)
    
    assert settings.database_url == "mysql+aiomysql://testuser:testpass@localhost:3306/testdb"
    assert settings.sync_database_url == sync_url


def test_missing_database_url():
    """Test error when DATABASE_URL is not provided."""
    # This should raise a validation error
    with pytest.raises(ValueError, match="DATABASE_URL is required"):
        Settings(database_url="")


def test_missing_database_url_none():
    """Test error when DATABASE_URL is None."""
    with pytest.raises((ValueError, TypeError)):
        Settings(database_url=None)
