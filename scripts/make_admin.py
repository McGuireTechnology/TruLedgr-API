#!/usr/bin/env python3
"""
Script to make a user an admin.
Usage: python make_admin.py <username>
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


def make_admin(username: str):
    """Make a user an admin."""
    with Session(engine) as session:
        # Find user
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()
        
        if not user:
            print(f"❌ User '{username}' not found")
            return False
        
        if user.is_admin:
            print(f"✅ User '{username}' is already an admin")
            return True
        
        # Make admin
        user.is_admin = True
        session.commit()
        print(f"✅ User '{username}' is now an admin")
        return True


def list_admins():
    """List all admin users."""
    with Session(engine) as session:
        statement = select(User).where(User.is_admin == True)
        admins = session.exec(statement).all()
        
        if not admins:
            print("No admin users found")
        else:
            print("Admin users:")
            for admin in admins:
                print(f"  • {admin.username} ({admin.email})")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python make_admin.py <username>")
        print("       python make_admin.py --list")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        list_admins()
    else:
        username = sys.argv[1]
        make_admin(username)
