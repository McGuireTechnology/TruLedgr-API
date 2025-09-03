
# TruLedgr API

TruLedgr API is a Python package providing a FastAPI-based server for your application. It is structured for easy deployment, testing, and extension.

## Workspace Setup for FastAPI Development

### 1. Install Python 3.9+
Make sure you have Python 3.9 or newer:
```sh
python3 --version
```

### 2. Set up a virtual environment (recommended)
```sh
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install in editable (dev) mode
```sh
pip install --upgrade pip
pip install -e ".[dev]"
```

### 4. Set up environment variables
If you use a `.env` file, create it in your project root:
```
APP_NAME=TruLedgr API
DEBUG=True
HOST=127.0.0.1
PORT=8000
```

### 5. Run the FastAPI app
```sh
uvicorn truledgr_api.main:app --reload
```
Visit http://127.0.0.1:8000/docs for the interactive API docs.

### 6. Run tests
```sh
pytest
```

### 7. (Recommended) Use code quality tools
Format code:
```sh
black .
```
Lint code:
```sh
ruff .
```
Type-check:
```sh
mypy truledgr_api
```

## Project Structure

- `truledgr_api/` — Main package (app code, routers, config, etc.)
- `tests/` — Test suite
- `pyproject.toml` — Project configuration and dependencies
- `Dockerfile` — For containerization
- `.env` — Environment variables (not committed)

## License
MIT
