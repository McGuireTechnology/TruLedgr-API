#!/usr/bin/env python3
"""
Test script for impersonation functionality.
Creates test users and demonstrates impersonation features.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import Session, select
from truledgr_api.database import engine
from truledgr_api.models.user import User
from truledgr_api.utils.auth import get_password_hash
from fastapi.testclient import TestClient
from truledgr_api.main import app


def create_test_users():
    """Create test users for impersonation testing."""
    print("👥 Creating test users...")
    
    with Session(engine) as session:
        # Check if users already exist
        existing_admin = session.exec(select(User).where(User.username == "admin")).first()
        existing_testuser = session.exec(select(User).where(User.username == "testuser")).first()
        existing_alice = session.exec(select(User).where(User.username == "alice")).first()
        
        users_to_create = []
        
        if not existing_admin:
            users_to_create.append(User(
                username="admin",
                email="admin@truledgr.com",
                full_name="Admin User",
                hashed_password=get_password_hash("admin123"),
                is_admin=True,
                is_active=True
            ))
        
        if not existing_testuser:
            users_to_create.append(User(
                username="testuser",
                email="test@truledgr.com", 
                full_name="Test User",
                hashed_password=get_password_hash("test123"),
                is_admin=False,
                is_active=True
            ))
        
        if not existing_alice:
            users_to_create.append(User(
                username="alice",
                email="alice@truledgr.com",
                full_name="Alice Smith", 
                hashed_password=get_password_hash("alice123"),
                is_admin=False,
                is_active=True
            ))
        
        if users_to_create:
            for user in users_to_create:
                session.add(user)
            session.commit()
            print(f"✅ Created {len(users_to_create)} new users")
        else:
            print("✅ All test users already exist")
        
        print("  • admin (admin@truledgr.com) - password: admin123 - Admin: ✅")
        print("  • testuser (test@truledgr.com) - password: test123 - Admin: ❌")
        print("  • alice (alice@truledgr.com) - password: alice123 - Admin: ❌")


def test_impersonation():
    """Test the impersonation functionality."""
    print("\n🧪 Testing impersonation functionality...")
    
    client = TestClient(app)
    
    # Step 1: Login as admin
    print("\n1️⃣ Logging in as admin...")
    login_response = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Admin login failed: {login_response.text}")
        return
    
    admin_token = login_response.json()["access_token"]
    print("✅ Admin login successful")
    
    # Step 2: Test whoami as admin
    print("\n2️⃣ Testing whoami as admin...")
    whoami_response = client.get("/auth/whoami", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    print(f"Admin whoami: {whoami_response.json()}")
    
    # Step 3: Start impersonation
    print("\n3️⃣ Starting impersonation of testuser...")
    # First get testuser ID
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == "testuser")).first()
        testuser_id = user.id if user else None
    
    if not testuser_id:
        print("❌ Test user not found")
        return
    
    impersonate_response = client.post("/auth/impersonations", 
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "target_user_id": testuser_id,
            "reason": "Testing impersonation functionality"
        }
    )
    
    if impersonate_response.status_code != 200:
        print(f"❌ Impersonation failed: {impersonate_response.text}")
        return
    
    impersonation_data = impersonate_response.json()
    impersonation_token = impersonation_data["access_token"]
    session_id = impersonation_data["impersonation_session_id"]
    print("✅ Impersonation started successfully")
    
    # Step 4: Test whoami while impersonating
    print("\n4️⃣ Testing whoami while impersonating...")
    whoami_impersonated = client.get("/auth/whoami", headers={
        "Authorization": f"Bearer {impersonation_token}"
    })
    print(f"Impersonated whoami: {whoami_impersonated.json()}")
    
    # Step 5: Test accessing user data while impersonating
    print("\n5️⃣ Testing user profile access while impersonating...")
    profile_response = client.get("/auth/me", headers={
        "Authorization": f"Bearer {impersonation_token}"
    })
    if profile_response.status_code == 200:
        profile_data = profile_response.json()
        print(f"✅ Can access profile as: {profile_data['username']}")
    else:
        print(f"❌ Profile access failed: {profile_response.text}")
    
    # Step 6: List impersonation sessions (as admin)
    print("\n6️⃣ Listing impersonation sessions...")
    sessions_response = client.get("/auth/impersonations", headers={
        "Authorization": f"Bearer {admin_token}"
    })
    if sessions_response.status_code == 200:
        sessions = sessions_response.json()
        print(f"✅ Found {len(sessions)} impersonation sessions")
        for session in sessions:
            print(f"  • {session['admin_username']} → {session['target_username']} ({session['status']})")
    
    # Step 7: End impersonation
    print("\n7️⃣ Ending impersonation...")
    end_response = client.request("DELETE", "/auth/impersonations",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"impersonation_session_id": session_id}
    )
    
    if end_response.status_code == 200:
        print("✅ Impersonation ended successfully")
    else:
        print(f"❌ Failed to end impersonation: {end_response.text}")
    
    # Step 8: Test that impersonation token no longer works
    print("\n8️⃣ Testing that impersonation token is revoked...")
    revoked_test = client.get("/auth/whoami", headers={
        "Authorization": f"Bearer {impersonation_token}"
    })
    if revoked_test.status_code == 401:
        print("✅ Impersonation token correctly revoked")
    else:
        print(f"❌ Impersonation token still valid: {revoked_test.status_code}")


if __name__ == "__main__":
    try:
        create_test_users()
        test_impersonation()
        print("\n🎉 Impersonation testing completed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
