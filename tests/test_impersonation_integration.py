#!/usr/bin/env python3
"""
Quick integration test for impersonation with other API endpoints.
Tests that impersonation works across all TruLedgr resources.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from truledgr_api.main import app


def test_impersonation_integration():
    """Test impersonation works with other API endpoints."""
    print("🔗 Testing impersonation integration with TruLedgr API...")
    
    client = TestClient(app)
    
    # 1. Login as admin
    admin_login = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    
    if admin_login.status_code != 200:
        print(f"❌ Admin login failed: {admin_login.text}")
        return
    
    admin_token = admin_login.json()["access_token"]
    print("✅ Admin logged in")
    
    # 2. Start impersonating testuser
    impersonate_response = client.post("/auth/impersonations",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "target_user_id": "01K4EJAT33FQE5GSSXJNCQ090R",  # testuser ID from earlier
            "reason": "Integration testing"
        }
    )
    
    if impersonate_response.status_code != 200:
        print(f"❌ Impersonation failed: {impersonate_response.text}")
        return
    
    impersonation_token = impersonate_response.json()["access_token"]
    session_id = impersonate_response.json()["impersonation_session_id"]
    print("✅ Started impersonating testuser")
    
    # 3. Test various endpoints while impersonating
    print("\n🧪 Testing API endpoints while impersonating:")
    
    # Test user profile
    profile_response = client.get("/auth/me", headers={
        "Authorization": f"Bearer {impersonation_token}"
    })
    if profile_response.status_code == 200:
        print("  ✅ /auth/me - Can access user profile")
    else:
        print(f"  ❌ /auth/me - Failed: {profile_response.status_code}")
    
    # Test users endpoint (if accessible)
    users_response = client.get("/users/", headers={
        "Authorization": f"Bearer {impersonation_token}"
    })
    print(f"  📊 /users/ - Status: {users_response.status_code}")
    
    # Test accounts endpoint (if accessible) 
    accounts_response = client.get("/accounts/", headers={
        "Authorization": f"Bearer {impersonation_token}"
    })
    print(f"  📊 /accounts/ - Status: {accounts_response.status_code}")
    
    # Test transactions endpoint (if accessible)
    transactions_response = client.get("/transactions/", headers={
        "Authorization": f"Bearer {impersonation_token}"
    })
    print(f"  📊 /transactions/ - Status: {transactions_response.status_code}")
    
    # 4. Verify whoami shows impersonation
    whoami_response = client.get("/auth/whoami", headers={
        "Authorization": f"Bearer {impersonation_token}"
    })
    
    if whoami_response.status_code == 200:
        whoami_data = whoami_response.json()
        if whoami_data.get("is_impersonating"):
            print(f"  ✅ /auth/whoami - Shows impersonation: {whoami_data['impersonation']['admin_username']} → {whoami_data['username']}")
        else:
            print("  ❌ /auth/whoami - Impersonation not detected")
    
    # 5. Test that admin endpoints are NOT accessible with impersonation token
    admin_test = client.get("/auth/impersonations", headers={
        "Authorization": f"Bearer {impersonation_token}"
    })
    
    if admin_test.status_code == 403:
        print("  ✅ Admin endpoints properly protected from impersonated users")
    else:
        print(f"  ⚠️ Admin endpoint accessible with impersonation token: {admin_test.status_code}")
    
    # 6. End impersonation
    end_response = client.request("DELETE", "/auth/impersonations",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"impersonation_session_id": session_id}
    )
    
    if end_response.status_code == 200:
        print("\n✅ Impersonation ended successfully")
    else:
        print(f"\n❌ Failed to end impersonation: {end_response.text}")
    
    # 7. Verify impersonation token no longer works
    final_test = client.get("/auth/whoami", headers={
        "Authorization": f"Bearer {impersonation_token}"
    })
    
    if final_test.status_code == 401:
        print("✅ Impersonation token correctly invalidated")
    else:
        print(f"❌ Impersonation token still valid: {final_test.status_code}")


if __name__ == "__main__":
    try:
        test_impersonation_integration()
        print("\n🎉 Integration testing completed!")
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
