import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app
from app.models import Employee, Organization

# Create test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_hr_employees.db"
test_engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
AsyncTestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Create all tables once at the start of the test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Drop all tables once at the end of the test session
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Provide a database session and clean up data after each test."""
    async with AsyncTestSessionLocal() as session:
        yield session

    # Clean up all data after each test to maintain isolation
    # Use begin() to ensure the deletes are committed
    async with test_engine.begin() as conn:
        # Delete in reverse order of dependencies to avoid foreign key issues
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
        # Transaction is automatically committed when exiting the context


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Create a test client with dependency override."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as async_client:
        yield async_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_organizations(db_session):
    """Create sample organizations."""
    org1 = Organization(
        id=1,
        name="Test Corp",
        display_columns=["first_name", "last_name", "email", "department", "location", "position"],
    )
    org2 = Organization(id=2, name="Another Corp", display_columns=["department", "location"])

    db_session.add(org1)
    db_session.add(org2)
    await db_session.commit()

    return [org1, org2]


@pytest_asyncio.fixture
async def sample_users(db_session, sample_organizations):
    """Create sample users for testing."""
    from app.models.user import User

    users = [
        User(
            id=1,
            organization_id=1,
            email="user1@test.com",
            hashed_password="hashed_password_1",
            full_name="Test User 1",
            is_active=1,
        ),
        User(
            id=2,
            organization_id=1,
            email="user2@test.com",
            hashed_password="hashed_password_2",
            full_name="Test User 2",
            is_active=1,
        ),
        User(
            id=3,
            organization_id=2,
            email="user3@test.com",
            hashed_password="hashed_password_3",
            full_name="Test User 3",
            is_active=1,
        ),
    ]

    db_session.add_all(users)
    await db_session.commit()

    return users


@pytest_asyncio.fixture
async def sample_employees(db_session, sample_organizations):
    """Create sample employees."""
    from app.models import Company, Department, Location, Position

    # Create companies, departments, locations, and positions first
    com1 = Company(id=1, name="Apple Inc.")

    dept1 = Department(id=1, name="Engineering")
    dept2 = Department(id=2, name="Sales")
    dept3 = Department(id=3, name="Marketing")

    loc1 = Location(id=1, name="New York")
    loc2 = Location(id=2, name="San Francisco")
    loc3 = Location(id=3, name="Boston")

    pos1 = Position(id=1, name="Software Engineer")
    pos2 = Position(id=2, name="Senior Engineer")
    pos3 = Position(id=3, name="Sales Manager")
    pos4 = Position(id=4, name="Marketing Manager")

    db_session.add_all([com1, dept1, dept2, dept3, loc1, loc2, loc3, pos1, pos2, pos3, pos4])
    await db_session.commit()

    # Now create employees with proper foreign keys
    employees = [
        Employee(
            id=1,
            organization_id=1,
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            phone="+1-555-0001",
            company_id=1,  # Apple Inc.
            department_id=1,  # Engineering
            location_id=1,  # New York
            position_id=1,  # Software Engineer
            status="Active",
        ),
        Employee(
            id=2,
            organization_id=1,
            first_name="Jane",
            last_name="Smith",
            email="jane@test.com",
            phone="+1-555-0002",
            department_id=1,  # Engineering
            location_id=2,  # San Francisco
            position_id=2,  # Senior Engineer
            status="Active",
        ),
        Employee(
            id=3,
            organization_id=1,
            first_name="Bob",
            last_name="Johnson",
            email="bob@test.com",
            phone="+1-555-0003",
            department_id=2,  # Sales
            location_id=1,  # New York
            position_id=3,  # Sales Manager
            status="Active",
        ),
        Employee(
            id=4,
            organization_id=2,
            first_name="Alice",
            last_name="Williams",
            email="alice@another.com",
            phone="+1-555-0004",
            department_id=3,  # Marketing
            location_id=3,  # Boston
            position_id=4,  # Marketing Manager
            status="Active",
        ),
    ]

    db_session.add_all(employees)
    await db_session.commit()

    return employees


@pytest.fixture(autouse=True)
def reset_rate_limiters():
    """Reset rate limiters before each test."""
    from app.decorators.rate_limit import reset_all_limiters

    reset_all_limiters()
    yield
    reset_all_limiters()
