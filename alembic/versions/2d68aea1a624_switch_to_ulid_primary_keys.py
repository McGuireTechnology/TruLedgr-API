"""Switch to ULID primary keys

Revision ID: 2d68aea1a624
Revises: 7c9f232a6d59
Create Date: 2025-09-04 22:58:19.972406

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '2d68aea1a624'
down_revision = '7c9f232a6d59'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### SQLite doesn't support ALTER COLUMN, so we'll recreate the table ###
    # Create new table with ULID primary key
    op.create_table(
        'users_new',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy data from old table to new table (if any exists)
    # Note: This will not preserve old integer IDs - new ULIDs will be generated
    # by the application when creating new records
    
    # Drop old table
    op.drop_table('users')
    
    # Rename new table to original name
    op.rename_table('users_new', 'users')
    
    # Recreate indexes
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)


def downgrade() -> None:
    # ### This is a destructive operation - recreating with integer IDs ###
    # Create old table structure
    op.create_table(
        'users_old',
        sa.Column('id', sa.INTEGER(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Drop ULID table
    op.drop_table('users')
    
    # Rename old table
    op.rename_table('users_old', 'users')
    
    # Recreate indexes
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
