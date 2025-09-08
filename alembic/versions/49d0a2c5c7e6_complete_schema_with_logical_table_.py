"""Complete schema with logical table ordering

Revision ID: 49d0a2c5c7e6
Revises: 1ff572a223ab
Create Date: 2025-09-05 16:03:36.141426

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel as sm
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '49d0a2c5c7e6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### Create enums first ###

    # Institution enums
    institution_type_enum = postgresql.ENUM('BANK', 'CREDIT_UNION', 'INVESTMENT_FIRM', 'INSURANCE', 'OTHER', name='institutiontype')
    institution_type_enum.create(op.get_bind(), checkfirst=True)

    institution_status_enum = postgresql.ENUM('ACTIVE', 'INACTIVE', 'SUSPENDED', name='institutionstatus')
    institution_status_enum.create(op.get_bind(), checkfirst=True)

    # Category enum
    category_type_enum = postgresql.ENUM('DEBIT', 'CREDIT', 'TRANSFER', 'PAYMENT', 'FEE', 'INTEREST', 'DIVIDEND', 'ADJUSTMENT', 'INCOME', 'OTHER', name='categorytype')
    category_type_enum.create(op.get_bind(), checkfirst=True)

    # Account enums
    account_type_enum = postgresql.ENUM('CHECKING', 'SAVINGS', 'CREDIT_CARD', 'INVESTMENT', 'LOAN', 'MORTGAGE', 'OTHER', name='accounttype')
    account_type_enum.create(op.get_bind(), checkfirst=True)

    account_status_enum = postgresql.ENUM('ACTIVE', 'INACTIVE', 'CLOSED', 'PENDING', name='accountstatus')
    account_status_enum.create(op.get_bind(), checkfirst=True)

    # Transaction enums
    transaction_status_enum = postgresql.ENUM('PENDING', 'CLEARED', 'RECONCILED', 'CANCELLED', name='transactionstatus')
    transaction_status_enum.create(op.get_bind(), checkfirst=True)

    transaction_category_enum = postgresql.ENUM('FOOD_AND_DRINK', 'TRANSPORTATION', 'SHOPPING', 'ENTERTAINMENT', 'BILLS_AND_UTILITIES', 'HEALTHCARE', 'EDUCATION', 'TRAVEL', 'PERSONAL_CARE', 'HOME_IMPROVEMENT', 'GIFTS_AND_DONATIONS', 'INVESTMENTS', 'INCOME', 'TRANSFER', 'OTHER', name='transactioncategory')
    transaction_category_enum.create(op.get_bind(), checkfirst=True)

    # Auth enums
    session_status_enum = postgresql.ENUM('ACTIVE', 'EXPIRED', 'REVOKED', name='sessionstatus')
    session_status_enum.create(op.get_bind(), checkfirst=True)

    oauth_provider_enum = postgresql.ENUM('GOOGLE', 'GITHUB', 'MICROSOFT', 'APPLE', name='oauthprovider')
    oauth_provider_enum.create(op.get_bind(), checkfirst=True)

    # ### 1. Users table (foundation) ###
    op.create_table('users',
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
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # ### 2. Institutions table (references users) ###
    op.create_table('institutions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('institution_type', institution_type_enum, nullable=False),
        sa.Column('status', institution_status_enum, nullable=False),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('zip_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=2), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_institutions_user_id'), 'institutions', ['user_id'])

    # ### 3. Categories table (references users, self-referencing) ###
    op.create_table('categories',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category_type', category_type_enum, nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('parent_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_user_id'), 'categories', ['user_id'])
    op.create_index(op.f('ix_categories_parent_id'), 'categories', ['parent_id'])

    # ### 4. Payees table (references users) ###
    op.create_table('payees',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('is_account_payee', sa.Boolean(), nullable=False),
        sa.Column('account_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payees_user_id'), 'payees', ['user_id'])

    # ### 5. Accounts table (references users and institutions) ###
    op.create_table('accounts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('institution_id', sa.String(), nullable=True),
        sa.Column('account_type', account_type_enum, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('account_number', sa.String(length=100), nullable=True),
        sa.Column('routing_number', sa.String(length=50), nullable=True),
        sa.Column('balance', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', account_status_enum, nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['institution_id'], ['institutions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_accounts_user_id'), 'accounts', ['user_id'])
    op.create_index(op.f('ix_accounts_institution_id'), 'accounts', ['institution_id'])

    # ### 6. Transactions table (references users, accounts, categories, payees) ###
    op.create_table('transactions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('account_id', sa.String(), nullable=False),
        sa.Column('category_id', sa.String(), nullable=False),
        sa.Column('payee_id', sa.String(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('category', transaction_category_enum, nullable=False),
        sa.Column('status', transaction_status_enum, nullable=False),
        sa.Column('transaction_date', sa.DateTime(), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id']),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.ForeignKeyConstraint(['payee_id'], ['payees.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'])
    op.create_index(op.f('ix_transactions_account_id'), 'transactions', ['account_id'])
    op.create_index(op.f('ix_transactions_category_id'), 'transactions', ['category_id'])
    op.create_index(op.f('ix_transactions_payee_id'), 'transactions', ['payee_id'])
    op.create_index(op.f('ix_transactions_reference_number'), 'transactions', ['reference_number'], unique=True)

    # ### 7. Auth tables (references users) ###

    # User sessions
    op.create_table('user_sessions',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('session_token', sa.String(), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=True),
        sa.Column('status', session_status_enum, nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('last_activity', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_sessions_session_token'), 'user_sessions', ['session_token'], unique=True)
    op.create_index(op.f('ix_user_sessions_refresh_token'), 'user_sessions', ['refresh_token'], unique=True)
    op.create_index(op.f('ix_user_sessions_user_id'), 'user_sessions', ['user_id'])

    # User OAuth accounts
    op.create_table('user_oauth_accounts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('provider', oauth_provider_enum, nullable=False),
        sa.Column('provider_user_id', sa.String(), nullable=False),
        sa.Column('provider_email', sa.String(), nullable=True),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('account_data', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_oauth_accounts_user_id'), 'user_oauth_accounts', ['user_id'])


def downgrade() -> None:
    # ### Drop tables in reverse order ###

    # Auth tables
    op.drop_index(op.f('ix_user_oauth_accounts_user_id'), table_name='user_oauth_accounts')
    op.drop_table('user_oauth_accounts')

    op.drop_index(op.f('ix_user_sessions_user_id'), table_name='user_sessions')
    op.drop_index(op.f('ix_user_sessions_refresh_token'), table_name='user_sessions')
    op.drop_index(op.f('ix_user_sessions_session_token'), table_name='user_sessions')
    op.drop_table('user_sessions')

    # Transactions
    op.drop_index(op.f('ix_transactions_reference_number'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_payee_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_category_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_account_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_user_id'), table_name='transactions')
    op.drop_table('transactions')

    # Accounts
    op.drop_index(op.f('ix_accounts_institution_id'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_user_id'), table_name='accounts')
    op.drop_table('accounts')

    # Payees
    op.drop_index(op.f('ix_payees_user_id'), table_name='payees')
    op.drop_table('payees')

    # Categories
    op.drop_index(op.f('ix_categories_parent_id'), table_name='categories')
    op.drop_index(op.f('ix_categories_user_id'), table_name='categories')
    op.drop_table('categories')

    # Institutions
    op.drop_index(op.f('ix_institutions_user_id'), table_name='institutions')
    op.drop_table('institutions')

    # Users
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    # ### Drop enums in reverse order ###
    op.execute("DROP TYPE IF EXISTS oauthprovider")
    op.execute("DROP TYPE IF EXISTS sessionstatus")
    op.execute("DROP TYPE IF EXISTS transactioncategory")
    op.execute("DROP TYPE IF EXISTS transactionstatus")
    op.execute("DROP TYPE IF EXISTS accountstatus")
    op.execute("DROP TYPE IF EXISTS accounttype")
    op.execute("DROP TYPE IF EXISTS categorytype")
    op.execute("DROP TYPE IF EXISTS institutionstatus")
    op.execute("DROP TYPE IF EXISTS institutiontype")
