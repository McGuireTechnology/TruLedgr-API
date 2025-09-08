# User Impersonation Feature

The TruLedgr API now supports secure user impersonation functionality that allows admin users to temporarily act on behalf of other users. This is useful for customer support, debugging, and administrative tasks.

## Overview

User impersonation allows admin users to:
- Temporarily access the system as another user
- Perform actions on behalf of that user
- Maintain a full audit trail of impersonation activities
- Have time-limited impersonation sessions (2 hours max)

## Security Features

- **Admin-only access**: Only users with `is_admin = true` can start impersonation
- **Session tracking**: All impersonation sessions are logged with timestamps, reasons, and participants
- **Time limits**: Impersonation sessions automatically expire after 2 hours
- **Self-protection**: Admins cannot impersonate themselves
- **Token isolation**: Impersonation uses separate tokens that don't affect regular user sessions
- **Audit trail**: Complete logging of who impersonated whom, when, and why

## Database Schema

### Users Table
```sql
ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;
```

### Impersonation Sessions Table
```sql
CREATE TABLE impersonation_sessions (
    id VARCHAR PRIMARY KEY,
    admin_user_id VARCHAR NOT NULL REFERENCES users(id),
    target_user_id VARCHAR NOT NULL REFERENCES users(id),
    session_token VARCHAR UNIQUE NOT NULL,
    reason VARCHAR,
    expires_at DATETIME NOT NULL,
    ended_at DATETIME,
    status VARCHAR(7) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

## API Endpoints

### 1. Start Impersonation
**POST `/auth/impersonations`**

Start impersonating another user (admin only).

**Request:**
```json
{
    "target_user_id": "01K4EJAT33FQE5GSSXJNCQ090R",
    "reason": "Customer support request - troubleshooting account issue"
}
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "target_user_id": "01K4EJAT33FQE5GSSXJNCQ090R",
    "admin_user_id": "01K4EJASXVVJKMP6K8Q3GQZKGJ",
    "impersonation_session_id": "01K4EJD6NQ1E2PVX1RWZTE7YX8"
}
```

### 2. Check Current User (with impersonation status)
**GET `/auth/whoami`**

Get current user information including impersonation status.

**Response (when impersonating):**
```json
{
    "user_id": "01K4EJAT33FQE5GSSXJNCQ090R",
    "username": "testuser",
    "email": "test@truledgr.com",
    "is_admin": false,
    "is_impersonating": true,
    "impersonation": {
        "admin_user_id": "01K4EJASXVVJKMP6K8Q3GQZKGJ",
        "admin_username": "admin",
        "session_id": "01K4EJD6NQ1E2PVX1RWZTE7YX8",
        "reason": "Customer support request"
    }
}
```

**Response (normal user):**
```json
{
    "user_id": "01K4EJASXVVJKMP6K8Q3GQZKGJ",
    "username": "admin",
    "email": "admin@truledgr.com",
    "is_admin": true,
    "is_impersonating": false
}
```

### 3. End Impersonation
**DELETE `/auth/impersonations`**

End an active impersonation session (admin only).

**Request:**
```json
{
    "impersonation_session_id": "01K4EJD6NQ1E2PVX1RWZTE7YX8"
}
```

**Response:**
```json
{
    "message": "Impersonation session ended successfully"
}
```

### 4. List Impersonation Sessions
**GET `/auth/impersonations`**

Get all impersonation sessions for the current admin user.

**Response:**
```json
[
    {
        "id": "01K4EJD6NQ1E2PVX1RWZTE7YX8",
        "admin_user_id": "01K4EJASXVVJKMP6K8Q3GQZKGJ",
        "admin_username": "admin",
        "target_user_id": "01K4EJAT33FQE5GSSXJNCQ090R",
        "target_username": "testuser",
        "reason": "Customer support request",
        "created_at": "2025-09-06T03:51:33.303503",
        "expires_at": "2025-09-06T05:51:33.303468",
        "ended_at": "2025-09-06T03:51:33.317035",
        "status": "revoked"
    }
]
```

## Setup Instructions

### 1. Run Database Migration
```bash
cd /path/to/truledgr-api
source .venv/bin/activate
python migrations/add_impersonation.py
```

### 2. Create Admin Users
```bash
# Make an existing user an admin
python scripts/make_admin.py username

