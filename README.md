
# TruLedgr API

A FastAPI-based ledger API with SQLModel/SQLAlchemy database support.

## Features

- **FastAPI** for modern, fast web API development
- **SQLModel** with SQLAlchemy for database operations
- **SQLite** for local development
- **PostgreSQL** support for production
- **Alembic** for database migrations
- **Comprehensive testing** with pytest
- **Code quality tools** (Black, isort, flake8, mypy)

## Setup

### Prerequisites

- Python 3.8+
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd TruLedgr-API
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e '.[dev]'
   ```

### Development Setup

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Run the development server:**
   ```bash
   uvicorn truledgr_api.main:app --reload
   ```

3. **Access the API:**
   - API: http://127.0.0.1:8000
   - Interactive docs: http://127.0.0.1:8000/docs
   - Alternative docs: http://127.0.0.1:8000/redoc

## Database Configuration

### Local Development (SQLite)

The default configuration uses SQLite for local development:

```env
DATABASE_DRIVER=sqlite
SQLITE_FILE_NAME=truledgr_dev.db
```

### Production (PostgreSQL)

For production, configure PostgreSQL:

```env
DATABASE_DRIVER=postgresql
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=truledgr
DATABASE_USER=truledgr
DATABASE_PASSWORD=your_password_here
```

Or use a complete database URL:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/truledgr
```

### Database Migrations

We use Alembic for database migrations:

1. **Create a migration:**
   ```bash
   alembic revision --autogenerate -m "Your migration message"
   ```

2. **Apply migrations:**
   ```bash
   alembic upgrade head
   ```

3. **Downgrade migrations:**
   ```bash
   alembic downgrade -1
   ```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=truledgr_api --cov-report=html

# Run specific test file
pytest tests/test_users.py
```

## Code Quality

### Formatting and Linting

```bash
# Format code
black truledgr_api tests

# Sort imports
isort truledgr_api tests

# Lint code
flake8 truledgr_api tests

# Type checking
mypy truledgr_api

# Run all quality checks
black truledgr_api tests && isort truledgr_api tests && flake8 truledgr_api tests && mypy truledgr_api
```

### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:

```bash
pre-commit install
```

## API Endpoints

### Health Check

- `GET /health/` - Health check endpoint

### Users

- `POST /users/` - Create a new user
- `GET /users/` - List all users
- `GET /users/{user_id}` - Get user by ID
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user

## VS Code Tasks

The project includes VS Code tasks for common operations:

- **Setup: Install Dependencies** - Install project dependencies
- **FastAPI: Run Server** - Start the development server
- **Test: Run All Tests** - Run the test suite
- **Test: Run Tests with Coverage** - Run tests with coverage report
- **Lint: Format Code (Black)** - Format code with Black
- **Lint: Check Imports (isort)** - Check import sorting
- **Lint: Type Check (MyPy)** - Run type checking
- **Lint: Run All Linting** - Run all linting tools
- **Database: Create Migration** - Create a new migration
- **Database: Migrate** - Apply migrations
- **Database: Downgrade** - Downgrade migrations

## Project Structure

```
truledgr_api/
├── __init__.py
├── main.py              # FastAPI application
├── config.py            # Configuration settings
├── database.py          # Database setup and sessions
├── auth/                # Authentication modules
│   └── __init__.py
├── models/              # SQLModel database models
│   ├── __init__.py
│   └── user.py
└── routers/             # API route handlers
    ├── health.py
    └── users.py

tests/                   # Test files
├── test_health.py
├── test_server.py
├── test_users.py
└── test_database.py

alembic/                 # Database migration files
├── versions/
├── env.py
└── script.py.mako

.vscode/                 # VS Code configuration
├── tasks.json
├── launch.json
└── settings.json
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite and linting
6. Submit a pull request

## License

MIT
