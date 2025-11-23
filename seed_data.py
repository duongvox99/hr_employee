"""
Script to seed the database with sample data for testing.
"""

import asyncio

from sqlalchemy import delete

from app.auth import create_access_token
from app.database import AsyncSessionLocal, Base, engine
from app.models import (
    Company,
    Department,
    Employee,
    EmployeeStatus,
    Location,
    Organization,
    Position,
    User,
)


async def seed_data():
    """Seed database with sample organizations and employees."""
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        try:
            # Clear existing data
            await db.execute(delete(Employee))
            await db.execute(delete(Department))
            await db.execute(delete(Company))
            await db.execute(delete(Location))
            await db.execute(delete(Position))
            await db.execute(delete(User))
            await db.execute(delete(Organization))
            await db.commit()

            # Create organizations with display column configurations
            org1 = Organization(
                id=1,
                name="Tech Corp",
                display_columns=[
                    "avatar",
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "department",
                    "position",
                    "location",
                    "status",
                ],
            )
            org2 = Organization(
                id=2,
                name="Finance Inc",
                display_columns=["department", "location", "position", "status"],  # No contact info
            )

            db.add(org1)
            db.add(org2)
            await db.commit()

            # Create users for each organization
            user1 = User(
                id=1,
                organization_id=1,
                email="admin@techcorp.com",
                hashed_password="hashed_password_here",  # In production, use proper password hashing
                full_name="Admin User",
                is_active=1,
            )
            user2 = User(
                id=2,
                organization_id=2,
                email="admin@financeinc.com",
                hashed_password="hashed_password_here",
                full_name="Finance Admin",
                is_active=1,
            )

            db.add(user1)
            db.add(user2)
            await db.commit()

            # Create a company
            company1 = Company(
                id=1,
                name="Apple",
            )
            db.add(company1)
            await db.commit()

            # Create departments
            departments_org1 = [
                Department(id=1, name="Engineering"),
                Department(id=2, name="Product"),
                Department(id=3, name="Design"),
                Department(id=4, name="Sales"),
                Department(id=5, name="Marketing"),
            ]

            departments_org2 = [
                Department(id=6, name="Finance"),
                Department(id=7, name="Accounting"),
            ]

            db.add_all(departments_org1 + departments_org2)
            await db.commit()

            # Create locations
            locations_org1 = [
                Location(id=1, name="New York"),
                Location(id=2, name="San Francisco"),
                Location(id=3, name="Austin"),
                Location(id=4, name="Boston"),
            ]

            locations_org2 = [
                Location(id=5, name="Chicago"),
                Location(id=6, name="New York"),
            ]

            db.add_all(locations_org1 + locations_org2)
            await db.commit()

            # Create positions
            positions_org1 = [
                Position(id=1, name="Senior Software Engineer"),
                Position(id=2, name="Staff Software Engineer"),
                Position(id=3, name="Product Manager"),
                Position(id=4, name="Engineering Manager"),
                Position(id=5, name="Senior Designer"),
                Position(id=6, name="Software Engineer"),
                Position(id=7, name="Sales Manager"),
                Position(id=8, name="Marketing Director"),
            ]

            positions_org2 = [
                Position(id=9, name="Financial Analyst"),
                Position(id=10, name="Senior Accountant"),
                Position(id=11, name="Investment Banker"),
            ]

            db.add_all(positions_org1 + positions_org2)
            await db.commit()

            # Create employees for Org 1 (Tech Corp)
            employees_org1 = [
                Employee(
                    id=1,
                    organization_id=1,
                    first_name="John",
                    last_name="Doe",
                    email="john.doe@techcorp.com",
                    phone="+1-555-0101",
                    avatar="https://i.pravatar.cc/150?img=1",
                    department_id=1,  # Engineering
                    location_id=1,  # New York
                    position_id=1,  # Senior Software Engineer
                    company_id=1,  # Apple
                    status=EmployeeStatus.ACTIVE.value,
                ),
                Employee(
                    id=2,
                    organization_id=1,
                    first_name="Jane",
                    last_name="Smith",
                    email="jane.smith@techcorp.com",
                    phone="+1-555-0102",
                    avatar="https://i.pravatar.cc/150?img=5",
                    department_id=1,  # Engineering
                    location_id=2,  # San Francisco
                    position_id=2,  # Staff Software Engineer
                    company_id=1,  # Apple
                    status=EmployeeStatus.ACTIVE.value,
                ),
                Employee(
                    id=3,
                    organization_id=1,
                    first_name="Bob",
                    last_name="Johnson",
                    email="bob.johnson@techcorp.com",
                    phone="+1-555-0103",
                    avatar="https://i.pravatar.cc/150?img=12",
                    department_id=2,  # Product
                    location_id=1,  # New York
                    position_id=3,  # Product Manager
                    company_id=1,  # Apple
                    status=EmployeeStatus.ACTIVE.value,
                ),
                Employee(
                    id=4,
                    organization_id=1,
                    first_name="Alice",
                    last_name="Williams",
                    email="alice.williams@techcorp.com",
                    phone="+1-555-0104",
                    avatar="https://i.pravatar.cc/150?img=9",
                    department_id=1,  # Engineering
                    location_id=3,  # Austin
                    position_id=4,  # Engineering Manager
                    company_id=1,  # Apple
                    status=EmployeeStatus.ACTIVE.value,
                ),
                Employee(
                    id=5,
                    organization_id=1,
                    first_name="Charlie",
                    last_name="Brown",
                    email="charlie.brown@techcorp.com",
                    phone="+1-555-0105",
                    avatar="https://i.pravatar.cc/150?img=13",
                    department_id=3,  # Design
                    location_id=2,  # San Francisco
                    position_id=5,  # Senior Designer
                    company_id=1,  # Apple
                    status=EmployeeStatus.ACTIVE.value,
                ),
                Employee(
                    id=6,
                    organization_id=1,
                    first_name="Diana",
                    last_name="Martinez",
                    email="diana.martinez@techcorp.com",
                    phone="+1-555-0106",
                    avatar="https://i.pravatar.cc/150?img=21",
                    department_id=1,  # Engineering
                    location_id=1,  # New York
                    position_id=6,  # Software Engineer
                    company_id=1,  # Apple
                    status=EmployeeStatus.NOT_STARTED.value,
                ),
                Employee(
                    id=7,
                    organization_id=1,
                    first_name="Ethan",
                    last_name="Davis",
                    email="ethan.davis@techcorp.com",
                    phone="+1-555-0107",
                    avatar="https://i.pravatar.cc/150?img=14",
                    department_id=4,  # Sales
                    location_id=4,  # Boston
                    position_id=7,  # Sales Manager
                    company_id=1,  # Apple
                    status=EmployeeStatus.ACTIVE.value,
                ),
                Employee(
                    id=8,
                    organization_id=1,
                    first_name="Fiona",
                    last_name="Garcia",
                    email="fiona.garcia@techcorp.com",
                    phone="+1-555-0108",
                    avatar="https://i.pravatar.cc/150?img=24",
                    department_id=5,  # Marketing
                    location_id=3,  # Austin
                    position_id=8,  # Marketing Director
                    company_id=1,  # Apple
                    status=EmployeeStatus.TERMINATED.value,
                ),
            ]

            # Create employees for Org 2 (Finance Inc)
            employees_org2 = [
                Employee(
                    id=9,
                    organization_id=2,
                    first_name="Michael",
                    last_name="Lee",
                    email="michael.lee@financeinc.com",
                    phone="+1-555-0201",
                    avatar="https://i.pravatar.cc/150?img=33",
                    department_id=6,  # Finance
                    location_id=5,  # Chicago
                    position_id=9,  # Financial Analyst
                    company_id=1,  # Apple
                    status=EmployeeStatus.ACTIVE.value,
                ),
                Employee(
                    id=10,
                    organization_id=2,
                    first_name="Sarah",
                    last_name="Taylor",
                    email="sarah.taylor@financeinc.com",
                    phone="+1-555-0202",
                    avatar="https://i.pravatar.cc/150?img=30",
                    department_id=7,  # Accounting
                    location_id=5,  # Chicago
                    position_id=10,  # Senior Accountant
                    company_id=1,  # Apple
                    status=EmployeeStatus.ACTIVE.value,
                ),
                Employee(
                    id=11,
                    organization_id=2,
                    first_name="David",
                    last_name="Anderson",
                    email="david.anderson@financeinc.com",
                    phone="+1-555-0203",
                    avatar="https://i.pravatar.cc/150?img=51",
                    department_id=6,  # Finance
                    location_id=6,  # New York
                    position_id=11,  # Investment Banker
                    company_id=1,  # Apple
                    status=EmployeeStatus.ACTIVE.value,
                ),
            ]

            db.add_all(employees_org1 + employees_org2)
            await db.commit()

            print("Database seeded successfully!")
            print(f"Created {len(employees_org1)} employees for Tech Corp (Org 1)")
            print(f"Created {len(employees_org2)} employees for Finance Inc (Org 2)")
            print(
                "\nOrganization 1 (Tech Corp) displays: name, email, phone, department, location, position, status, avatar"
            )
            print(
                "Organization 2 (Finance Inc) displays: department, location, position, status (no contact info)"
            )
            print("\n=== Authentication Tokens ===")
            print(f"Org 1 User Token: {create_access_token(1)}")
            print(f"Org 2 User Token: {create_access_token(2)}")
            print("\nUse these tokens in the Authorization header:")
            print("Authorization: Bearer <token>")

        except Exception as e:
            print(f"Error seeding database: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_data())