# List all admin users
python scripts/make_admin.py --list
```

### 3. Test the Feature
```bash
# Run the comprehensive test suite
python tests/test_impersonation.py
```

## Usage Examples

### Frontend Implementation

```javascript
// Start impersonation
const startImpersonation = async (targetUserId, reason) => {
    const response = await fetch('/auth/impersonations', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${adminToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            target_user_id: targetUserId,
            reason: reason
        })
    });
    
    const data = await response.json();
    
    // Store impersonation token
    localStorage.setItem('impersonation_token', data.access_token);
    localStorage.setItem('impersonation_session_id', data.impersonation_session_id);
    
    return data;
};

// Check if currently impersonating
const checkImpersonationStatus = async (token) => {
    const response = await fetch('/auth/whoami', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    return data.is_impersonating;
};

// End impersonation
const endImpersonation = async (sessionId) => {
    const response = await fetch('/auth/impersonations', {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${adminToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            impersonation_session_id: sessionId
        })
    });
    
    // Clear impersonation tokens
    localStorage.removeItem('impersonation_token');
    localStorage.removeItem('impersonation_session_id');
    
    return response.json();
};
```

### Python Client Example

```python
import requests

class TruLedgrClient:
    def __init__(self, base_url, admin_token):
        self.base_url = base_url
        self.admin_token = admin_token
        self.impersonation_token = None
        self.session_id = None
    
    def start_impersonation(self, target_user_id, reason):
        """Start impersonating a user."""
        response = requests.post(
            f"{self.base_url}/auth/impersonations",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={
                "target_user_id": target_user_id,
                "reason": reason
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.impersonation_token = data["access_token"]
            self.session_id = data["impersonation_session_id"]
            return data
        else:
            raise Exception(f"Impersonation failed: {response.text}")
    
    def end_impersonation(self):
        """End current impersonation session."""
        if not self.session_id:
            return
            
        response = requests.delete(
            f"{self.base_url}/auth/impersonations",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"impersonation_session_id": self.session_id}
        )
        
        self.impersonation_token = None
        self.session_id = None
        return response.json()
    
    def get_current_user(self):
        """Get current user info (use impersonation token if active)."""
        token = self.impersonation_token or self.admin_token
        response = requests.get(
            f"{self.base_url}/auth/whoami",
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()

# Usage
client = TruLedgrClient("http://localhost:8000", admin_token)

# Start impersonation
client.start_impersonation("user123", "Customer support request")

# Check who we're acting as
user_info = client.get_current_user()
print(f"Acting as: {user_info['username']}")

# End impersonation
client.end_impersonation()
```

## Security Considerations

1. **Admin Verification**: Always verify admin status before allowing impersonation
2. **Audit Logging**: Log all impersonation activities for compliance
3. **Time Limits**: Enforce session expiration to minimize risk
4. **Reason Tracking**: Require and log reasons for impersonation
5. **Token Isolation**: Use separate tokens to avoid session contamination
6. **Permission Inheritance**: Impersonated users inherit target user permissions, not admin permissions

## Troubleshooting

### Common Issues

1. **"Admin privileges required"**
   - Ensure the user has `is_admin = true` in the database
   - Check that the correct admin token is being used

2. **"Impersonation session expired"**
   - Sessions expire after 2 hours
   - End the session and start a new one if needed

3. **"Cannot impersonate yourself"**
   - Admins cannot impersonate their own accounts
   - Use a different target user ID

4. **"Target user not found or inactive"**
   - Verify the target user exists and is active
   - Check the user ID is correct

### Debug Commands

```bash
# Check admin users
python scripts/make_admin.py --list

# Check impersonation sessions
python -c "
from truledgr_api.database import engine
from sqlmodel import Session, select
from truledgr_api.models.auth import ImpersonationSession

with Session(engine) as session:
    sessions = session.exec(select(ImpersonationSession)).all()
    for s in sessions:
        print(f'{s.admin_user_id} -> {s.target_user_id} ({s.status})')
"
```

## Files Modified

- `truledgr_api/models/user.py` - Added `is_admin` field
- `truledgr_api/models/auth.py` - Added impersonation models and schemas
- `truledgr_api/utils/auth.py` - Added impersonation utilities and dependencies
- `truledgr_api/routers/auth.py` - Added impersonation endpoints
- `migrations/add_impersonation.py` - Database migration script
- `scripts/make_admin.py` - Admin user management script
- `tests/test_impersonation.py` - Comprehensive test suite

This feature provides a secure, auditable way for administrators to temporarily act on behalf of users while maintaining full traceability and security controls.
