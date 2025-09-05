"""Test ULID functionality."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from truledgr_api.main import create_app
from truledgr_api.database import get_db
from truledgr_api.models.user import User, UserCreate
from truledgr_api.apps.users import create_users_app
from ulid import ULID


def test_ulid_generation():
    """Test that ULID generation works correctly."""
    from truledgr_api.models import generate_ulid
    
    ulid1 = generate_ulid()
    ulid2 = generate_ulid()
    
    # ULIDs should be 26 characters long
    assert len(ulid1) == 26
    assert len(ulid2) == 26
    
    # ULIDs should be different
    assert ulid1 != ulid2
    
    # ULIDs should be alphanumeric
    assert ulid1.isalnum()
    assert ulid2.isalnum()
    
    print(f"Generated ULID 1: {ulid1}")
    print(f"Generated ULID 2: {ulid2}")


def test_user_creation_with_ulid():
    """Test that users are created with ULID primary keys."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        def get_session_override():
            yield session

        # Create a fresh app for testing with custom database dependency
        from fastapi import FastAPI
        from truledgr_api.config import settings
        from truledgr_api.routers import health
        
        app = FastAPI(title=settings.app_name, servers=[])
        
        # Include health router with dependency override
        app.dependency_overrides[get_db] = get_session_override
        app.include_router(health.router)
        
        # Mount users subapp with test database dependency
        users_app = create_users_app(db_dependency=get_session_override)
        app.mount("/users", users_app)
        
        client = TestClient(app)
        
        # Create a user
        response = client.post(
            "/users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "full_name": "Test User",
                "password": "testpassword"
            }
        )
        
        assert response.status_code == 201
        user_data = response.json()
        
        print(f"Created user with ID: {user_data['id']}")
        
        # Verify the ID is a ULID
        assert len(user_data['id']) == 26
        assert user_data['id'].isalnum()
        assert isinstance(user_data['id'], str)
        
        # Test getting user by ULID
        user_id = user_data['id']
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 200
        
        fetched_user = get_response.json()
        assert fetched_user['id'] == user_id
        assert fetched_user['username'] == "testuser"
        
        print(f"Successfully fetched user by ULID: {user_id}")


if __name__ == "__main__":
    print("Testing ULID generation...")
    test_ulid_generation()
    
    print("\nTesting user creation with ULID...")
    test_user_creation_with_ulid()
    
    print("\n✅ All ULID tests passed!")
