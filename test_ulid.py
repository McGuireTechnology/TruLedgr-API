#!/usr/bin/env python3
"""Test script to verify ULID functionality."""

import httpx
import json

def test_ulid_api():
    """Test that the API uses ULIDs for primary keys."""
    base_url = "http://127.0.0.1:8000"
    
    # Create a user
    user_data = {
        "username": "testuser_ulid",
        "email": "testulid@example.com",
        "full_name": "Test ULID User",
        "password": "testpassword"
    }
    
    print("Creating user...")
    response = httpx.post(f"{base_url}/users/", json=user_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        user = response.json()
        print(f"Created user with ID: {user['id']}")
        print(f"ID length: {len(user['id'])}")
        print(f"ID type: {type(user['id'])}")
        
        # Verify it's a valid ULID format (26 characters, alphanumeric)
        if len(user['id']) == 26 and user['id'].isalnum():
            print("✅ ID appears to be a valid ULID!")
        else:
            print("❌ ID does not appear to be a valid ULID")
        
        # Test getting the user by ULID
        print(f"\nFetching user by ID: {user['id']}")
        get_response = httpx.get(f"{base_url}/users/{user['id']}")
        print(f"Get status: {get_response.status_code}")
        
        if get_response.status_code == 200:
            fetched_user = get_response.json()
            print(f"Fetched user: {fetched_user['username']}")
            print("✅ ULID lookup works!")
        else:
            print("❌ Failed to fetch user by ULID")
            
    else:
        print(f"Failed to create user: {response.text}")

if __name__ == "__main__":
    try:
        test_ulid_api()
    except Exception as e:
        print(f"Error: {e}")
