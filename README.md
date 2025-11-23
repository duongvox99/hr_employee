# HR Employee API

A FastAPI microservice for employee management.

## Features

- **Hybrid Pagination** (use both cursor-based & offset-based) for better performance but still can work with page numbers
- **Rate Limit** - Prevent abuse with configurable rate limits using sliding window algorithm
- **Clean Architecture** - Separated into Router, Service, and Repository layers
- **Comprehensive Tests** - Unit and integration tests included
- **Type Safety** - Using Pydantic for data validation
- **Code Quality Tools** - Ruff, and Pre-commit hooks
- **Docker Support** - Multi-stage builds for optimized images with dev/prod configurations

## Tech Stack

- **Python 3.12**
- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Docker** - Containerization with multi-stage builds
- **uv** - Fast Python package manager
- **Pytest** - Testing framework
- **Ruff** - Fast Python linter and formatter
- **Pre-commit** - Git hooks for code quality
- **SQLite** - Database (for development/testing)

## Project Structure

```
hr_employee/
├── app/
│   ├── decorators/          # Decorators
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── repositories/        # Data access layer
│   ├── services/            # Business logic layer
│   ├── routers/             # API endpoints
│   ├── utils/               # Utility functions
│   └── main.py              # FastAPI application
├── tests/
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── alembic/versions         # Database migrations files
├── Dockerfile               # Multi-stage Docker build
├── docker-compose.dev.yml   # Development configuration
├── docker-compose.prod.yml  # Production configuration
├── .dockerignore            # Docker ignore patterns
├── .env                     # Environment variables
└── seed_data.py             # Script to populate test data
```

## Prepare the database (first time only):

```bash
# Install uv and dependencies locally to seed data
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Init .env file following sample file
cp .env.example .env

# Run migrations
alembic upgrade head

# Seed database with sample data
python seed_data.py
```

You will see a `hr_employees.db` SQLite file created in the project root.
You can use the token after running script for testing API.

## Installation

You can run this application either using **Docker** (recommended) or **local installation**.

### Option 1: Using Docker (Recommended)

Docker provides a consistent environment and is the easiest way to get started.

#### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

#### **Run in Development Mode** (with hot-reloading):

```bash
# Start the container
docker compose -f docker-compose.dev.yml up

# Or run in background
docker compose -f docker-compose.dev.yml up -d

# View logs
docker compose -f docker-compose.dev.yml logs -f

# Stop
docker compose -f docker-compose.dev.yml down
```

#### **Run in Production Mode**:
```bash
# Start the container
docker compose -f docker-compose.prod.yml up -d

# View logs
docker compose -f docker-compose.prod.yml logs -f

# Stop
docker compose -f docker-compose.prod.yml down
```

#### Development vs Production

| Feature | Development | Production |
|---------|-------------|------------|
| **Hot-reload** | ✅ Yes | ❌ No |
| **Code changes** | Instant (no rebuild) | Requires rebuild |
| **Container name** | `hr_employee_api_dev` | `hr_employee_api_prod` |
| **Use case** | Local development | Deployment |

#### Useful Docker Commands

```bash
# Rebuild after dependency changes
docker compose -f docker-compose.dev.yml up --build

# Execute commands inside container
docker compose -f docker-compose.dev.yml exec api bash
docker compose -f docker-compose.dev.yml exec api python seed_data.py

# View container status
docker ps

# Clean up
docker compose -f docker-compose.dev.yml down -v
```

### Option 2: Local Installation (Using uv)

#### Quickstart
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"
```

#### Configuration

The application uses environment variables for configuration. Create a `.env` file following `.env.example`:

```env
DATABASE_URL=sqlite+aiosqlite:///./hr_employees.db
ENVIRONMENT=development
```

#### Run the application
```bash
# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Application Access
The API will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

## Sample requests
### Get Employees with Search and Pagination
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/api/v1/employees?search=john&limit=2&page=1' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJ1c2VyX2lkIjogMX0='
```

## Set up pre-commit hooks

```bash
pre-commit install
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_employee_repository.py

# Run integration tests only
pytest tests/integration/
```

## Code Quality

```bash
# Format code with ruff
ruff format .

# Lint code
ruff check .

# Fix lint issues automatically
ruff check --fix .
```

## License

MIT
