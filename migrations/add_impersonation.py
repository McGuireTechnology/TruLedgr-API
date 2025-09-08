#!/usr/bin/env python3
"""
Migration script to add impersonation functionality.

This adds:
1. is_admin column to users table
2. impersonation_sessions table
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlmodel import SQLModel, text
from truledgr_api.database import engine, create_db_and_tables_sync
from truledgr_api.models.auth import ImpersonationSession
from truledgr_api.models.user import User


def run_migration():
    """Run the migration to add impersonation features."""
    print("🔄 Starting impersonation migration...")
    
    try:
        # Create connection
        with engine.connect() as conn:
            # Check if is_admin column already exists
            try:
                result = conn.execute(text("SELECT is_admin FROM users LIMIT 1"))
                print("✅ is_admin column already exists")
            except Exception:
                print("📝 Adding is_admin column to users table...")
                conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
                conn.commit()
                print("✅ is_admin column added")
            
            # Check if impersonation_sessions table exists
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM impersonation_sessions"))
                print("✅ impersonation_sessions table already exists")
            except Exception:
                print("📝 Creating impersonation_sessions table...")
                # Create all tables (will only create missing ones)
                SQLModel.metadata.create_all(engine)
                print("✅ impersonation_sessions table created")
        
        print("✅ Migration completed successfully!")
        print()
        print("🔧 Next steps:")
        print("1. Restart your application")
        print("2. Make at least one user an admin:")
        print("   UPDATE users SET is_admin = TRUE WHERE username = 'your_admin_username';")
        print("3. Test impersonation endpoints:")
        print("   POST /auth/impersonate")
        print("   GET /auth/whoami")
        print("   POST /auth/impersonate/end")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_migration()
