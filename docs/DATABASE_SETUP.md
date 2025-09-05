# Database Setup

This project uses SQLModel/SQLAlchemy for database operations, supporting multiple database backends through a single `DATABASE_URL` configuration.

## Configuration

### Required Environment Variable

The application requires a single environment variable:

```bash
DATABASE_URL=<your_database_connection_string>
```

If `DATABASE_URL` is not set, the application will throw a clear error message with examples.

### Database URL Examples

#### SQLite (Local Development)
```bash
DATABASE_URL=sqlite:///./truledgr.db
```

#### PostgreSQL (Production)
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/truledgr
```

#### MySQL (Alternative)
```bash
DATABASE_URL=mysql://username:password@localhost:3306/truledgr
```

## Setup Instructions

### Local Development (SQLite)

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. The `.env` file already contains a SQLite configuration:
   ```bash
   DATABASE_URL=sqlite:///./truledgr.db
   ```

3. Install dependencies:
   ```bash
   pip install -e '.[dev]'
   ```

4. Run migrations (if using Alembic):
   ```bash
   alembic upgrade head
   ```

5. Start the development server:
   ```bash
   uvicorn truledgr_api.main:app --reload
   ```

### Production (PostgreSQL)

1. Set up your PostgreSQL database and user.

2. Update your production environment with:
   ```bash
   DATABASE_URL=postgresql://username:password@host:port/database_name
   ```

3. Install production dependencies:
   ```bash
   pip install -e '.[production]'
   ```

4. Run migrations:
   ```bash
   alembic upgrade head
   ```

## Database Features

- **Async Support**: Automatically converts database URLs to async versions for SQLAlchemy async operations
- **SQLite**: Uses `sqlite+aiosqlite://` for async operations
- **PostgreSQL**: Uses `postgresql+asyncpg://` for async operations
- **Other Databases**: Returns the original URL (may require manual async driver setup)

## Testing

The test suite includes comprehensive database configuration tests:

```bash
pytest tests/test_database.py -v
```

## Error Handling

If `DATABASE_URL` is not configured, you'll see this error:

```
DATABASE_URL is required. Please set it in your .env file.
Examples:
  For SQLite: DATABASE_URL=sqlite:///./truledgr.db
  For PostgreSQL: DATABASE_URL=postgresql://user:password@localhost:5432/truledgr
```

## Migration Management

This project uses Alembic for database migrations:

- Generate a new migration: `alembic revision --autogenerate -m "description"`
- Apply migrations: `alembic upgrade head`
- Downgrade: `alembic downgrade -1`

## Supported Databases

- SQLite (recommended for development)
- PostgreSQL (recommended for production)
- MySQL (community support)
- Any database supported by SQLAlchemy (with appropriate drivers)
