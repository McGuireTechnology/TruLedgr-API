# Database Migration Workflow

This project uses Alembic for database migrations. We've transitioned from automatic table creation to proper version-controlled migrations.

## Quick Commands

```bash
# Create a new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Downgrade one migration
alembic downgrade -1

# Check current migration status
alembic current

# View migration history
alembic history --verbose
```

## Initial Setup (Already Done)

The project has been initialized with:

1. **Initial Migration**: `7c9f232a6d59_initial_migration_with_user_model.py`
   - Creates the `users` table with all fields
   - Adds unique indexes for `username` and `email`

2. **Database Created**: `truledgr_dev.db` with:
   - `users` table
   - `alembic_version` tracking table

## Workflow for Adding New Models

1. **Create the model** in `truledgr_api/models/`
2. **Export it** in `truledgr_api/models/__init__.py`
3. **Generate migration**:
   ```bash
   alembic revision --autogenerate -m "Add ModelName table"
   ```
4. **Review the migration** file in `alembic/versions/`
5. **Apply the migration**:
   ```bash
   alembic upgrade head
   ```

## Example: Adding a new model

```python
# truledgr_api/models/transaction.py
from sqlmodel import SQLModel, Field
from typing import Optional
from decimal import Decimal
from .base import BaseModel

class Transaction(BaseModel, table=True):
    __tablename__ = "transactions"
    
    amount: Decimal = Field(decimal_places=2)
    description: Optional[str] = None
    user_id: int = Field(foreign_key="users.id")
```

```python
# truledgr_api/models/__init__.py
# Add to imports and __all__
from .transaction import Transaction
__all__ = ["BaseModel", "TimestampMixin", "User", "Transaction"]
```

```bash
# Generate and apply migration
alembic revision --autogenerate -m "Add Transaction model"
alembic upgrade head
```

## Environment-specific Migrations

- **Development**: Uses SQLite (`sqlite+aiosqlite:///./truledgr_dev.db`)
- **Production**: Uses PostgreSQL (`postgresql+asyncpg://...`)
- **Testing**: Uses in-memory or separate test database

## VS Code Tasks

The following tasks are available in VS Code:

- **Alembic: Generate Migration** - Creates new migration with autogenerate
- **Alembic: Upgrade Database** - Applies all pending migrations
- **Alembic: Downgrade Database** - Rolls back one migration
- **Alembic: Check Status** - Shows current migration status

## Best Practices

1. **Always review** generated migrations before applying
2. **Test migrations** on a copy of production data
3. **Backup database** before major migrations in production
4. **Keep migrations small** and focused
5. **Use descriptive messages** for migration names
6. **Don't edit** applied migrations - create new ones for fixes

## Troubleshooting

### Migration not detecting model changes
- Ensure model is imported in `truledgr_api/models/__init__.py`
- Check that the model inherits from appropriate base class
- Verify the model has `table=True` parameter

### SQLModel import errors in migrations
- Alembic automatically adds `import sqlmodel.sql.sqltypes`
- This is normal for SQLModel string fields

### Database out of sync
```bash
# Reset to specific migration
alembic downgrade <revision_id>
alembic upgrade head

# Or start fresh (development only!)
rm truledgr_dev.db
alembic upgrade head
```
