"""Test database configuration and models."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from truledgr_api.main import create_app
from truledgr_api.database import get_db
from truledgr_api.models.user import User, UserCreate
from truledgr_api.apps.users import create_users_app


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    # Only create the User table for these tests
    User.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with test database."""
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
    yield client
    app.dependency_overrides.clear()


def test_create_user(client: TestClient):
    """Test creating a user."""
    response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "testpassword"
        }
    )
    data = response.json()
    assert response.status_code == 201
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "hashed_password" not in data  # Should not be in response


def test_signup_user(client: TestClient):
    """Test user signup endpoint."""
    response = client.post(
        "/users/signup",
        json={
            "username": "signupuser",
            "email": "signup@example.com",
            "full_name": "Signup User",
            "password": "signuppassword"
        }
    )
    data = response.json()
    assert response.status_code == 201
    assert data["username"] == "signupuser"
    assert data["email"] == "signup@example.com"
    assert data["full_name"] == "Signup User"
    assert "id" in data
    assert "hashed_password" not in data  # Should not be in response


def test_read_users(client: TestClient):
    """Test reading users."""
    # Create a user first
    client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    response = client.get("/users/")
    data = response.json()
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["username"] == "testuser"


def test_read_user_by_id(client: TestClient):
    """Test reading a user by ID."""
    # Create a user first
    create_response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    user_id = create_response.json()["id"]
    
    response = client.get(f"/users/{user_id}")
    data = response.json()
    assert response.status_code == 200
    assert data["username"] == "testuser"
    assert data["id"] == user_id


def test_update_user(client: TestClient):
    """Test updating a user."""
    # Create a user first
    create_response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    user_id = create_response.json()["id"]
    
    # Update the user
    response = client.put(
        f"/users/{user_id}",
        json={"full_name": "Updated Name"}
    )
    data = response.json()
    assert response.status_code == 200
    assert data["full_name"] == "Updated Name"
    assert data["username"] == "testuser"  # Should remain unchanged


def test_delete_user(client: TestClient):
    """Test deleting a user."""
    # Create a user first
    create_response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    user_id = create_response.json()["id"]
    
    # Delete the user
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204
    
    # Verify user is deleted
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 404


def test_create_duplicate_username(client: TestClient):
    """Test creating a user with duplicate username."""
    # Create first user
    client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test1@example.com",
            "password": "testpassword"
        }
    )
    
    # Try to create second user with same username
    response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_create_duplicate_email(client: TestClient):
    """Test creating a user with duplicate email."""
    # Create first user
    client.post(
        "/users/",
        json={
            "username": "testuser1",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    # Try to create second user with same email
    response = client.post(
        "/users/",
        json={
            "username": "testuser2",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_signup_duplicate_username(client: TestClient):
    """Test signup with duplicate username."""
    # Create first user via signup
    client.post(
        "/users/signup",
        json={
            "username": "signupuser",
            "email": "signup1@example.com",
            "password": "signuppassword"
        }
    )
    
    # Try to signup second user with same username
    response = client.post(
        "/users/signup",
        json={
            "username": "signupuser",
            "email": "signup2@example.com",
            "password": "signuppassword"
        }
    )
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_signup_duplicate_email(client: TestClient):
    """Test signup with duplicate email."""
    # Create first user via signup
    client.post(
        "/users/signup",
        json={
            "username": "signupuser1",
            "email": "signup@example.com",
            "password": "signuppassword"
        }
    )
    
    # Try to signup second user with same email
    response = client.post(
        "/users/signup",
        json={
            "username": "signupuser2",
            "email": "signup@example.com",
            "password": "signuppassword"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]
